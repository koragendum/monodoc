import re

# "..." text
# *id   multicharacter
# \id   upright
# %id   small capitals
# &id   semibold
# &&id  bold
# _     subscript
# ^     superscript
# __    under
# ^^    over

# TODO root and sqrt

#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~

FRACTION = 'on'

KEYWORDS = {
    FRACTION: None,
    'all':    '∀',  # U+2200 FOR ALL
    'exists': '∃',  # U+2203 THERE EXISTS
    'prod':   '∏',  # U+220F N-ARY PRODUCT
    'sum':    '∑',  # U+2211 N-ARY SUMMATION
    'inf':    '∞',  # U+221E INFINITY
    'int':    '∫',  # U+222B INTEGRAL
    'ent':    '⊢',  # U+22A2 RIGHT TACK
    'star':   '⋆',  # U+22C6 STAR OPERATOR
}

OPERATORS = {
    '!': None,  # U+0021 EXCLAMATION MARK
    "'": '′',   # U+0027 APOSTROPHE -> U+2032 PRIME
    '(': None,  # U+0028 LEFT PARENTHESIS
    ')': None,  # U+0029 RIGHT PARENTHESIS
    '+': None,  # U+002B PLUS SIGN
    '-': '−',   # U+002D HYPHEN-MINUS -> U+2212 MINUS SIGN
#   '/': '∕',   # U+002F SOLIDUS -> U+2215 DIVISION SLASH
    '/': None,  # U+002F SOLIDUS
    ':': None,  # U+003A COLON
    '<': None,  # U+003C LESS-THAN SIGN
    '=': None,  # U+003D EQUALS SIGN
    '>': None,  # U+003E GREATER-THAN SIGN
    '[': None,  # U+005B LEFT SQUARE BRACKET
    ']': None,  # U+005D RIGHT SQUARE BRACKET
    '{': None,  # U+007B LEFT CURLY BRACKET
    '|': None,  # U+007C VERTICAL LINE
    '}': None,  # U+007D RIGHT CURLY BRACKET
    '~': '∼',   # U+007E TILDE -> U+223C TILDE OPERATOR
    '±': None,  # U+00B1 PLUS-MINUS SIGN
    '·': '⋅',   # U+00B7 MIDDLE DOT -> U+22C5 DOT OPERATOR
    '×': None,  # U+00D7 MULTIPLICATION SIGN
    '÷': None,  # U+00F7 DIVISION SIGN
    '←': None,  # U+2190 LEFTWARDS ARROW
    '→': None,  # U+2192 RIGHTWARDS ARROW
    '∂': None,  # U+2202 PARTIAL DIFFERENTIAL
    '−': None,  # U+2212 MINUS SIGN
    '∙': None,  # U+2219 BULLET OPERATOR
    '∧': None,  # U+2227 LOGICAL AND
    '∨': None,  # U+2228 LOGICAL OR
    '⋅': None,  # U+22C5 DOT OPERATOR
    '⟨': None,  # U+27E8 MATHEMATICAL LEFT ANGLE BRACKET
    '⟩': None,  # U+27E9 MATHEMATICAL RIGHT ANGLE BRACKET
}

DIGRAPHS = {
    '<-': '←',  # U+2190 LEFTWARDS ARROW
    '->': '→',  # U+2192 RIGHTWARDS ARROW
    '~-': '≃',  # U+2243 ASYMPTOTICALY EQUAL TO
    '~=': '≅',  # U+2245 APPROXIMATELY EQUAL TO
    '~~': '≈',  # U+2248 ALMOST EQUAL TO
    '/=': '≠',  # U+2260 NOT EQUAL TO
    '<=': '≤',  # U+2264 LESS-THAN OR EQUAL TO
    '>=': '≥',  # U+2265 GREATER-THAN OR EQUAL TO
    '//': '⁄',  # U+2044 FRACTION SLASH
}

# ∗ U+2217 ASTERISK OPERATOR
# ″ U+2033 DOUBLE PRIME
# ‴ U+2034 TRIPLE PRIME
# ∘ U+2218 RING OPERATOR
# ⊕ U+2295 CIRCLED PLUS
# ⊗ U+2297 CIRCLED TIMES

PUNCTUATION = {
    ',': 'comma',
    '.': 'period',
    ';': 'semi',
}

DISPLAY_SPACE = {
    'shelf':    '0.2em',
    'thin':     '0.1em',
    'med':      '0.2em',
    'thick':    '0.5em',
    'adjust':  '-0.2em',
    'dots':     '0.4em',
    'comma':    '0.3em',
    'period':   '0.2em',
    'semi':     '0.2em',
}
INLINE_SPACE = {
    'shelf':    '0.1em',
    'thin':     '0.1em',
    'med':      '0.2em',
    'thick':    '0.5em',
    'adjust':  '-0.3em',
    'dots':     '0.4em',
    'comma':    '0.3em',
    'period':   '0.2em',
    'semi':     '0.2em',
}

#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~

ESCAPE = {
    '<': '&lt;',
    '>': '&gt;',
}

NONLATIN = re.compile(r'[α-ωΑ-Ω\U0001D400-\U0001D7FF∞]')

class Atom:
    def __init__(self, kind, inner):
        self.kind = kind        # "mi", "mn", "mo", "mtext"
        self.inner = inner
        self.upright = False    # or unary (if operator)
        self.smallcaps = False
        self.weight = 0         # 0: regular, 1: semibold, 2: bold

    def render(self, lines, inline, indent):
        inner = self.inner
        opening = [self.kind]
        nonlatin = self.kind == 'mi' and NONLATIN.fullmatch(inner) is not None

        if self.kind == 'mi' and len(inner) == 1 and not nonlatin:
            opening.append('mathvariant="normal"')

        if self.kind == 'mo' and self.upright:
            opening.append('rspace="0"')
        if self.kind == 'mo' and inner == '⁄':
            # convert U+2044 FRACTION SLASH back to U+002F SOLIDUS
            inner = '/'
            opening.append('lspace="0"')
            opening.append('rspace="0"')
        if self.kind == 'mo' and inner == '|':
            opening.append('lspace="0.1em"')
            opening.append('rspace="0.1em"')

        classes = []
        if inner == '!': classes.append('exclam')
        if nonlatin:
            classes.append('mf')
        if self.kind != 'mo' and self.upright:
            classes.append('rm')
        if self.smallcaps:   classes.append('sc')
        if self.weight == 1: classes.append('sb')
        if self.weight == 2: classes.append('bf')
        if len(classes) > 0:
            classes = " ".join(classes)
            opening.append(f'class="{classes}"')

        if self.kind == 'mo':
            inner = ESCAPE.get(inner, inner)

        lines.append(f'{"  "*indent}<{" ".join(opening)}>{inner}</{self.kind}>')

class Space:
    def __init__(self, width):
        self.width = width  # numeric (in em) or 'shelf'

    def render(self, lines, inline, indent):
        space = INLINE_SPACE if inline else DISPLAY_SPACE
        width = space.get(self.width, self.width)
        lines.append(f'{"  "*indent}<mspace width="{width}"/>')

class Frac:
    def __init__(self, upper, lower):
        self.upper = upper
        self.lower = lower

    def render(self, lines, inline, indent):
        shelf = Space('shelf')
        upper = Row(
            [shelf, *self.upper.sequence, shelf] if isinstance(self.upper, Row)
            else [shelf, self.upper, shelf]
        )
        lower = Row(
            [shelf, *self.lower.sequence, shelf] if isinstance(self.lower, Row)
            else [shelf, self.lower, shelf]
        )
        margin = '  ' * indent
        lines.append(f'{margin}<mfrac>')
        upper.render(lines, inline, indent+1)
        lower.render(lines, inline, indent+1)
        lines.append(f'{margin}</mfrac>')

STRUCT = {
    ('script', True , False): 'msub',
    ('script', False, True ): 'msup',
    ('script', True , True ): 'msubsup',
    ('stack' , True , False): 'munder',
    ('stack' , False, True ): 'mover',
    ('stack' , True , True ): 'munderover',
}

class Struct:
    def __init__(self, kind, center):
        self.kind = kind    # 'script' or 'stack'
        self.center = center
        self.upper = None
        self.lower = None

    def render(self, lines, inline, indent):
        # if not inline and isinstance(self.center, Atom) \
        #     and self.center.kind == 'mo' and self.center.inner == '∑':
        #     kind = 'stack'
        # else:
        #     kind = self.kind
        kind = self.kind
        margin = '  ' * indent
        has_lower = self.lower is not None
        has_upper = self.upper is not None
        element = STRUCT[(kind, has_lower, has_upper)]
        lines.append(f'{margin}<{element}>')
        self.center.render(lines, inline, indent+1)
        if self.lower is not None:
            if isinstance(self.center, Atom) and self.center.kind == 'mo' \
                and self.center.inner == '∫':
                adj = Space('adjust')
                lower = Row(
                    [adj, *self.lower.sequence] if isinstance(self.lower, Row)
                    else [adj, self.lower]
                )
            else:
                lower = self.lower
            lower.render(lines, inline, indent+1)
        if self.upper is not None:
            self.upper.render(lines, inline, indent+1)
        lines.append(f'{margin}</{element}>')

class Row:
    def __init__(self, sequence):
        self.sequence = sequence
        self.root = False

    def render(self, lines, inline, indent):
        margin = '  ' * indent
        if self.root:
            element = 'math'
            if inline:
                attrs = ' display="inline" class="inline"'
            else:
                attrs = ' display="block"'
        else:
            element = 'mrow'
            attrs = ''

        lines.append(f'{margin}<{element}{attrs}>')
        for item in self.sequence:
            item.render(lines, inline, indent+1)
        lines.append(f'{margin}</{element}>')

IDENTIFIER = re.compile(r'([a-zA-Zα-ωΑ-Ω\U0001D400-\U0001D7FF∞])|\*([a-zA-Z]+)')
SPECIAL = re.compile('(?:' + '|'.join(KEYWORDS) + ')(?![a-zA-Z])')
NUMERIC = re.compile(r'\d+(?:\.\d+)?')

def parse(text):
    def escape(x):
        return x.replace(r'\.', r'¹').replace(r'\ ', '²').replace(r'\:', '³')

    blocks = []
    offset = 0
    while True:
        try: start = text.index('"', offset)
        except ValueError: break

        try: end = text.index('"', start+1)
        except: return None

        blocks.extend(x.strip() for x in escape(text[offset:start]).split())
        blocks.append(Atom('mtext', text[start+1:end]))
        offset = end + 1

    blocks.extend(x.strip() for x in escape(text[offset:]).split())

    tokens = []
    for block in blocks:
        if isinstance(block, Atom):
            tokens.append(block)
            continue

        block_len = len(block)
        offset = 0
        while offset < block_len:
            match = NUMERIC.match(block, offset)
            if match is not None:
                num = match.group()
                tokens.append(Atom('mn', num))
                offset += len(num)
                continue

            match = SPECIAL.match(block, offset)
            if match is not None:
                word = match.group()
                if word == FRACTION:
                    tokens.append('/')
                else:
                    tokens.append(Atom('mo', KEYWORDS[word]))
                offset += len(word)
                continue

            match = IDENTIFIER.match(block, offset)
            if match is not None:
                word = match.group(1) or match.group(2)
                tokens.append(Atom('mi', word))
                offset += len(match.group())
                continue

            trip = block[offset:offset+3]
            if trip == '...':
                tokens.append(Atom('mtext', '. . .'))
                tokens.append(Space('period'))
                offset += 3
                continue

            if trip == '···':
                tokens.append(Space('dots'))
                tokens.append(Atom('mtext', '· · ·'))
                tokens.append(Space('dots'))
                offset += 3
                continue

            pair = block[offset:offset+2]
            if pair in ('__', '^^', '&&'):
                tokens.append(pair)
                offset += 2
                continue

            if pair in DIGRAPHS:
                tokens.append(Atom('mo', DIGRAPHS[pair]))
                offset += 2
                continue

            char = block[offset]
            if char in ('{', '}', '_', '^', '\\', '&', '%'):
                tokens.append(char)
                offset += 1
                continue

            if char in OPERATORS:
                tokens.append(Atom('mo', OPERATORS[char] or char))
                offset += 1
                continue

            if char in PUNCTUATION:
                tokens.append(Atom('mtext', char))
                tokens.append(Space(PUNCTUATION[char]))
                offset += 1
                continue

            if char in ('¹', '²', '³'):
                SKIP = {'¹': 'thin', '²': 'med', '³': 'thick'}
                tokens.append(Space(SKIP[char]))
                offset += 1
                continue

            return None

    weight = 0
    upright = False
    smallcaps = False
    coalesced = []
    for token in tokens:
        if token == '&':
            weight = max(weight, 1)
        elif token == '&&':
            weight = max(weight, 2)
        elif token == '\\':
            upright = True
        elif token == '%':
            smallcaps = True
        elif isinstance(token, Atom):
            token.weight = weight
            token.upright = upright
            token.smallcaps = smallcaps
            coalesced.append(token)
            weight = 0
            upright = False
            smallcaps = False
        else:
            if weight > 0 or upright or smallcaps:
                return None
            coalesced.append(token)

    coalesced_len = len(coalesced)

    def get(offset, depth):
        if offset >= coalesced_len:
            return (offset, None)
        item = coalesced[offset]
        if item == '{':
            return parse(offset+1, depth+1)
        return (offset+1, item)

    def parse(offset, depth):
        sequence = []
        while offset < coalesced_len:
            offset, item = get(offset, depth)
            if item is None:
                return (offset, None)
            if item == '}':
                if depth == 0:
                    return (offset, None)
                break
            if item in ('/', '_', '^', '__', '^^'):
                if len(sequence) == 0:
                    return (offset, None)
                prev = sequence[-1]
                offset, arg = get(offset, depth)
                if arg is None:
                    return (offset, None)
                if not isinstance(prev, (Atom, Frac, Struct, Row)):
                    return (offset, None)
                if not isinstance(arg, (Atom, Frac, Struct, Row)):
                    return (offset, None)
                if item == '/':
                    sequence[-1] = Frac(prev, arg)
                else:
                    kind = 'stack' if item in ('__', '^^') else 'script'
                    if isinstance(prev, Struct) and prev.kind == kind:
                        if item in ('_', '__'):
                            if struct.lower is not None:
                                return (offset, None)
                            struct.lower = arg
                        if item in ('^', '^^'):
                            if struct.upper is not None:
                                return (offset, None)
                            struct.upper = arg
                    else:
                        struct = Struct(kind, prev)
                        if item in ('_', '__'):
                            struct.lower = arg
                        if item in ('^', '^^'):
                            struct.upper = arg
                        sequence[-1] = struct
                continue
            sequence.append(item)
        else:
            if depth > 0:
                return (offset, None)

        while len(sequence) > 0 and isinstance(sequence[0], Space):
            sequence.pop(0)
        while len(sequence) > 0 and isinstance(sequence[-1], Space):
            sequence.pop()

        if len(sequence) == 0:
            result = None
        elif len(sequence) == 1:
            result = sequence[0]
        else:
            result = Row(sequence)
        return (offset, result)

    _, result = parse(0, 0)
    if result is None:
        return None
    if not isinstance(result, Row):
        result = Row([result])
    result.root = True
    return result

def render(expr, inline, indent=0):
    lines = []
    expr.render(lines, inline, indent)
    return lines
