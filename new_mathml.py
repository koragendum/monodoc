import re
from html import HtmlElement

#  x        variable (italic by default)
#  log      function (nonitalic by default)
#
#  r{}      nonitalic
#  it{}     italic
#  sb{}     semibold
#  b{}      bold
#  sc{}     small capitals
#  cal{}    calligraphic
#  pen{}    alternate calligraphic
#  blk{}    blackletter
#  dbl{}    doublestruck
#
#  "fn"     escape

#   style: nonitalic, italic
#  weight: book, semibold, bold
# variant: small capital, calligraphic, blackletter

# setmath('abc', 'it{abc}')
# setmath('@a', 'cal{a}')
# setmath('@_', 'cal{_}')

# subscript
# superscript
# under
# over
# fraction
# stack
# square root
# root

# Block vs Inline
#
#   <math display="block">    sets  math-style: normal;
#   <math display="inline">   sets  math-style: compact;
#
#   <* displaystyle="true">   sets  math-style: normal;
#   <* displaystyle="false">  sets  math-style: compact;
#
#   <mo movablelimits="true"> moves under/over to sub/sup
#                               when math-style is compact
#
#   <mo largeop="true">       draws the operator larger
#                               when math-style is normal
#
# Depth
#
#   <* scriptlevel="+1">  vs  math-depth: add(1);

VARIANTS = {
    # calligraphic, bold caligraphic,
    #   blackletter, bold blackletter,
    #   doublestruck
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
        self.kind    = kind     # "mi", "mn", "mo", "ms", "mtext"
        self.inner   = inner

        # Operators
        self.arity   = None     # None, 'prefix', 'infix', 'postfix'

        # Identifiers
        self.italic  = None     # None, False, True
        self.weight  = None     # None, "semi", "bold"
        self.variant = None     # None, "scp", "cal", "alt", "blk", "dbl"

    def html(self, inline=False, scriptlevel=0, fraclevel=0):
        inner  = self.inner
        weight = self.weight

        attrs   = {}
        classes = []

        # Operators
        #   fence="true"|"false"
        #   form="prefix"|"infix"|"postfix"
        #   largeop="true"|"false"
        #     (the operator should be drawn larger when math-style is normal)
        #   moveablelimits="true"|"false"
        #     (move under/over to sub/sup when math-style is compact)
        #   separator="true"|"false"
        #   stretchy="true"|"false"
        #   symmetric="true"|"false"
        #   lspace=...
        #   rspace=...
        if self.kind == 'mo':
            pass

        # Identifiers
        #   mathvariant="normal"
        #     (sets text-transform to none rather than math-auto)
        if self.kind == 'mi':
            pass

        if weight == 'semi': classes.append('sb')
        if weight == 'bold': classes.append('bf')

        if classes:
            attrs['class'] = " ".join(classes)

        return HtmlElement(self.kind, inner, **attrs)

# mi {
#   text-transform: math-auto;
# }
#
# mi[mathvariant="normal"] {
#   text-transform: none;
# }

class Empty:
    def __init__(self):
        pass

    def html(self, inline=False, scriptlevel=0, fraclevel=0):
        pass

class Space:
    def __init__(self):
        pass

    def html(self, inline=False, scriptlevel=0, fraclevel=0):
        pass

class Boxed:
    def __init__(self):
        pass

    def html(self, inline=False, scriptlevel=0, fraclevel=0):
        pass

class Row:
    def __init__(self):
        pass

    def html(self, inline=False, scriptlevel=0, fraclevel=0):
        pass

class Sqrt:
    def __init__(self):
        pass

    def html(self, inline=False, scriptlevel=0, fraclevel=0):
        pass

class Root:
    def __init__(self):
        pass

    def html(self, inline=False, scriptlevel=0, fraclevel=0):
        pass

class Frac:
    def __init__(self):
        pass

    def html(self, inline=False, scriptlevel=0, fraclevel=0):
        pass

class Struct:
    def __init__(self):
        pass

    def html(self, inline=False, scriptlevel=0, fraclevel=0):
        pass
