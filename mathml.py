import re

# TODO digraphs for U+2061 FUNCTION APPLICATION
#                   U+2062 INVISIBLE TIMES
#                   U+2063 INVISIBLE SEPARATOR
#                   U+2064 INVISIBLE PLUS

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

# <math display="block">      sets    math-style: normal;
# <math display="inline">     sets    math-style: compact;

# <* displaystyle="true">     sets    math-style: normal;
# <* displaystyle="false">    sets    math-style: compact;

# <mo movablelimits="true">   moves under/over to sub/sup when math-style is compact

#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~

KEYWORDS = {
    'on':     'frac',
    'sqrt':   'sqrt',
    'all':    '∀',  # U+2200 FOR ALL
    'exists': '∃',  # U+2203 THERE EXISTS
    'prod':   '∏',  # U+220F N-ARY PRODUCT
    'sum':    '∑',  # U+2211 N-ARY SUMMATION
    'inf':    '∞',  # U+221E INFINITY
    'int':    '∫',  # U+222B INTEGRAL
    'ent':    '⊢',  # U+22A2 RIGHT TACK
    'star':   '⋆',  # U+22C6 STAR OPERATOR
    'lt':     '<',  # U+003C LESS-THAN SIGN
    'gt':     '>',  # U+003E GREATER-THAN SIGN
}

OPERATORS = {
    '!': None,  # U+0021 EXCLAMATION MARK
    "'": '′',   # U+0027 APOSTROPHE -> U+2032 PRIME
    '(': None,  # U+0028 LEFT PARENTHESIS
    ')': None,  # U+0029 RIGHT PARENTHESIS
    '+': None,  # U+002B PLUS SIGN
    '-': '−',   # U+002D HYPHEN-MINUS -> U+2212 MINUS SIGN
    '.': None,  # U+002E FULL STOP
#   '/': '∕',   # U+002F SOLIDUS -> U+2215 DIVISION SLASH
    '/': None,  # U+002F SOLIDUS
    ':': None,  # U+003A COLON
    '<': None,  # U+003C LESS-THAN SIGN
    '=': None,  # U+003D EQUALS SIGN
    '>': None,  # U+003E GREATER-THAN SIGN
    '?': None,  # U+003F QUESTION MARK
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
    '↑': None,  # U+2191 UPWARDS ARROW
    '→': None,  # U+2192 RIGHTWARDS ARROW
    '↓': None,  # U+2193 DOWNWARDS ARROW
    '⇐': None,  # U+21D0 LEFTWARDS DOUBLE ARROW
    '⇒': None,  # U+21D2 RIGHTWARDS DOUBLE ARROW
    '∂': None,  # U+2202 PARTIAL DIFFERENTIAL
    '−': None,  # U+2212 MINUS SIGN
    '∘': None,  # U+2218 RING OPERATOR
    '∙': None,  # U+2219 BULLET OPERATOR
    '∧': None,  # U+2227 LOGICAL AND
    '∨': None,  # U+2228 LOGICAL OR
    '⊕': None,  # U+2295 CIRCLED PLUS
    '⊗': None,  # U+2297 CIRCLED TIMES
    '⋅': None,  # U+22C5 DOT OPERATOR
    '⋮': None,  # U+22EE VERTICAL ELLIPSIS
    '⋯': None,  # U+22EF MIDLINE HORIZONTAL ELLIPSIS
    '⟨': None,  # U+27E8 MATHEMATICAL LEFT ANGLE BRACKET
    '⟩': None,  # U+27E9 MATHEMATICAL RIGHT ANGLE BRACKET
    '⟪': None,  # U+27EA MATHEMATICAL LEFT DOUBLE ANGLE BRACKET
    '⟫': None,  # U+27EB MATHEMATICAL RIGHT DOUBLE ANGLE BRACKET
}

DIGRAPHS = {
    '<-': '←',  # U+2190 LEFTWARDS ARROW
    '->': '→',  # U+2192 RIGHTWARDS ARROW
    '<=': '⇐',  # U+21D0 LEFTWARDS DOUBLE ARROW
    '=>': '⇒',  # U+21D2 RIGHTWARDS DOUBLE ARROW
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

PUNCTUATION = {
    ',': 'comma',
    '.': 'period',
    ';': 'semi',
}

SPACE = {
    #         ( display,  inline )
    'shelf':  ( '0.2em',  '0.1em'),    # fraction rule
    'sadj':   ('-0.4em', '-0.4em'),    # fraction superscript
    'ladj':   ('-0.2em', '-0.3em'),    # integral lower bound
    'uadj':   ( '0.1em',  '0.0em'),    # integral upper bound

    'neg':    ('-0.1em', '-0.1em'),
    'thin':   ( '0.1em',  '0.1em'),
    'med':    ( '0.2em',  '0.2em'),
    'thick':  ( '0.5em',  '0.5em'),

    'dots':   ( '0.4em',  '0.4em'),
    'comma':  ( '0.3em',  '0.3em'),
    'period': ( '0.2em',  '0.2em'),
    'semi':   ( '0.2em',  '0.2em'),
}

def space(dimen, inline):
    if dimen in SPACE:
        return SPACE[dimen][int(inline)]
    return dimen

#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~

ESCAPE = {
    '<': '&lt;',
    '>': '&gt;',
}

LATIN = re.compile(r'[a-zA-Zſ][a-zA-Zſ\u0300-\u036F]*')
GREEK = re.compile(r'[α-ωΑ-Ω]+')
DELIM = {'(', ')', '[', ']', '⟨', '⟩', '⟪', '⟫', '|'}
CLOSE = {')', ']', '⟩', '⟫', '|', '!', '?', '⋯'}

VARIANTS = {
    'A': ('𝒜', '𝓐', '𝔄', '𝕬', '𝔸'),
    'B': ('ℬ', '𝓑', '𝔅', '𝕭', '𝔹'),
    'C': ('𝒞', '𝓒', 'ℭ', '𝕮', 'ℂ'),
    'D': ('𝒟', '𝓓', '𝔇', '𝕯', '𝔻'),
    'E': ('ℰ', '𝓔', '𝔈', '𝕰', '𝔼'),
    'F': ('ℱ', '𝓕', '𝔉', '𝕱', '𝔽'),
    'G': ('𝒢', '𝓖', '𝔊', '𝕲', '𝔾'),
    'H': ('ℋ', '𝓗', 'ℌ', '𝕳', 'ℍ'),
    'I': ('ℐ', '𝓘', 'ℑ', '𝕴', '𝕀'),
    'J': ('𝒥', '𝓙', '𝔍', '𝕵', '𝕁'),
    'K': ('𝒦', '𝓚', '𝔎', '𝕶', '𝕂'),
    'L': ('ℒ', '𝓛', '𝔏', '𝕷', '𝕃'),
    'M': ('ℳ', '𝓜', '𝔐', '𝕸', '𝕄'),
    'N': ('𝒩', '𝓝', '𝔑', '𝕹', 'ℕ'),
    'O': ('𝒪', '𝓞', '𝔒', '𝕺', '𝕆'),
    'P': ('𝒫', '𝓟', '𝔓', '𝕻', 'ℙ'),
    'Q': ('𝒬', '𝓠', '𝔔', '𝕼', 'ℚ'),
    'R': ('ℛ', '𝓡', 'ℜ', '𝕽', 'ℝ'),
    'S': ('𝒮', '𝓢', '𝔖', '𝕾', '𝕊'),
    'T': ('𝒯', '𝓣', '𝔗', '𝕿', '𝕋'),
    'U': ('𝒰', '𝓤', '𝔘', '𝖀', '𝕌'),
    'V': ('𝒱', '𝓥', '𝔙', '𝖁', '𝕍'),
    'W': ('𝒲', '𝓦', '𝔚', '𝖂', '𝕎'),
    'X': ('𝒳', '𝓧', '𝔛', '𝖃', '𝕏'),
    'Y': ('𝒴', '𝓨', '𝔜', '𝖄', '𝕐'),
    'Z': ('𝒵', '𝓩', 'ℨ', '𝖅', 'ℤ'),
    'a': ('𝒶', '𝓪', '𝔞', '𝖆', '𝕒'),
    'b': ('𝒷', '𝓫', '𝔟', '𝖇', '𝕓'),
    'c': ('𝒸', '𝓬', '𝔠', '𝖈', '𝕔'),
    'd': ('𝒹', '𝓭', '𝔡', '𝖉', '𝕕'),
    'e': ('ℯ', '𝓮', '𝔢', '𝖊', '𝕖'),
    'f': ('𝒻', '𝓯', '𝔣', '𝖋', '𝕗'),
    'g': ('ℊ', '𝓰', '𝔤', '𝖌', '𝕘'),
    'h': ('𝒽', '𝓱', '𝔥', '𝖍', '𝕙'),
    'i': ('𝒾', '𝓲', '𝔦', '𝖎', '𝕚'),
    'j': ('𝒿', '𝓳', '𝔧', '𝖏', '𝕛'),
    'k': ('𝓀', '𝓴', '𝔨', '𝖐', '𝕜'),
    'l': ('𝓁', '𝓵', '𝔩', '𝖑', '𝕝'),
    'm': ('𝓂', '𝓶', '𝔪', '𝖒', '𝕞'),
    'n': ('𝓃', '𝓷', '𝔫', '𝖓', '𝕟'),
    'o': ('ℴ', '𝓸', '𝔬', '𝖔', '𝕠'),
    'p': ('𝓅', '𝓹', '𝔭', '𝖕', '𝕡'),
    'q': ('𝓆', '𝓺', '𝔮', '𝖖', '𝕢'),
    'r': ('𝓇', '𝓻', '𝔯', '𝖗', '𝕣'),
    's': ('𝓈', '𝓼', '𝔰', '𝖘', '𝕤'),
    't': ('𝓉', '𝓽', '𝔱', '𝖙', '𝕥'),
    'u': ('𝓊', '𝓾', '𝔲', '𝖚', '𝕦'),
    'v': ('𝓋', '𝓿', '𝔳', '𝖛', '𝕧'),
    'w': ('𝓌', '𝔀', '𝔴', '𝖜', '𝕨'),
    'x': ('𝓍', '𝔁', '𝔵', '𝖝', '𝕩'),
    'y': ('𝓎', '𝔂', '𝔶', '𝖞', '𝕪'),
    'z': ('𝓏', '𝔃', '𝔷', '𝖟', '𝕫'),
}

class Atom:
    def __init__(self, kind, inner):
        self.kind = kind        # "mi", "mn", "mo", "mtext"
        self.inner = inner
        self.upright = False    # or unary if operator
        self.smallcaps = False
        self.weight = 0         # 0 regular, 1 semibold, 2 bold
        self.height = 0
        self.variant = False

    def tall(self):
        return self.kind == 'mo' and self.upright and self.inner in DELIM

    def render(self, lines, inline, indent, prev=None):
        inner = self.inner
        weight = self.weight

        opening = [self.kind]
        classes = []

        if self.kind == 'mo':
            delim = inner in DELIM

            zero_lspace = False
            zero_rspace = False

            if inner in ('+', '−'):
                if isinstance(prev, Atom) and prev.kind == 'mo' \
                and prev.inner not in CLOSE:
                    zero_lspace = True
                if self.upright:
                    zero_rspace = True  # unary

            if inner in ('→', '←', '⇒', '⇐', '↑', '↓'):
                if self.upright:
                    zero_lspace = True
                    zero_rspace = True

            # convert U+2044 FRACTION SLASH back to U+002F SOLIDUS
            if inner == '⁄':
                inner = '/'
                zero_lspace = True
                zero_rspace = True

            if zero_lspace: opening.append('lspace="0"')
            if zero_rspace: opening.append('rspace="0"')

            if inner in ('|', '<', '>'):
                opening.append('lspace="0.15em"')
                opening.append('rspace="0.15em"')

            if inner == ':' and self.upright:
                opening.append('lspace="0.075em"')
                opening.append('rspace="0.075em"')

            if inner == '=' and self.upright:
                opening.append('lspace="0.075em"')
                opening.append('rspace="0.075em"')

            if delim:
                if self.height > 0:
                    SIZES = ['1em', '1.25em', '1.5em', '1.75em', '2em']
                    height = min(self.height, 4)
                    size = SIZES[height]
                    opening.append(f'minsize="{size}"')
                    opening.append(f'maxsize="{size}"')
                elif self.upright:
                    size = '1.25em' if inline else '2em'
                    opening.append(f'minsize="{size}"')
                    opening.append(f'maxsize="{size}"')
                else:
                    opening.append('stretchy="false"')  # Chromium and Safari

            inner = ESCAPE.get(inner, inner)

        if self.kind == 'mi':
            latin = LATIN.fullmatch(inner) is not None

            if latin and self.variant:
                classes.append('mf')

                if self.smallcaps:
                    if self.upright:
                        # doublestruck
                        index = 4
                    else:
                        # blackletter
                        index = 3 if weight > 0 else 2
                        weight = 0
                else:
                    # script
                    if self.upright:
                        classes.append('ca')
                    index = 1 if weight > 0 else 0
                    weight = 0

                inner = VARIANTS.get(inner, inner)[index]

            else:
                greek = GREEK.fullmatch(inner) is not None
                greek = greek and not self.variant

                if len(inner) == 1 and (latin or greek or self.upright):
                    opening.append('mathvariant="normal"')  # Firefox

                if latin:
                    if 'ſ' in inner:
                        classes.append('alt')
                elif greek:
                    classes.append('gk')
                else:
                    classes.append('mf')

                if (latin or greek) and self.upright:
                    classes.append('rm')

                if self.smallcaps:
                    classes.append('sc')

        if weight == 1: classes.append('sb')
        if weight == 2: classes.append('bf')
        if inner == '!': classes.append('it')
        if inner == '?': classes.append('it')

        if len(classes) > 0:
            classes = " ".join(classes)
            opening.append(f'class="{classes}"')

        lines.append(f'{"  "*indent}<{" ".join(opening)}>{inner}</{self.kind}>')

class Space:
    def __init__(self, width, height=None, depth=None):
        self.width = width  # numeric (in em) or 'shelf'
        self.height = None
        self.depth = None

    def render(self, lines, inline, indent, prev=None):
        width = space(self.width, inline)
        attrs = [f'width="{width}"']
        if self.height is not None:
            height = space(self.height, inline)
            attrs.append(f'height="{height}"')
        if self.depth is not None:
            depth = space(self.depth, inline)
            attrs.append(f'depth="{depth}"')
        attrs = ' '.join(attrs)
        lines.append(f'{"  "*indent}<mspace {attrs}/>')

class Empty:
    def __init__(self):
        pass

    def render(self, lines, inline, indent, prev=None):
        lines.append(f'{"  "*indent}<mspace height="0" depth="0" width="0"/>')

class Boxed:
    def __init__(self,
        sequence,
        height=None,
        depth=None,
        width=None,
        voffset=None,
        hoffset=None,
    ):
        self.sequence = sequence
        self.height   = height
        self.depth    = depth
        self.width    = width
        self.voffset  = voffset
        self.hoffset  = hoffset

    def render(self, lines, inline, indent, prev=None):
        margin = '  ' * indent
        opening = ['mpadded']
        if self.height is not None:
            height = space(self.height, inline)
            opening.append(f'height="{height}"')
        if self.depth is not None:
            depth = space(self.depth, inline)
            opening.append(f'depth="{depth}"')
        if self.width is not None:
            width = space(self.width, inline)
            opening.append(f'width="{width}"')
        if self.voffset is not None:
            voffset = space(self.voffset, inline)
            opening.append(f'voffset="{voffset}"')
        if self.hoffset is not None:
            hoffset = space(self.hoffset, inline)
            opening.append(f'lspace="{hoffset}"')
        lines.append(f'{margin}<{" ".join(opening)}>')
        prev = None
        for item in self.sequence:
            item.render(lines, inline, indent+1, prev)
            prev = item
        lines.append(f'{margin}</mpadded>')

class Frac:
    def __init__(self, upper, lower):
        self.upper = upper
        self.lower = lower

    def render(self, lines, inline, indent, prev=None):
        shelf = Space('shelf')
        upper = Row(
            [shelf, *self.upper.sequence, shelf] if isinstance(self.upper, Row)
            else (
                [self.upper]
                if isinstance(self.upper, (Empty, Space)) or (
                    isinstance(self.upper, Atom) and self.upper.inner == ''
                )
                else [shelf, self.upper, shelf]
            )
        )
        lower = Row(
            [shelf, *self.lower.sequence, shelf] if isinstance(self.lower, Row)
            else (
                [self.lower]
                if isinstance(self.lower, (Empty, Space)) or (
                    isinstance(self.lower, Atom) and self.lower.inner == ''
                )
                else [shelf, self.lower, shelf]
            )
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

    def render(self, lines, inline, indent, prev=None):
        margin = '  ' * indent
        has_lower = self.lower is not None
        has_upper = self.upper is not None
        element = STRUCT[(self.kind, has_lower, has_upper)]
        lines.append(f'{margin}<{element}>')
        self.center.render(lines, inline, indent+1)
        if has_lower:
            if isinstance(self.center, Atom) and self.center.kind == 'mo' \
            and self.center.inner == '∫':
                lower = Boxed(
                    self.lower.sequence if isinstance(self.lower, Row)
                    else [self.lower],
                    hoffset='ladj'
                )
            else:
                lower = self.lower
            lower.render(lines, inline, indent+1)
        if has_upper:
            if isinstance(self.center, Atom) and self.center.kind == 'mo' \
            and self.center.inner == '∫':
                adj = Space('uadj')
                upper = Row(
                    [adj, *self.upper.sequence] if isinstance(self.lower, Row)
                    else [adj, self.upper]
                )
            elif self.kind == 'script' and isinstance(self.center, Row) \
            and any(
                isinstance(item, Atom) and item.tall()
                for item in self.center.sequence
            ):
                adj = Space('sadj')
                upper = Row(
                    [adj, *self.upper.sequence] if isinstance(self.lower, Row)
                    else [adj, self.upper]
                )
            elif self.kind == 'script' and isinstance(self.upper, Atom) \
            and self.upper.kind == 'mi' and self.upper.inner == '⋆':
                upper = Boxed([self.upper], height='0')
            else:
                upper = self.upper
            upper.render(lines, inline, indent+1)
        lines.append(f'{margin}</{element}>')

class Sqrt:
    def __init__(self, inner):
        self.inner = inner

    def render(self, lines, inline, indent, prev=None):
        margin = '  ' * indent
        lines.append(f'{margin}<msqrt>')
        self.inner.render(lines, inline, indent+1)
        lines.append(f'{margin}</msqrt>')

class Phantom:
    def __init__(self, inner):
        self.inner = inner

    def render(self, lines, inline, indent, prev=None):
        margin = '  ' * indent
        lines.append(f'{margin}<mphantom>')
        self.inner.render(lines, inline, indent+1)
        lines.append(f'{margin}</mphantom>')

class Row:
    def __init__(self, sequence):
        self.sequence = sequence
        self.root = False

    def render(self, lines, inline, indent, prev=None):
        margin = '  ' * indent
        if self.root:
            element = 'math'
            display = 'inline' if inline else 'block'
            attrs = f' display="{display}"'
        else:
            element = 'mrow'
            attrs = ''

        lines.append(f'{margin}<{element}{attrs}>')
        prev = None
        for item in self.sequence:
            item.render(lines, inline, indent+1, prev)
            prev = item
        lines.append(f'{margin}</{element}>')

IDENTIFIER = re.compile(r'([a-zA-Zα-ωΑ-Ωſ•∞\U0001D400-\U0001D7FF][\u0300-\u036F]?)|\*([a-zA-Zſ\u0300-\u036F]+)')
SPECIAL = re.compile('(?:' + '|'.join(KEYWORDS) + ')(?![a-zA-Z])')
NUMERIC = re.compile(r'\d+(?:\.\d+)?|[½⅓⅔¼¾⅕⅖⅗⅘⅙⅚⅛⅜⅝⅞]')
INTEGER = re.compile(r'\d+')
SKIP = {'₋': 'neg', '₁': 'thin', '₂': 'med', '₃': 'thick'}

# TODO for “:” keep track of whether there is a space (in the source) on the
#   lefthand side and use that to determine whether it is a label or a relation

def parse(text):
    def escape(x):
        return x.replace(r'\ ', '₂')

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
                if len(tokens) > 0 and tokens[-1] == '\\' \
                and INTEGER.fullmatch(num) is not None:
                    tokens[-1] = int(num)
                else:
                    tokens.append(Atom('mn', num))
                offset += len(num)
                continue

            match = SPECIAL.match(block, offset)
            if match is not None:
                word = match.group()
                resolved = KEYWORDS[word]
                if resolved in ('frac', 'sqrt'):
                    tokens.append(resolved)
                elif resolved in ('∞', '⋆'):
                    tokens.append(Atom('mi', resolved))
                else:
                    tokens.append(Atom('mo', resolved))
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
            if char in ('{', '}', '_', '^', '\\', '&', '%', '@'):
                tokens.append(char)
                offset += 1
                continue

            if len(tokens) > 0 and tokens[-1] == '\\' and char in PUNCTUATION:
                tokens.append(Atom('mtext', char))
                tokens.append(Space(PUNCTUATION[char]))
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

            if char in SKIP:
                tokens.append(Space(SKIP[char]))
                offset += 1
                continue

            return None

    weight = 0
    height = 0
    upright   = False
    smallcaps = False
    calli     = False
    coalesced = []
    for token in tokens:
        if isinstance(token, int):
            height = max(height, token)
        elif token == '&':
            weight = max(weight, 1)
        elif token == '&&':
            weight = max(weight, 2)
        elif token == '\\':
            upright = True
        elif token == '%':
            smallcaps = True
        elif token == '@':
            calli = True
        elif isinstance(token, Atom):
            token.weight = weight
            token.height = height
            token.upright = upright
            token.smallcaps = smallcaps
            token.variant = calli
            coalesced.append(token)
            weight = 0
            height = 0
            upright = False
            smallcaps = False
            calli = False
        else:
            if weight > 0 or height > 0 or upright or smallcaps or calli:
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
            if item == 'sqrt':
                offset, arg = get(offset, depth)
                if arg is None:
                    return (offset, None)
                if not isinstance(arg, (Atom, Boxed, Frac, Struct, Sqrt, Phantom, Row, Empty)):
                    return (offset, None)
                sequence.append(Sqrt(arg))
                continue
            if item in ('_', '^', '__', '^^', 'frac'):
                if len(sequence) == 0:
                    return (offset, None)
                prev = sequence[-1]
                offset, arg = get(offset, depth)
                if arg is None:
                    return (offset, None)
                if not isinstance(prev, (Atom, Boxed, Frac, Struct, Sqrt, Phantom, Row, Empty)):
                    return (offset, None)
                if not isinstance(arg, (Atom, Boxed, Frac, Struct, Sqrt, Phantom, Row, Empty)):
                    return (offset, None)
                if item == 'frac':
                    sequence[-1] = Frac(prev, arg)
                    continue
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
                    continue
                # This is a hack to allow both under and sub on a sum.
                if isinstance(prev, Struct) \
                    and prev.kind == 'stack' and kind == 'script':
                    prev = Boxed([prev], height="1.0em", depth="0.5em")
                struct = Struct(kind, prev)
                if item in ('_', '__'):
                    struct.lower = arg
                if item in ('^', '^^'):
                    struct.upper = arg
                sequence[-1] = struct
                continue
            # Remove punctuation space before unary plus and minus
            if len(sequence) >= 2 and isinstance(item, Atom) \
            and item.kind == 'mo' and item.inner in ('+', '−'):
                penult = sequence[-2]
                ultima = sequence[-1]
                if isinstance(penult, Atom) and penult.inner in PUNCTUATION \
                and isinstance(ultima, Space):
                    sequence.pop()
            sequence.append(item)
        else:
            if depth > 0:
                return (offset, None)

        while len(sequence) > 0 and isinstance(sequence[0], Space):
            sequence.pop(0)
        while len(sequence) > 0 and isinstance(sequence[-1], Space):
            sequence.pop()

        if len(sequence) == 0:
            result = Empty()
            # result = Phantom(Atom('mo', '\u2062'))
            # result = None
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
