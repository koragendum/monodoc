import re

INDENTSIZE = 1.5

def midrender(text):
    text = text.replace('P–V', '<span class="sc bl">pv</span>')
    text = text.replace('Cut', '<span class="rd">Cut</span>')
    text = text.replace('All', '<span class="gr">All</span>')
    return text


def postrender(text):
    text = text.replace('⟨', '<span class="fc">⟨</span>')
    text = text.replace('⟩', '<span class="fc">⟩</span>')
    for s in ('F', 'Z', 'S'):
        text = text.replace(f'<span class="var">{s}</span><span class="var">α</span>', f'<span class="var sb mv">{s}</span><span class="var mv">α</span>')
        text = text.replace(f'<span class="var">{s}</span><span class="var">β</span>', f'<span class="var sb oc">{s}</span><span class="var oc">β</span>')
        text = text.replace(f'<span class="var">{s}</span>',                           f'<span class="var sb">{s}</span>'                                )
    text = text.replace('<span class="var">α</span>', '<span class="var mv">α</span>')
    text = text.replace('<span class="var">β</span>', '<span class="var oc">β</span>')
    text = text.replace('<span class="sc">r</span>',  '<span class="sc az">r</span>')
    text = text.replace('<span class="var">c</span>', '<span class="var az">c</span>')
    return text


def blockclass(inner, lang):
    if lang == 'box':    return 'box-drawing'
    if lang == 'pseudo': return 'pseudocode'
    return None


keyword   = re.compile(r'\$([a-zA-Z-]+)')
flow      = re.compile(r'@([a-zA-Z-]+)')
function  = re.compile(r"%([+−×/<>≤≥=≠]|[a-zA-Z][a-zA-Z'-]*)")
numconst  = re.compile(r'#([0-9]+)')
wordconst = re.compile(r"#([a-zA-Z][a-zA-Z0-9'-]*)")
comment   = re.compile(r'([※◊].*)$', re.MULTILINE)
annot     = re.compile(r'(?<= )([a-zαβ][ ₀₁₂][+−]\d[=↓↑]?|[+−]\d[=↓↑])')

def codeblock(inner, lang):
    if lang == 'pseudo':
        # $keyword      define end mutable
        # @flow         if end then else for in break next return
        # %function
        # #constant
        inner =   keyword.sub(r'<span class="keyword">\1</span>',       inner)
        inner =      flow.sub(r'<span class="flow">\1</span>',          inner)
        inner =  function.sub(r'<span class="function">\1</span>',      inner)
        inner =  numconst.sub(r'<span class="numeric-const">\1</span>', inner)
        inner = wordconst.sub(r'<span class="textual-const">\1</span>', inner)
        inner =   comment.sub(r'<span class="comment">\1</span>',       inner)
        return inner
    inner = inner.replace('P–V',    '<span class="bl">P−V</span>')
    inner = inner.replace('Cut',    '<span class="rd">Cut</span>')
    inner = inner.replace('All',    '<span class="gr">All</span>')
    inner = inner.replace('Skp',    '<span class="rd dim">Skp</span>')
    inner = inner.replace(' C',     ' <span class="rd">C</span>')
    inner = inner.replace('Z+F',    '<span class="rl"><span class="sb lc">Z</span>+<span class="sb tl">F</span></span>')
    inner = inner.replace('F ',     '<span class="rl sb tl">F</span> ')
    inner = inner.replace(' Z',     ' <span class="rl sb lc">Z</span>')
    inner = inner.replace('before', '<span class="lt">before</span>')
    inner = inner.replace('after',  '<span class="lt">after</span>')
    inner = annot.sub(r'<span class="hi">\1</span>', inner)
    return inner
