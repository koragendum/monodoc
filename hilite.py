import re


WHITESPACE = re.compile(r'\s+')

WORD = re.compile("'?[_a-zA-Zα-ωΑ-Ω][_a-zA-Zα-ωΑ-Ω0-9'-]*[!?]?")

NUMERIC = re.compile(r'([+−])?(\d+)(\.\d+)?')

LEFT_DELIM  = {'(', '[', '⟨', '{'}
RIGHT_DELIM = {')', ']', '⟩', '}'}

DYAD = {'->', '<-', '=>', '<=', '::', '||', '&&', '<<', '>>', '//', '++', '<>'}

LEFT_QUOTE1  = '‘'
RIGHT_QUOTE1 = '’'

LEFT_QUOTE2  = '“'
RIGHT_QUOTE2 = '”'

COMMENT_CHAR = '#'
COMMENT_DYAD = '//'

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
        fragments.append(text[taken:])

    return ''.join(fragments)

def lex(lines):
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

        match = WORD.match(text, offset)
        if match:
            tokens.append(('word', match.group(0)))
            offset = match.end()
            continue

        match = NUMERIC.match(text, offset)
        if match:
            sign, integer, fractional = match.groups()
            if sign and tokens and tokens[-1][0] in LEFT_OPERAND:
                tokens.append(('symbol', sign))
                sign = ''
            elif sign is None:
                sign = ''
            if fractional:
                tokens.append(('fractional', sign + integer + fractional))
            else:
                tokens.append(('integer', sign + integer))
            offset = match.end()
            continue

        char = text[offset]

        if char == '\\' and offset < final and text[offset+1] == '<':
            end = text.find('>', offset+2)
            if end > 0:
                tokens.append(('tag', text[offset+1:end+1]))
                offset = end + 1
                continue

        if char == '<' and offset < final and text[offset+1] == '/':
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

        if char == LEFT_QUOTE1:
            end = text.find(RIGHT_QUOTE1, offset+1)
            if end > 0:
                tokens.append(('quote1', text[offset:end+1]))
                offset = end + 1
                continue

        if char == LEFT_QUOTE2:
            end = text.find(RIGHT_QUOTE2, offset+1)
            if end > 0:
                tokens.append(('quote2', text[offset:end+1]))
                offset = end + 1
                continue

        pair = text[offset:offset+2]

        if char == COMMENT_CHAR or pair == COMMENT_DYAD:
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
}

FUNCTION = {'and', 'or', 'not', 'xor', 'mod', 'as'}

CONSTANT = {'NONE', 'None', 'none', 'NULL', 'null', 'nil', 'TAU', 'tau'}

GENERIC_TYPE = re.compile('[A-ZΑ-Ω][a-zA-Zα-ωΑ-Ω0-9]*')

NUMERIC_TYPE = re.compile('[uif][1-9][0-9]*')

OPERATOR = re.compile('[+−×/÷<>≤≥=≠~!*&|-]*')

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

def default_handler(lang, lines, modifiers=None):
    # The less-than character “<” is escaped as “&lt;”
    #   unless it is preceded by “\” or followed by “/”.
    tokens = lex(lines)
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
                if text in KEYWORD:
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
                output.append(
                    f'<{ELEM} class="delimiter {DELIM_NAME[text]}"'
                    # f' data-depth="{depth}"'
                    # f' data-{DELIM_NAME[text]}-depth="{var_depth[var]}">'
                    f' data-depth="{var_depth[var]}">'
                    f'{text}</{ELEM}>'
                )
                if kind == 'ldelim':
                    depth += 1
                    var_depth[var] += 1

            case 'integer':
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
