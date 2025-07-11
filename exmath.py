import re

PERMALINK = '§'

score = re.compile(r'(2|1½|1|½|0)–(2|1½|1|½|0)')

def scorereplacement(match):
    fst, snd = match.group(1), match.group(2)
    lhs = '&hairsp;' if fst[-1] == '½' else ''
    rhs = '&hairsp;' if snd[0] == '½' else ''
    return f'<span class="score">{fst}{lhs}–{rhs}{snd}</span>'

abbrev = re.compile(r'#([12345])')

def prerender(text):
    text = score.sub(scorereplacement, text)
    text = abbrev.sub(r'''"<span class='score'>\1</span>"''', text)
    return text

def postrender(text):
    text = text.replace('”,', '”<span style="margin-left: -0.25em;">.</span>')
    text = text.replace('”.', '”<span style="margin-left: -0.25em;">.</span>')
    return text

def blockclass(inner, lang):
    if lang == 'pseudo': return 'pseudocode'
    return None

keyword   = re.compile(r'\$([a-zA-Z-]+)')
flow      = re.compile(r'@([a-zA-Z-]+)')
typ       = re.compile(r'\^([a-zA-Zα-ωΑ-Ω][a-zA-Zα-ωΑ-Ω0-9-]*)')
function  = re.compile(r"%([+−×/<>≤≥=≠]|[a-zA-Zα-ωΑ-Ω][a-zA-Zα-ωΑ-Ω0-9'-]*)")
numconst  = re.compile(r'#([0-9]+)')
wordconst = re.compile(r"#([a-zA-Zα-ωΑ-Ω][a-zA-Zα-ωΑ-Ω0-9'-]*)")
comment   = re.compile(r'([※◊].*)$', re.MULTILINE)

def codeblock(inner, lang):
    if lang != 'pseudo': return inner
    # $keyword      define end mutable
    # @flow         if end then else for in break next return
    # %function
    # #constant
    inner =   keyword.sub(r'<span class="keyword">\1</span>',       inner)
    inner =      flow.sub(r'<span class="flow">\1</span>',          inner)
    inner =       typ.sub(r'<span class="type">\1</span>',          inner)
    inner =  function.sub(r'<span class="function">\1</span>',      inner)
    inner =  numconst.sub(r'<span class="numeric-const">\1</span>', inner)
    inner = wordconst.sub(r'<span class="textual-const">\1</span>', inner)
    inner =   comment.sub(r'<span class="comment">\1</span>',       inner)
    return inner
