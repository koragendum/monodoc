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
    'include'    , 'python'     ,
}

SINGLELINE = {
    # HTML - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    'title'      , 'address'    , 'h1'         , 'h2'         , 'h3'         ,
    'h4'         , 'h5'         , 'h6'         , 'dd'         , 'dt'         ,
    'figcaption' , 'li'         , 'p'          , 'a'          , 'abbr'       ,
    'b'          , 'bdi'        , 'bdo'        , 'cite'       , 'code'       ,
    'data'       , 'dfn'        , 'em'         , 'i'          , 'kbd'        ,
    'mark'       , 'q'          , 'rp'         , 'rt'         , 'ruby'       ,
    's'          , 'samp'       , 'small'      , 'span'       , 'strong'     ,
    'sub'        , 'sup'        , 'time'       , 'u'          , 'var'        ,
    'audio'      , 'track'      , 'video'      , 'del'        , 'ins'        ,
    'caption'    , 'td'         , 'th'         , 'button'     , 'label'      ,
    'legend'     , 'meter'      , 'option'     , 'output'     , 'progress'   ,
    'summary'    , 'slot'       ,
    # MathML - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    'mi'         , 'mn'         , 'mo'         , 'mtext'      ,
}

VOID = {
    # HTML - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    'area'       , 'base'       , 'br'         , 'col'        , 'embed'      ,
    'hr'         , 'img'        , 'input'      , 'link'       , 'meta'       ,
    'source'     , 'track'      , 'wbr'        ,
    # MathML - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    'mspace'     ,
    # Extensions - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    'include'    ,
}


INDENT = '  '

class HtmlElement:
    def __init__(self, element, *inner, **attrs):
        self.element = element
        self.inner = list(inner)
        if 'kind' in attrs:
            assert 'class' not in attrs
            attrs['class'] = attrs.pop('kind')
        self.attrs = attrs
        self._size = None

    def size(self):
        # Roughly the number of characters in
        #   the rendered output divided by four.
        if self._size is None:
            self._size = (
                (1 if self.element in VOID else 2)
                + len(self.attrs) * 2
                + sum(
                    item.size() if isinstance(item, HtmlElement)
                        else len(item) // 4
                    for item in self.inner
                )
            )
        return self._size

    def push(self, *items):
        self.inner.extend(items)
        self._size = None
        return self

    def render(self, buffer, depth=0):
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
        multiline = self.element not in SINGLELINE and self.size() > 6
        if multiline: buffer.append('\n')
        margin = INDENT * (depth + 1)
        for item in self.inner:
            if multiline:
                buffer.append(margin)
            if isinstance(item, HtmlElement):
                item.render(buffer, depth + 1 if multiline else depth)
            elif isinstance(item, str):
                buffer.append(item)
            else:
                raise TypeError('not an instance of str or HtmlElement: '
                    f'{item} has type {type(item)}')
            if multiline: buffer.append('\n')
        if multiline and depth > 0: buffer.append(INDENT * depth)
        buffer.append(f'</{self.element}>')
