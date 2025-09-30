import re

ELEMENTS = {
    # HTML - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    'html'       , 'base'       , 'head'       , 'link'       , 'meta'       ,
    'style'      , 'title'      , 'body'       , 'address'    , 'article'    ,
    'aside'      , 'footer'     , 'header'     , 'h1'         , 'h2'         ,
    'h3'         , 'h4'         , 'h5'         , 'h6'         , 'hgroup'     ,
    'main'       , 'nav'        , 'section'    , 'search'     , 'blockquote' ,
    'dd'         , 'div'        , 'dl'         , 'dt'         , 'figcaption' ,
    'figure'     , 'hr'         , 'li'         , 'menu'       , 'ol'         ,
    'p'          , 'pre'        , 'ul'         , 'a'          , 'abbr'       ,
    'b'          , 'bdi'        , 'bdo'        , 'br'         , 'cite'       ,
    'code'       , 'data'       , 'dfn'        , 'em'         , 'i'          ,
    'kbd'        , 'mark'       , 'q'          , 'rp'         , 'rt'         ,
    'ruby'       , 's'          , 'samp'       , 'small'      , 'span'       ,
    'strong'     , 'sub'        , 'sup'        , 'time'       , 'u'          ,
    'var'        , 'wbr'        , 'area'       , 'audio'      , 'img'        ,
    'map'        , 'track'      , 'video'      , 'embed'      , 'fencedframe',
    'iframe'     , 'object'     , 'picture'    , 'portal'     , 'source'     ,
    'svg'        , 'math'       , 'canvas'     , 'noscript'   , 'script'     ,
    'del'        , 'ins'        , 'caption'    , 'col'        , 'colgroup'   ,
    'table'      , 'tbody'      , 'td'         , 'tfoot'      , 'th'         ,
    'thead'      , 'tr'         , 'button'     , 'datalist'   , 'fieldset'   ,
    'form'       , 'input'      , 'label'      , 'legend'     , 'meter'      ,
    'optgroup'   , 'option'     , 'output'     , 'progress'   , 'select'     ,
    'textarea'   , 'details'    , 'dialog'     , 'summary'    , 'slot'       ,
    'template'   ,
    # MathML - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    'math'       , 'mfrac'      , 'mi'         , 'mn'         , 'mo'         ,
    'mover'      , 'mroot'      , 'mrow'       , 'mspace'     , 'msqrt'      ,
    'msub'       , 'msubsup'    , 'msup'       , 'mtext'      , 'munder'     ,
    'munderover' ,
    # Extensions - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    'include'    , 'module'     , 'python'     ,
    'block-note' , 'block-quote', 'block-math' , 'block-code' ,
    'block-indent'              ,
    'esc-i'      , 'em-sp'      , 'en-sp'      , 'sp-3'       , 'sp-4'       ,
    'sp-5'       , 'sp-6'       , 'sp-7'       , 'sp-8'       , 'small-caps' ,
    'inline-math', 'margin-note', 'inline-note', 'no-break'   , 'hi-group'   ,
    'hybridoc-error'
}

VOID = {
    # HTML - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    'area'       , 'base'       , 'br'         , 'col'        , 'embed'      ,
    'hr'         , 'img'        , 'input'      , 'link'       , 'meta'       ,
    'source'     , 'track'      , 'wbr'        ,
    # MathML - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    'mspace'     ,
    # Extensions - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    'include'    , 'module'     ,
}


INDENT = 2

# Ordinarily, linebreaks may be inserted between the nodes of an element.
#   This is suppressed for these elements.
SINGLELINE = {
    # HTML - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    'a'          , 'abbr'       , 'address'    , 'audio'      , 'b'          ,
    'bdi'        , 'bdo'        , 'button'     , 'caption'    , 'cite'       ,
    'code'       , 'data'       , 'del'        , 'dd'         , 'dfn'        ,
    'dt'         , 'em'         , 'figcaption' , 'h1'         , 'h2'         ,
    'h3'         , 'h4'         , 'h5'         , 'h6'         , 'i'          ,
    'ins'        , 'kbd'        , 'label'      , 'legend'     , 'li'         ,
    'mark'       , 'meter'      , 'option'     , 'output'     , 'progress'   ,
    'q'          , 'rp'         , 'rt'         , 'ruby'       , 's'          ,
    'samp'       , 'slot'       , 'small'      , 'span'       , 'strong'     ,
    'sub'        , 'summary'    , 'sup'        , 'td'         , 'th'         ,
    'time'       , 'title'      , 'track'      , 'u'          , 'var'        ,
    'video'      ,
    # MathML - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    'mi'         , 'mn'         , 'mo'         , 'mtext'      ,
    # Extensions - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    'esc-i'      , 'em-sp'      , 'en-sp'      , 'sp-3'       , 'sp-4'       ,
    'sp-5'       , 'sp-6'       , 'sp-7'       , 'sp-8'       , 'small-caps' ,
    'inline-math', 'margin-note', 'inline-note', 'no-break'   , 'hi-group'   ,
    'hybridoc-error'
}

# Ordinarily, leading or trailing whitespace within an element may be stripped
#   or added, and whitespace preceding or following an element may be stripped
#   or added. This is suppressed for these elements.
# This should be a subset of SINGLELINE.
RESPECTING = {
    # HTML - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    'a'          , 'abbr'       , 'b'          , 'bdi'        , 'bdo'        ,
    'cite'       , 'code'       , 'data'       , 'del'        , 'dfn'        ,
    'em'         , 'i'          , 'ins'        , 'kbd'        , 'mark'       ,
    'q'          , 'ruby'       , 's'          , 'samp'       , 'slot'       ,
    'small'      , 'span'       , 'strong'     , 'sub'        , 'sup'        ,
    'time'       , 'u'          , 'var'        , 'wbr'        ,
    # Extensions - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    'esc-i'      , 'em-sp'      , 'en-sp'      , 'sp-3'       , 'sp-4'       ,
    'sp-5'       , 'sp-6'       , 'sp-7'       , 'sp-8'       , 'small-caps' ,
    'inline-math', 'margin-note', 'inline-note', 'no-break'   , 'hi-group'   ,
    'hybridoc-error'
}

COMPACTSP = re.compile(r'[ \t\r\n]+')

class HtmlElement:
    def __init__(self, element, *inner, **attrs):
        self.element = element
        self.inner = list(inner)
        if 'kind' in attrs:
            assert 'class' not in attrs
            attrs['class'] = attrs.pop('kind')
        if 'name' in attrs:
            assert 'id' not in attrs
            attrs['id'] = attrs.pop('name')
        self.attrs = attrs
        self._compact = False
        self._pruned = False
        self._size = None

    def push(self, *items):
        self.inner.extend(items)
        self._size = None
        self._compact = False
        return self

    def _check(self):
        for item in self.inner:
            if isinstance(item, (str, HtmlElement)):
                continue
            raise TypeError('not an instance of str or HtmlElement: '
                f'{item} has type {type(item)}')

    def compact(self):
        if self._compact:
            return

        prev = None
        for index, item in enumerate(self.inner):
            if isinstance(item, str) and isinstance(prev, str):
                joined = prev + item
                self.inner[index-1] = None
                self.inner[index] = joined
                prev = joined
            else:
                prev = item

        if self.element == 'pre':
            self.inner = [item for item in self.inner if item is not None]
        else:
            self.inner = [
                COMPACTSP.sub(' ', item) if isinstance(item, str) else item
                for item in self.inner
                if item is not None
            ]

        self._size = None
        self._compact = True

    def prune(self):
        if self._pruned:
            return

        for index, item in enumerate(self.inner):
            if isinstance(item, HtmlElement):
                item.prune()
                if item.element == 'p' and not item.inner:
                    self.inner[index] = None

        self.inner = [item for item in self.inner if item is not None]

        self.compact()

        if self.element == 'p' and self.inner == [' ']:
            self.inner.clear()

        self._size = None
        self._pruned = True

    def size(self):
        # Roughly the number of characters in the rendered output.
        if self._size is None:
            self._size = (
                (4 if self.element in VOID else 8)
                + len(self.attrs) * 12
                + sum(
                    item.size() if isinstance(item, HtmlElement)
                        else len(item)
                    for item in self.inner
                )
            )
        return self._size

    def render(self, buffer, depth=0, verbatim=False):
        # “In HTML, a void element must not have an end tag. In contrast, SVG
        #  or MathML elements that cannot have any child nodes may use an end
        #  tag instead of XML self-closing-tag syntax in their start tag.”
        # “A Self-closing tag is a special form of start tag with a slash
        #  immediately before the closing right angle bracket. These indicate
        #  that the element is to be closed immediately, and has no content.
        #  Where this syntax is permitted and used, the end tag must be omitted.
        #  In HTML, the use of this syntax is restricted to void elements and
        #  foreign elements. If it is used for other elements, it is treated
        #  as a start tag.”
        # “If the element is one of the void elements, or if the element
        #  is a foreign element, then there may be a single U+002F SOLIDUS
        #  character. This character has no effect on void elements, but on
        #  foreign elements it marks the start tag as self-closing.”

        fields = [self.element]
        for key in sorted(self.attrs):
            value = self.attrs[key]
            fields.append(key if value is None else f'{key}="{value}"')

        if self.element in VOID:
            assert not self.inner
            # XHTML requires U+002F whereas HTML 5 does not.
            ultima = '/' if self.element == 'mspace' else ''
            buffer.append(f'<{" ".join(fields)}{ultima}>')
            return

        buffer.append(f'<{" ".join(fields)}>')
        if not self.inner:
            buffer.append(f'</{self.element}>')
            return

        if verbatim:
            for item in self.inner:
                if isinstance(item, str):
                    buffer.append(item)
                else:
                    item.render(buffer, depth, verbatim=True)
            buffer.append(f'</{self.element}>')
            return

        L = len(self.inner) - 1

        if self.element == 'pre':
            buffer.append('\n')
            for index, item in enumerate(self.inner):
                if isinstance(item, str):
                    if index == 0:
                        item = item.lstrip('\n')
                    if index == L:
                        item = item.rstrip('\n')
                    buffer.append(item)
                else:
                    item.render(buffer, depth, verbatim=True)
            buffer.append(f'</{self.element}>')
            return

        multiline = self.element not in SINGLELINE and self.size() > 32
        flexible = self.element not in RESPECTING
        margin = ' ' * (INDENT * (depth + 1))

        def flexible_item(index):
            return self.inner[index].element not in RESPECTING

        def prev_admissable(index):
            item = self.inner[index]
            return item.endswith(' ') if isinstance(item, str) \
                else item.element not in RESPECTING

        def post_admissable(index):
            item = self.inner[index]
            return item.startswith(' ') if isinstance(item, str) \
                else item.element not in RESPECTING

        # TODO prefer to place the first item on the same line as the opening
        #     tag if it’s a string
        #   and place the closing on the same line as the last item if it’s
        #     a string
        #   especially (only?) in paragraphs

        for index, item in enumerate(self.inner):
            if isinstance(item, str):
                # TODO line breaks for long strings
                flex_leading = (index == 0 and flexible) \
                    or (index > 0 and flexible_item(index - 1))
                flex_trailing = (index == L and flexible) \
                    or (index < L and flexible_item(index + 1))
                space_leading = item.startswith(' ')
                if flex_leading or (multiline and space_leading):
                    item = item.removeprefix(' ')
                if flex_trailing or (multiline and item.endswith(' ')):
                    item = item.removesuffix(' ')
                if item:
                    if multiline and (flex_leading or space_leading):
                        buffer.append('\n')
                        buffer.append(margin)
                    buffer.append(item)
            else:
                flex_leading = (index == 0 and flexible) \
                    or (index > 0 and prev_admissable(index - 1))
                flex_trailing = (index == L and flexible) \
                    or (index < L and post_admissable(index + 1))
                newline = multiline and flex_leading
                if newline:
                    buffer.append('\n')
                    buffer.append(margin)
                item.render(buffer, depth + 1 if newline else depth)

        if multiline and (flexible or prev_admissable(L)):
            buffer.append('\n')
            if depth > 0:
                buffer.append(' ' * (INDENT * depth))

        buffer.append(f'</{self.element}>')


def render(element, depth=0):
    buffer = []
    element.render(buffer, depth)
    return ''.join(buffer)


def _extant(elements, classes, node):
    elements.add(node.element)
    if 'class' in node.attrs:
        classes.update(node.attrs['class'])
    for item in node.inner:
        if isinstance(item, HtmlElement):
            _extant(elements, classes, item)

def extant(node):
    elements, classes = set(), set()
    _extant(elements, classes, node)
    return (elements, classes)


def replace(
    element, expr, repl,
    origin=None, exempt=None,
    final=False, recurse=False
):
    # When final is True, do not restart at origin nodes in exempt subtrees.
    # When recurse is True, examine newly created nodes.
    def _replace(elem, active):
        if (not active) and origin is not None and origin(elem):
            active = True
        if (active or final) and exempt is not None and exempt(elem):
            if final: return
            active = False
        inner = elem.inner
        if active:
            expanded = []
            modified = False

            if isinstance(expr, str):
                for item in inner:
                    if isinstance(item, str) and expr in item:
                        fragments = iter(item.split(expr))
                        expanded.append(next(fragments))
                        for fragment in fragments:
                            expanded.append(repl(expr))
                            expanded.append(fragment)
                        modified = True
                    else:
                        expanded.append(item)

            if isinstance(expr, re.Pattern):
                for item in inner:
                    if isinstance(item, str):
                        length = len(item)
                        offset = 0
                        while offset < length:
                            match = expr.search(item, offset)
                            if match is None:
                                expanded.append(item[offset:])
                                break
                            expanded.append(item[offset:match.start()])
                            expanded.append(repl(match))
                            offset = match.end()
                            modified = True
                    else:
                        expanded.append(item)

            if modified:
                elem.inner = expanded
                elem._size = None
                elem._compact = False

        for item in (elem.inner if recurse else inner):
            if isinstance(item, HtmlElement):
                _replace(item, active)

    _replace(element, origin is None)
