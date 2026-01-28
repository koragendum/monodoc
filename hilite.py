import re


WHITESPACE = re.compile(r'\s+')

WORD = re.compile("`?'?[_a-zA-Zα-ωΑ-Ω][_a-zA-Zα-ωΑ-Ω0-9-]*['!?]?")

NONUMERIC_WORD = re.compile("`?'?[_a-zA-Zα-ωΑ-Ω][_a-zA-Zα-ωΑ-Ω-]*['!?]?")

NUMERIC = re.compile(r'([+−-])?(\d+)(\.\d+)?')

SUFFIXED_NUMERIC = re.compile(r'([+−-])?(\d+)(\.\d+)?([_a-zA-Z][_a-zA-Z0-9]*)?')

HEXADECIMAL = re.compile(r"([+−-])?(0x)([0-9a-fA-F]+(?:['_][0-9a-fA-F]+)*)")

LEFT_DELIM  = {'(', '[', '⟨', '{'}
RIGHT_DELIM = {')', ']', '⟩', '}'}

DYAD = {
    '->', '<-', '=>', '<=',
    '||', '&&', '<<', '>>',
    '++', '--', '**', '//',
    '+=', '-=', '*=',
    '==', '!=', '/=',
    ':=', '::',
}

QUOTE1 = ('‘', '’')
QUOTE2 = ('“', '”')

COMMENT_CHAR = '※'
COMMENT_DYAD = None

HTML_ENTITY = re.compile(r'&(?:[a-zA-Z]+|#[0-9]+|#x[0-9a-fA-F]+);')

LEFT_OPERAND = ('word', 'rdelim', 'integer', 'fractional')

def _replace(text):
    return text.replace('<', '&lt;').replace('>', '&gt;')

def _escape(text):
    if '<' not in text:
        return text.replace('>', '&gt;')
    fragments = []
    length = len(text)
    final = length - 1
    offset = 0
    taken = 0
    while offset < length:
        start = text.find('<', offset)
        if start == -1:
            break
        if start > 0 and text[start-1] == '\\':
            end = text.find('>', start+1)
            if end > 0:
                fragments.append(_replace(text[taken:start-1]))
                fragments.append(text[start:end+1])
                offset = end + 1
                taken = end + 1
                continue

        elif start < final and text[start+1] == '/':
            end = text.find('>', start+2)
            if end > 0:
                fragments.append(_replace(text[taken:start]))
                fragments.append(text[start:end+1])
                offset = end + 1
                taken = end + 1
                continue

        offset = start + 1

    if taken < length:
        fragments.append(_replace(text[taken:]))

    return ''.join(fragments)

def lex(lines, quote1, quote2, comment_char, comment_dyad, mode='default'):
    left_quote1, right_quote1 = quote1
    left_quote2, right_quote2 = quote2
    text = '\n'.join(lines)
    length = len(text)
    final = length - 1
    tokens = []
    offset = 0
    while offset < length:
        match = WHITESPACE.match(text, offset)
        if match:
            tokens.append(('space', match.group(0)))
            offset = match.end()
            continue

        if mode == 'sepr-word-numeric' and tokens and tokens[-1][0] in ('integer', 'fractional'):
            match = NONUMERIC_WORD.match(text, offset)
        else:
            match = WORD.match(text, offset)
        if match:
            tokens.append(('word', match.group(0)))
            offset = match.end()
            continue

        match = HEXADECIMAL.match(text, offset)
        if match:
            sign, radix, integer = match.groups()
            if sign and tokens and tokens[-1][0] in LEFT_OPERAND:
                tokens.append(('symbol', sign))
                sign = ''
            elif sign is None:
                sign = ''
            tokens.append(('integer', sign + radix + integer))
            offset = match.end()
            continue

        if mode == 'join-numeric-word':
            match = SUFFIXED_NUMERIC.match(text, offset)
        else:
            match = NUMERIC.match(text, offset)
        if match:
            if mode == 'join-numeric-word':
                sign, integer, frac, suffix = match.groups()
                if suffix is None:
                    suffix = ''
            else:
                sign, integer, frac = match.groups()
                suffix = ''

            if sign and tokens and tokens[-1][0] in LEFT_OPERAND:
                tokens.append(('symbol', sign))
                sign = ''
            elif sign is None:
                sign = ''

            if frac:
                tokens.append(('fractional', sign + integer + frac + suffix))
            else:
                tokens.append(('integer', sign + integer + suffix))

            offset = match.end()
            continue

        char = text[offset]

        if char == '\\' and text[offset+1:offset+2] == '<':
            end = text.find('>', offset+2)
            if end > 0:
                tokens.append(('tag', text[offset+1:end+1]))
                offset = end + 1
                continue

        if char == '<' and text[offset+1:offset+2] == '/':
            end = text.find('>', offset+2)
            if end > 0:
                tokens.append(('tag', text[offset:end+1]))
                offset = end + 1
                continue

        if char in LEFT_DELIM:
            tokens.append(('ldelim', char))
            offset += 1
            continue

        if char in RIGHT_DELIM:
            tokens.append(('rdelim', char))
            offset += 1
            continue

        if char == left_quote1:
            end = text.find(right_quote1, offset+1)
            if end > 0:
                tokens.append(('quote1', text[offset:end+1]))
                offset = end + 1
                continue

        if char == left_quote2:
            end = text.find(right_quote2, offset+1)
            if end > 0:
                tokens.append(('quote2', text[offset:end+1]))
                offset = end + 1
                continue

        pair = text[offset:offset+2]

        if char == comment_char or pair == comment_dyad:
            end = text.find('\n', offset+1)
            if end > 0:
                tokens.append(('comment', text[offset:end]))
                offset = end
                continue

        match = HTML_ENTITY.match(text, offset)
        if match:
            tokens.append(('entity', match.group(0)))
            offset = match.end()
            continue

        if pair in DYAD:
            tokens.append(('symbol', pair))
            offset += 2
            continue

        tokens.append(('symbol', char))
        offset += 1

    return tokens


KEYWORD = {
    'define', 'def', 'fn', 'const', 'mutable', 'mut', 'public', 'pub',
    'raw', 'let', 'use', 'in', 'with', 'impl',
}

FLOW = {
    'end', 'return', 'if', 'then', 'else', 'unless',
    'break', 'loop', 'for', 'next', 'while', 'until',
    'from', 'to', 'case', 'match', 'when', 'otherwise'
}

FUNCTION = {'and', 'or', 'not', 'xor', 'mod', 'as'}

CONSTANT = {
    'NONE', 'None', 'none', 'NULL', 'null', 'nil',
    'True', 'true', 'False', 'false', 'TAU', 'tau',
    'UNKNOWN', 'unknown', 'UNDEFINED', 'undefined',
    'UNINIT', 'uninit', 'UNINITIALIZED', 'uninitialized'
}

GENERIC_TYPE = re.compile('[A-ZΑ-Ω][a-zA-Zα-ωΑ-Ω0-9]*')

NUMERIC_TYPE = re.compile('[uif][1-9][0-9]*')

OPERATOR = re.compile('[+−×/÷<>≤≥=≠~!*&|←→↑↓-]*')

SCOPE = '::'

ITALIC = re.compile('[a-zA-Z]')

DELIM_VARIANT = {
    '(': 0, ')': 0,
    '[': 1, ']': 1,
    '⟨': 2, '⟩': 2,
    '{': 3, '}': 3,
}

DELIM_NAME = {
    '(': 'paren',   ')': 'paren',
    '[': 'bracket', ']': 'bracket',
    '⟨': 'angle',   '⟩': 'angle',
    '{': 'brace',   '}': 'brace',
}

ELEM = 'hi-group'

def default_parser(tokens):
    length = len(tokens)
    output = []
    depth = 0
    var_depth = [0, 0, 0, 0]
    for index, (kind, text) in enumerate(tokens):
        match kind:
            case 'tag' | 'entity':
                output.append(text)

            case 'space':
                output.append(text)

            case 'word':
                italic = False
                if text.startswith('`'):
                    _class = "constant"
                    text = text[1:]
                elif text in KEYWORD:
                    _class = "keyword"
                elif text in FLOW:
                    _class = "flow"
                elif text in CONSTANT:
                    _class = "constant"
                elif text in FUNCTION:
                    _class = "function"
                elif NUMERIC_TYPE.fullmatch(text):
                    _class = "type"
                elif GENERIC_TYPE.fullmatch(text):
                    _class = "type"
                    if ITALIC.fullmatch(text): italic = True
                else:
                    if ITALIC.fullmatch(text): italic = True
                    if index+1 < length and tokens[index+1][1] in ('(', '⟨'):
                        _class = "function"
                    else:
                        _class = "identifier"
                # if italic:
                #     _class = f'{_class} i'
                text = text.replace('!', '<i>!</i>')
                output.append(f'<{ELEM} class="{_class}">{text}</{ELEM}>')

            case 'symbol':
                esc = _replace(text)
                if text == SCOPE:
                    output.append(f'<{ELEM} class="scope">{esc}</{ELEM}>')
                elif OPERATOR.fullmatch(text):
                    output.append(f'<{ELEM} class="operator">{esc}</{ELEM}>')
                else:
                    output.append(esc)

            case 'ldelim' | 'rdelim':
                var = DELIM_VARIANT[text]
                if kind == 'rdelim':
                    depth -= 1
                    var_depth[var] -= 1
                    output.append('</span>')
                output.append(
                    f'<{ELEM} class="delimiter {DELIM_NAME[text]}"'
                    # f' data-depth="{depth}"'
                    # f' data-{DELIM_NAME[text]}-depth="{var_depth[var]}">'
                    f' data-depth="{var_depth[var]}">'
                    f'{text}</{ELEM}>'
                )
                if kind == 'ldelim':
                    output.append(
                        f'<span class="region {DELIM_NAME[text]}-delimited"'
                        f' data-depth="{var_depth[var]}">'
                    )
                    depth += 1
                    var_depth[var] += 1

            case 'integer':
                text = text.replace('0x', '<span class="radix">0x</span>')
                output.append(f'<{ELEM} class="numeric">{text}</{ELEM}>')

            case 'fractional':
                output.append(f'<{ELEM} class="numeric">{text}</{ELEM}>')

            case 'quote1':
                esc = _escape(text)
                output.append(f'<{ELEM} class="character">{esc}</{ELEM}>')

            case 'quote2':
                esc = _escape(text)
                output.append(f'<{ELEM} class="quote">{esc}</{ELEM}>')

            case 'comment':
                esc = _escape(text)
                output.append(f'<{ELEM} class="comment">{esc}</{ELEM}>')

    return ''.join(output).splitlines()

ASM_INSTRUCTION = {
    'ret',
    'vaddps',
    'vbroadcastss',
    'vcmpltps',
    'vcvtps2dq',
    'vcvttps2udq',
    'vdivps',
    'vfmadd213ps',
    'vfnmadd231ps',
    'vmovups',
    'vmulps',
    'vrcp14ps',
    'vsubps',
    'vxorps',
    'vzeroupper',
}

ASM_REGISTER = {
    'al', 'ah', 'ax', 'eax', 'rax',
    'bl', 'bh', 'bx', 'ebx', 'rbx',
    'cl', 'ch', 'cx', 'ecx', 'rcx',
    'dl', 'dh', 'dx', 'edx', 'rdx',

    'sil', 'si', 'esi', 'rsi',
    'dil', 'di', 'edi', 'rdi',
    'spl', 'sp', 'esp', 'rsp',
    'bpl', 'bp', 'ebp', 'rbp',
           'ip', 'eip', 'rip',

    'r8b',  'r8w',  'r8d',  'r8',
    'r9b',  'r9w',  'r9d',  'r9',
    'r10b', 'r10w', 'r10d', 'r10',
    'r11b', 'r11w', 'r11d', 'r11',
    'r12b', 'r12w', 'r12d', 'r12',
    'r13b', 'r13w', 'r13d', 'r13',
    'r14b', 'r14w', 'r14d', 'r14',
    'r15b', 'r15w', 'r15d', 'r15',

    'xmm0', 'xmm1', 'xmm2', 'xmm3',
    'xmm4', 'xmm5', 'xmm6', 'xmm7',
    'ymm0', 'ymm1', 'ymm2', 'ymm3',
    'ymm4', 'ymm5', 'ymm6', 'ymm7',
    'zmm0', 'zmm1', 'zmm2', 'zmm3',
    'zmm4', 'zmm5', 'zmm6', 'zmm7',

    'k0', 'k1', 'k2', 'k3',
}

ASM_KEYWORD = {
    'ptr', 'byte', 'word', 'dword', 'qword', 'xmmword', 'ymmword', 'zmmword',
}

ASM_DIRECTIVE = {
    'long',
}

ASM_OPERATOR = re.compile('[+−×/<>=~!*&|-]*')

def assembly_parser(tokens):
    length = len(tokens)
    output = []
    depth = 0
    var_depth = [0, 0, 0, 0]
    index = 0
    while index < length:
        kind, text = tokens[index]
        match kind:
            case 'tag' | 'entity':
                output.append(text)

            case 'space':
                output.append(text)

            case 'word':
                if index+1 < length and tokens[index+1][1] == ':':
                    index += 1
                    text = text + ':'
                    _class = 'flow'
                elif text in ASM_KEYWORD:
                    _class = 'keyword'
                elif text in ASM_INSTRUCTION:
                    _class = 'function'
                elif text in ASM_REGISTER:
                    _class = 'identifier'
                else:
                    _class = None

                if _class is None:
                    output.append(text)
                else:
                    output.append(f'<{ELEM} class="{_class}">{text}</{ELEM}>')

            case 'symbol':
                if text == '.' and index+1 < length and tokens[index+1][0] == 'word':
                    index += 1
                    word = tokens[index][1]
                    text = '.' + word
                    if index+1 < length and tokens[index+1][1] == ':':
                        index += 1
                        text = text + ':'
                        _class = 'flow'
                    elif word in ASM_DIRECTIVE:
                        _class = 'keyword'
                    else:
                        _class = 'flow'
                    output.append(f'<{ELEM} class="{_class}">{text}</{ELEM}>')

                elif ASM_OPERATOR.fullmatch(text):
                    esc = _replace(text)
                    output.append(f'<{ELEM} class="operator">{esc}</{ELEM}>')

                else:
                    esc = _replace(text)
                    output.append(esc)

            case 'ldelim' | 'rdelim':
                var = DELIM_VARIANT[text]
                if kind == 'rdelim':
                    depth -= 1
                    var_depth[var] -= 1
                    output.append('</span>')
                output.append(
                    f'<{ELEM} class="delimiter {DELIM_NAME[text]}"'
                    f' data-depth="{var_depth[var]}">'
                    f'{text}</{ELEM}>'
                )
                if kind == 'ldelim':
                    output.append(
                        f'<span class="region {DELIM_NAME[text]}-delimited"'
                        f' data-depth="{var_depth[var]}">'
                    )
                    depth += 1
                    var_depth[var] += 1

            case 'integer':
                text = text.replace('0x', '<span class="radix">0x</span>')
                output.append(f'<{ELEM} class="numeric">{text}</{ELEM}>')

            case 'fractional':
                output.append(f'<{ELEM} class="numeric">{text}</{ELEM}>')

            case 'quote1':
                esc = _escape(text)
                output.append(f'<{ELEM} class="character">{esc}</{ELEM}>')

            case 'quote2':
                esc = _escape(text)
                output.append(f'<{ELEM} class="quote">{esc}</{ELEM}>')

            case 'comment':
                esc = _escape(text)
                output.append(f'<{ELEM} class="comment">{esc}</{ELEM}>')

        index += 1

    return ''.join(output).splitlines()


def default_handler(lang, lines, modifiers=None):
    # The less-than character “<” is escaped as “&lt;”
    #   unless it is preceded by “\” or followed by “/”.
    match lang:
        case 'rs' | 'rust':
            comment_char = None
            comment_dyad = '//'
        case 'rb' | 'ruby' | 'py' | 'python':
            comment_char = '#'
            comment_dyad = None
        case 'asm' | 'assembly':
            comment_char = ';'
            comment_dyad = None
        case _:
            comment_char = COMMENT_CHAR
            comment_dyad = COMMENT_DYAD

    match lang:
        case 'rs' | 'rust' | 'rb' | 'ruby' | 'py' | 'python' | 'asm' | 'assembly':
            quote1 = ("'", "'")
            quote2 = ('"', '"')
        case _:
            quote1 = QUOTE1
            quote2 = QUOTE2

    match lang:
        case 'rs' | 'rust':
            mode = 'join-numeric-word'
        case 'asm' | 'assembly':
            mode = 'sepr-word-numeric'
        case _:
            mode = 'default'

    tokens = lex(lines, quote1, quote2, comment_char, comment_dyad, mode)

    match lang:
        case 'asm' | 'assembly':
            return assembly_parser(tokens)
        case _:
            return default_parser(tokens)
