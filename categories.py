# ELEMENTS - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

ELEMENTS = {
    # HTML
    'a', 'abbr', 'address', 'area', 'article', 'aside', 'audio', 'b', 'base',
    'bdi', 'bdo', 'blockquote', 'body', 'br', 'button', 'canvas', 'caption',
    'cite', 'code', 'col', 'colgroup', 'data', 'datalist', 'dd', 'del',
    'details', 'dfn', 'dialog', 'div', 'dl', 'dt', 'em', 'embed',
    'fencedframe', 'fieldset', 'figcaption', 'figure', 'footer', 'form', 'h1',
    'h2', 'h3', 'h4', 'h5', 'h6', 'head', 'header', 'hgroup', 'hr', 'html',
    'i', 'iframe', 'img', 'input', 'ins', 'kbd', 'label', 'legend', 'li',
    'link', 'main', 'map', 'mark', 'menu', 'meta', 'meter', 'nav', 'noscript',
    'object', 'ol', 'optgroup', 'option', 'output', 'p', 'picture', 'portal',
    'pre', 'progress', 'q', 'rp', 'rt', 'ruby', 's', 'samp', 'script',
    'search', 'section', 'select', 'slot', 'small', 'source', 'span', 'strong',
    'style', 'sub', 'summary', 'sup', 'svg', 'table', 'tbody', 'td',
    'template', 'textarea', 'tfoot', 'th', 'thead', 'time', 'title', 'tr',
    'track', 'u', 'ul', 'var', 'video', 'wbr',
    # MathML
    'math', 'mfrac', 'mi', 'mn', 'mo', 'mover', 'mroot', 'mrow', 'mspace',
    'msqrt', 'msub', 'msubsup', 'msup', 'mtext', 'munder', 'munderover',
    # Extensions (metadata)
    'include', 'module', 'python',
    # Extensions (non-phrasing)
    'block-code', 'block-indent', 'block-math', 'block-note', 'block-quote',
    # Extensions (phrasing)
    'em-sp', 'en-sp', 'esc-i', 'extra-bold', 'hi-group', 'inline-math',
    'inline-note', 'margin-note', 'no-break', 'semi-bold', 'small-caps',
    'sp-3', 'sp-4', 'sp-5', 'sp-6', 'sp-7', 'sp-8'
}

VOID = {
    # HTML
    'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta',
    'source', 'track', 'wbr',
    # MathML
    'mspace',
    # Extensions (metadata)
    'include', 'module'
}

# CATEGORIES - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

METADATA = {
    # HTML
    'base', 'link', 'meta', 'noscript', 'script', 'style', 'template', 'title',
}

# The following are also flow content:
#   plain text
#   an <area> element if it is a descendent of a <map> element
#   a <link> or <meta> element if it has the itemprop attribute
FLOW = {
    # HTML
    'a', 'abbr', 'address', 'area', 'article', 'aside', 'audio', 'b', 'bdi',
    'bdo', 'blockquote', 'br', 'button', 'canvas', 'cite', 'code', 'data',
    'datalist', 'del', 'details', 'dfn', 'dialog', 'div', 'dl', 'em', 'embed',
    'fieldset', 'figure', 'footer', 'form', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'header', 'hgroup', 'hr', 'i', 'iframe', 'img', 'input', 'ins', 'kbd',
    'label', 'main', 'map', 'mark', 'menu', 'meter', 'nav', 'noscript',
    'object', 'ol', 'output', 'p', 'picture', 'pre', 'progress', 'q', 'ruby',
    's', 'samp', 'script', 'search', 'section', 'select', 'slot', 'small',
    'span', 'strong', 'sub', 'sup', 'svg', 'table', 'template', 'textarea',
    'time', 'u', 'ul', 'var', 'video', 'wbr',
    # MathML
    'math', 'mfrac', 'mi', 'mn', 'mo', 'mover', 'mroot', 'mrow', 'mspace',
    'msqrt', 'msub', 'msubsup', 'msup', 'mtext', 'munder', 'munderover',
    # Extensions (non-phrasing)
    'block-code', 'block-indent', 'block-math', 'block-note', 'block-quote',
    # Extensions (phrasing)
    'em-sp', 'en-sp', 'esc-i', 'extra-bold', 'hi-group', 'inline-math',
    'inline-note', 'margin-note', 'no-break', 'semi-bold', 'small-caps',
    'sp-3', 'sp-4', 'sp-5', 'sp-6', 'sp-7', 'sp-8'
}

SECTIONING = {
    # HTML
    'article', 'aside', 'nav', 'section'
}

HEADING = {
    # HTML
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'hgroup'
}

# The following are also phrasing content:
#   plain text
#   an <a>, <map>, <del>, or <ins> element if it contains only phrasing content
#   an <area> element if it is a descendent of a <map> element
#   a <link> or <meta> element if it has the itemprop attribute
PHRASING = {
    # HTML
    'a', 'abbr', 'area', 'audio', 'b', 'bdi', 'bdo', 'br', 'button', 'canvas',
    'cite', 'code', 'data', 'datalist', 'del', 'dfn', 'em', 'embed', 'i',
    'iframe', 'img', 'input', 'ins', 'kbd', 'label', 'map', 'mark', 'meter',
    'noscript', 'object', 'output', 'picture', 'progress', 'q', 'ruby', 's',
    'samp', 'script', 'select', 'slot', 'small', 'span', 'strong', 'sub',
    'sup', 'svg', 'template', 'textarea', 'time', 'u', 'var', 'video', 'wbr',
    # MathML
    'math', 'mfrac', 'mi', 'mn', 'mo', 'mover', 'mroot', 'mrow', 'mspace',
    'msqrt', 'msub', 'msubsup', 'msup', 'mtext', 'munder', 'munderover',
    # Extensions (phrasing)
    'em-sp', 'en-sp', 'esc-i', 'extra-bold', 'hi-group', 'inline-math',
    'inline-note', 'margin-note', 'no-break', 'semi-bold', 'small-caps',
    'sp-3', 'sp-4', 'sp-5', 'sp-6', 'sp-7', 'sp-8'
}

# The following are also palpable content:
#   plain text that is not inter-element whitespace
#   an <audio> element if the controls attribute is present
#   a <dl> element if its children include at least one name–value group
#   an <input> element if the type attribute is not in the hidden state
#   an <ol> or <ul> element if its children include at least one <li> element
PALPABLE = {
    # HTML
    'a', 'abbr', 'address', 'article', 'aside', 'audio', 'b', 'bdi', 'bdo',
    'blockquote', 'button', 'canvas', 'cite', 'code', 'data', 'del', 'details',
    'dfn', 'div', 'dl', 'em', 'embed', 'fieldset', 'footer', 'figure', 'form',
    'iframe', 'img', 'input', 'ins', 'kbd', 'label', 'main', 'map', 'mark',
    'meter', 'nav', 'object', 'ol', 'p', 'picture', 'pre', 'progress', 'q',
    'ruby', 's', 'samp', 'search', 'section', 'select', 'small', 'span',
    'strong', 'sub', 'sup', 'svg', 'table', 'textarea', 'time', 'u', 'ul',
    'var', 'video',
    # MathML
    'math', 'mfrac', 'mi', 'mn', 'mo', 'mover', 'mroot', 'mrow', 'msqrt',
    'msub', 'msubsup', 'msup', 'mtext', 'munder', 'munderover',
    # Extensions (non-phrasing)
    'block-code', 'block-indent', 'block-math', 'block-note', 'block-quote',
    # Extensions (phrasing)
    'esc-i', 'extra-bold', 'hi-group', 'inline-math', 'inline-note',
    'margin-note', 'no-break', 'semi-bold', 'small-caps'
}

# OUTER DISPLAY TYPE - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

NODISPLAY = {
    # HTML
    'area', 'base', 'datalist', 'head', 'link', 'meta', 'noscript', 'rp',
    'script', 'source', 'style', 'template', 'title', 'track',
    # Extensions (metadata)
    'module', 'python'
}

BLOCK = {
    # HTML
    'address', 'article', 'aside', 'blockquote', 'body', 'caption', 'col',
    'colgroup', 'dd', 'details', 'dialog', 'div', 'dl', 'dt', 'fieldset',
    'figcaption', 'figure', 'footer', 'form', 'h1', 'h2', 'h3', 'h4', 'h5',
    'h6', 'header', 'hgroup', 'hr', 'html', 'legend', 'li', 'main', 'menu',
    'nav', 'ol', 'p', 'pre', 'search', 'section', 'summary', 'table', 'tbody',
    'td', 'tfoot', 'th', 'thead', 'tr', 'ul',
    # Extensions (non-phrasing)
    'block-code', 'block-indent', 'block-math', 'block-note', 'block-quote'
}

# The MathML elements are not categorized as block or inline.

INLINE = {
    'a', 'abbr', 'audio', 'b', 'bdi', 'bdo', 'br', 'button', 'canvas', 'cite',
    'code', 'data', 'del', 'dfn', 'em', 'embed', 'fencedframe', 'i', 'iframe',
    'img', 'input', 'ins', 'kbd', 'label', 'map', 'mark', 'meter', 'object',
    'optgroup', 'option', 'output', 'picture', 'portal', 'progress', 'q', 'rt',
    'ruby', 's', 'samp', 'select', 'slot', 'small', 'span', 'strong', 'sub',
    'sup', 'svg', 'textarea', 'time', 'u', 'var', 'video', 'wbr',
    # Extensions (metadata)
    'include',
    # Extensions (phrasing)
    'em-sp', 'en-sp', 'esc-i', 'extra-bold', 'hi-group', 'inline-math',
    'inline-note', 'margin-note', 'no-break', 'semi-bold', 'small-caps',
    'sp-3', 'sp-4', 'sp-5', 'sp-6', 'sp-7', 'sp-8'
}


# This is a subset of INLINE. It does not include:
#   audio br button canvas embed fencedframe iframe img input label
#   map meter object optgroup option output picture portal progress
#   rt select svg textarea video
FORMATTING = {
    # HTML
    'a', 'abbr', 'b', 'bdi', 'bdo', 'cite', 'code', 'data', 'del', 'dfn', 'em',
    'i', 'ins', 'kbd', 'mark', 'q', 'ruby', 's', 'samp', 'slot', 'small',
    'span', 'strong', 'sub', 'sup', 'time', 'u', 'var', 'wbr',
    # Extensions (metadata)
    'include',
    # Extensions (phrasing)
    'em-sp', 'en-sp', 'esc-i', 'extra-bold', 'hi-group', 'inline-math',
    'inline-note', 'margin-note', 'no-break', 'semi-bold', 'small-caps',
    'sp-3', 'sp-4', 'sp-5', 'sp-6', 'sp-7', 'sp-8',
}
