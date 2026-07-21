import re


WHITESPACE = re.compile(r'\s+')

WORD = re.compile("[`']?[_a-zA-Zα-ωΑ-Ω][_a-zA-Zα-ωΑ-Ω0-9-]*['!?]?")

NONUMERIC_WORD = re.compile("[`']?[_a-zA-Zα-ωΑ-Ω][_a-zA-Zα-ωΑ-Ω-]*['!?]?")

NUMERIC = re.compile(r'([+−-])?(\d+)(\.\d+)?')

SUFFIXED_NUMERIC = re.compile(r'([+−-])?(\d+)(\.\d+)?([_a-zA-Z][_a-zA-Z0-9]*)?')

HEXADECIMAL = re.compile(r"([+−-])?(0x)([0-9a-fA-F]+(?:['_][0-9a-fA-F]+)*)")

LEFT_DELIM  = {'(', '[', '⟨', '{'}
RIGHT_DELIM = {')', ']', '⟩', '}'}

DYAD = {
    '->', '<-', '=>', '<=',
    '||', '&&', '<<', '>>',
    '++', '--', '**', '//',
    '+=', '-=', '*=', '/=',
    '==', '!=',
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

def default_lexer(lines, quote1, quote2, comment1, comment2, delim_comment, mode='default'):
    left_quote1, right_quote1  = quote1
    left_quote2, right_quote2  = quote2

    multiline_comments = bool(delim_comment)
    if multiline_comments:
        left_comment, right_comment = delim_comment

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
        pair = text[offset:offset+2]

        if pair == '\\<':
            end = text.find('>', offset+2)
            if end > 0:
                tokens.append(('tag', text[offset+1:end+1]))
                offset = end + 1
                continue

        if pair == '</':
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

        if char == comment1 or pair == comment2:
            end = text.find('\n', offset+1)
            if end == -1:
                end = len(text)
            tokens.append(('comment', text[offset:end]))
            offset = end
            continue

        if multiline_comments:
            if char == left_comment or pair == left_comment:
                end = text.find(right_comment, offset + len(left_comment))
                if end > 0:
                    end += len(right_comment)
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
    'define', 'def', 'fn', 'proc', 'lambda', 'Λ', 'λ',
    'let', 'in', 'use', 'with',
    'const', 'mutable', 'mut',
    'public', 'pub', 'raw', 'unsafe',
    'type', 'trait', 'impl', 'struct', 'enum'
}

FLOW = {
    'end', 'return', 'if', 'then', 'else', 'unless',
    'yield', 'break', 'loop', 'for', 'next', 'while', 'until',
    'from', 'to', 'case', 'match', 'when', 'otherwise'
}

FUNCTION = {'and', 'or', 'not', 'xor', 'mod', 'as', 'exists', 'forall'}

CONSTANT = {
    'Some',
    'NONE', 'None', 'none',
    'NULL', 'null', 'nil',
    'True', 'true', 'False', 'false', 'TAU', 'tau',
    'UNKNOWN', 'unknown', 'UNDEFINED', 'undefined',
    'UNINIT', 'uninit', 'UNINITIALIZED', 'uninitialized',
#   'self', 'Self', 'unit', 'Unit'
}

GENERIC_TYPE = re.compile('[A-Z][a-zA-Z0-9]*')

NUMERIC_TYPE = re.compile('[uif][1-9][0-9]*')

WORD_OPERATOR = {
    'Σ', 'Π'
}

OPERATOR = re.compile('[+−×/÷<>≤≥=≠~!*&|←→↑↓∀∃-]*')

SCOPE = '::'

ITALIC = re.compile('[a-zA-Z]')

DELIM_VARIANT = {
    '(': 0, ')': 0,
    '[': 1, ']': 1,
    '⟨': 2, '⟩': 2,
    '{': 3, '}': 3,
    '⟦': 4, '⟧': 4,
    '⟪': 5, '⟫': 5,
}

DELIM_NAME = {
    '(': 'paren',    ')': 'paren',
    '[': 'bracket',  ']': 'bracket',
    '⟨': 'angle',    '⟩': 'angle',
    '{': 'brace',    '}': 'brace',
    '⟦': 'bracket2', '⟧': 'bracket2',
    '⟪': 'angle2',   '⟫': 'angle2',
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
                following = tokens[index+1] if index+1 < length else ('eof', '')
                if text.startswith('`'):
                    _class = "constant"
                    text = text[1:]
                elif text == 'TODO':
                    _class = "to-do"
                elif text in KEYWORD:
                    _class = "keyword"
                elif text in FLOW and following[0] != 'symbol':
                    _class = "flow"
                elif text in CONSTANT:
                    _class = "constant"
                elif text in FUNCTION:
                    _class = "function"
                elif text in WORD_OPERATOR:
                    _class = "operator"
                elif NUMERIC_TYPE.fullmatch(text):
                    _class = "type"
                elif GENERIC_TYPE.fullmatch(text):
                    _class = "type"
                    if ITALIC.fullmatch(text): italic = True
                else:
                    if ITALIC.fullmatch(text): italic = True
                    if following[1] in ('(', '⟨'):
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
                text = text.replace(
                    'TODO', f'\\<{ELEM} class="to-do">TODO</{ELEM}>'
                )
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
    'vfmadd231ps',
    'vfnmadd213ps',
    'vfnmadd231ps',
    'vmovaps',
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
                text = text.replace(
                    'TODO', f'\\<{ELEM} class="to-do">TODO</{ELEM}>'
                )
                esc = _escape(text)
                output.append(f'<{ELEM} class="comment">{esc}</{ELEM}>')

        index += 1

    return ''.join(output).splitlines()


def default_handler(lang, lines, modifiers=None):
    # The less-than character “<” is escaped as “&lt;”
    #   unless it is preceded by “\” or followed by “/”.
    match lang:
        case 'rs' | 'rust':
            comment1 = None
            comment2 = '//'
            delimcmt = ('/*', '*/')
        case 'rb' | 'ruby' | 'py' | 'python':
            comment1 = '#'
            comment2 = None
            delimcmt = None
        case 'asm' | 'assembly':
            comment1 = ';'
            comment2 = None
            delimcmt = None
        case _:
            comment1 = COMMENT_CHAR
            comment2 = COMMENT_DYAD
            delimcmt = None

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

    tokens = default_lexer(lines, quote1, quote2, comment1, comment2, delimcmt, mode)

    match lang:
        case 'asm' | 'assembly':
            return (None, assembly_parser(tokens))
        case _:
            return (None, default_parser(tokens))


BLANK_LINES = re.compile(r'\n{2,}')

THEORY_WORD    = re.compile(r"([a-z]?'|@)?([a-zA-Z][a-zA-Z0-9]*(?:-[a-zA-Z0-9]+)*)")
THEORY_GREEK   = re.compile(r"([a-z]?'|@)?([α-ωΑ-Ω])")
THEORY_NUMERIC = re.compile(r'\d+')

DELEGATED_SYMBOLS = {'+', '−', '×', '→', '←', '=', '|', '⟨', '⟩'}

PUNCTUATION = {
    '=': 'sp-3',
    ':': 'sp-3',
    '.': 'sp-3',
}

THEORY_DELIMITERS = {
    '(': ('sp-6', 'sp-7'),
    '[': ('sp-6', None  ),
    '⟨': (None  , 'sp-7'),

    ')': (None  , None  ),
    ']': (None  , None  ),
    '⟩': (None  , None  ),
}

THEORY_HIGHLIGHT = {
    'b': 'bl',
    'f': 'gy',
    'g': 'gr',
    'o': 'or',
    'p': 'pr',
    'r': 'rd',
}

def theory_parser(lines):
    text = '\n'.join(lines)

    length = len(text)
    final = length - 1
    tokens = []
    offset = 0

    while offset < length:
        match = WHITESPACE.match(text, offset)
        if match:
            span = match.group(0)
            newlines = span.count('\n')
            if newlines:
                for _ in range(newlines):
                    tokens.append(('newline', None))
                line_start = span.rindex('\n') + 1
                span = span[line_start:]
            if span:
                distance = span.count(' ') + span.count('\t') * 2
                tokens.append(('space', distance))
            offset = match.end()
            continue

        match = THEORY_GREEK.match(text, offset)
        if match:
            hi = None
            modifier = match.group(1)
            if modifier == '@':
                kind = 'keyword'
            elif modifier:
                kind = 'var'
                modifier = modifier.removesuffix("'")
                if modifier:
                    hi = THEORY_HIGHLIGHT.get(modifier, None)
            else:
                kind = 'const'
            letter = (kind, hi, match.group(2))
            tokens.append(('greek', letter))
            offset = match.end()
            continue

        match = THEORY_WORD.match(text, offset)
        if match:
            hi = None
            modifier = match.group(1)
            if modifier == '@':
                kind = 'keyword'
            elif modifier:
                kind = 'var'
                modifier = modifier.removesuffix("'")
                if modifier:
                    hi = THEORY_HIGHLIGHT.get(modifier, None)
            else:
                kind = 'const'
            word = (kind, hi, match.group(2))
            tokens.append(('word', word))
            offset = match.end()
            continue

        match = THEORY_NUMERIC.match(text, offset)
        if match:
            tokens.append(('number', match.group(0)))
            offset = match.end()
            continue

        match = HTML_ENTITY.match(text, offset)
        if match:
            tokens.append(('entity', match.group(0)))
            offset = match.end()
            continue

        char = text[offset]

        if char == '<':
            end = text.find('>', offset+1)
            if end > 0:
                tokens.append(('tag', text[offset:end+1]))
                offset = end + 1
                continue

        tokens.append(('symbol', char))
        offset += 1

    length = len(tokens)
    final = length - 1
    output = []

    for index, (kind, content) in enumerate(tokens):
        prev_kind, prev = tokens[index-1] if index > 0     else (None,  None)
        post_kind, post = tokens[index+1] if index < final else ('eof', None)
        match kind:
            case 'newline':
                output.append('\n')

            case 'space':
                # start of line
                if prev_kind == 'newline':
                    indent = round(content * 0.5, 6)
                    output.append(f'<span style="display: inline-block; width: {indent}em;"> </span>')

                # before punctuation
                elif post_kind == 'symbol' and post in PUNCTUATION:
                    element = PUNCTUATION[post]
                    output.append(f'<{element}> </{element}>')

                # after punctuation
                elif prev_kind == 'symbol' and prev in PUNCTUATION:
                    element = PUNCTUATION[prev]
                    output.append(f'<{element}> </{element}>')

                elif content > 1:
                    output.append('<sp-3> </sp-3>')

                else:
                    output.append(' ')

            case 'word':
                kind, hi, word = content
                if kind == 'var':
                    if hi:
                        output.append(f'<var class="{hi}">{word}</var>')
                    else:
                        output.append(f'<var>{word}</var>')
                elif word == 'Type':
                    output.append('<small-caps>type</small-caps>')
                else:
                    output.append(word)

            case 'greek':
                kind, hi, letter = content
                if kind == 'var' and hi:
                    output.append(f'<span class="gk {hi}">{letter}</span>')
                else:
                    output.append(f'<span class="gk">{letter}</span>')

            case 'symbol':
                leading  = None
                display  = content
                trailing = None

                match content:
                    case '&':
                        display ='<i>&amp;</i>'
                        if post_kind == 'word':
                            trailing = 'sp-7'

                    case '!':
                        display = '<i>!</i>'
                        if prev_kind == 'word' and prev[0] != 'var':
                            leading = 'sp-7'

                    case '.' | ':':
                        if content == '.':
                            if prev_kind == 'space' and post_kind == 'space':
                                display = '<span class="xb">.</span>'
                        if prev_kind == 'word' and prev[0] != 'var':
                            leading = 'sp-7'
                        if post_kind == 'word':
                            trailing = 'sp-7'

                    case _:
                        if content in DELEGATED_SYMBOLS:
                            display = f'<span class="cm">{content}</span>'

                if content in THEORY_DELIMITERS:
                    ld, tr = THEORY_DELIMITERS[content]
                    if prev_kind in ('word', 'greek', 'symbol', 'entity'):
                        leading = ld
                    if post_kind in ('word', 'greek', 'symbol', 'entity'):
                        trailing = tr

                if leading:
                    output.append(f'<{leading}> </{leading}>')

                output.append(display)

                if trailing:
                    output.append(f'<{trailing}> </{trailing}>')

            case 'entity':
                if content in DELEGATED_SYMBOLS:
                    output.append(f'<span class="cm">{content}</span>')
                else:
                    output.append(content)

            case _:
                output.append(content)

    output = ''.join(output).strip('\n')
    if '\n\n' in output:
        opening, closing = '<div class="sub-block">', '</div>'
        output = BLANK_LINES.sub(f'{closing}{opening}', output)
        output = f'{opening}{output}{closing}'

    return output.splitlines()


def theory_handler(lang, lines, modifiers=None):
    # The less-than character “<” is not escaped;
    #   if needed, “&lt;” should be used.
    return ('block-pre', theory_parser(lines))
