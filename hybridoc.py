#! /usr/bin/python

import re

from html    import ELEMENTS, VOID, HtmlElement
from mathml  import parse as parse_math
from inspect import currentframe, getframeinfo
from re      import Match as MatchObject
from typing  import Optional


ATTRKEY = re.compile('[a-zA-Z]+(?:-[a-zA-Z]+)*')
ATTRBRK = re.compile('[\\s=\'"]')

def parse_attributes(text : str) -> Optional[dict[str, str]]:
    # We assume there is no leading whitespace,
    #   and maintain that property as an invariant.
    if not text:
        return {}
    parts = []
    while True:
        match = ATTRBRK.search(text)
        if match is None:
            parts.append(text)
            break
        item = text[:match.start()]
        if item:
            parts.append(item)
        char = match[0]
        if char == '=':
            parts.append(None)
            text = text[match.end():].lstrip()
            if text: continue
            break
        if char == '"' or char == "'":
            left = match.end()
            try: right = text.index(char, left)
            except ValueError: return None
            parts.append(text[left:right])
            text = text[right+1:].lstrip()
            if text: continue
            break
        text = text[match.end():].lstrip()
        if not text:
            break
    attrs = {}
    index = 0
    length = len(parts)
    while index < length:
        key = parts[index]
        if key is None: return None # “= ...”
        if not ATTRKEY.fullmatch(key): return None
        if index + 2 < length and parts[index+1] is None:
            value = parts[index+2]
            if value is None: return None # “key = = ...”
            attrs[key] = value
            index += 3
        else:
            attrs[key] = None
            index += 1
    return attrs


def parse_error(text) -> HtmlElement:
    kwargs = {
        'class': 'hybridoc-error',
        'line-number': getframeinfo(currentframe().f_back).lineno
    }
    if isinstance(text, str):
        text = text.replace('<', '&lt;').replace('>', '&gt;')
        return HtmlElement('span', text, **kwargs)
    else:
        return HtmlElement('span', *text, **kwargs)


INITIAL  = re.compile('[' + re.escape("$%&'*<@^_`{}\u2020\u203B") + ']')
NONSPACE = re.compile('[^ \t\n\r]')

ELEMINI = re.compile('[a-z]')
TAGBRK  = re.compile('[>"\']')

WORD    = re.compile('[a-zA-Z]+(?:-[a-zA-Z]+)*')
LETTER  = re.compile('[a-zA-Zα-ωΑ-Ω]')
NUMERAL = re.compile('[+−]?[0-9]+') # U+2212 MINUS SIGN not U+002D HYPHEN-MINUS

SPECIAL = re.compile('([' + re.escape('<>[]()!₀₁₂₃₄₅₆₇₈₉') + '])')

SUPERSCRIPT = {
    '+': '⁺', '0': '⁰', '1': '¹', '2': '²', '3': '³', '4': '⁴',
    '−': '⁻', '5': '⁵', '6': '⁶', '7': '⁷', '8': '⁸', '9': '⁹',
}

SUBSCRIPT = {
    '+': '₊', '0': '₀', '1': '₁', '2': '₂', '3': '₃', '4': '₄',
    '−': '₋', '5': '₅', '6': '₆', '7': '₇', '8': '₈', '9': '₉',
}

SKIPCLASS = {
    '₁': 'em',  '₂': 'en',  '₃': 'ws3', '₄': 'ws4',
    '₅': 'ws5', '₆': 'ws6', '₇': 'ws7', '₈': 'ws8',
}

# https://www.desmos.com/calculator/jirjvadckz

#    name    size   class
#    ────  ───────  ─────
# ₁  em      1  em    em
# ₂  en     1/2 em    en
# ₃         1/3 em   ws3
# ₄  word   1/4 em   ws4
# ₅  thin   1/6 em   ws5
# ₆  hair  1/10 em   ws6
# ₇        1/16 em   ws7
# ₈        1/24 em   ws8

def _parse(
    src    : str,
    offset : int           = 0,
    stop   : Optional[str] = None,
    italic : bool          = False
) -> tuple[list[str | HtmlElement], int, bool]:
    # Returns HTML output, the index following the last character parsed,
    #   and whether the parse ended because the stop pattern was matched.
    #  (If the stop pattern is matched, the returned index is the index
    #   following the stop pattern.)
    #
    # hyperlinks               @{...}{...}
    # inline math               $...$   automatically no-break
    # inline code               `...`
    # small capitals    %word  %{...}
    # variables         'letr  '{...}   using <var>
    # superscripts      ^nmrl  ^{...}   using <sup> or U+2070–208F
    # subscripts        _nmrl  _{...}
    # italic            *word  *{...}
    # bold                     &{...}
    # margin notes             †{...}
    # inline notes            ※ {...}
    # no-break spans            {...}
    # fixed whitespace  ₁₂₃₄₅₆₇₈₉
    # hyphenation point ₀

    # offset        # number of characters scanned
    adv = offset    # number of characters taken (less than or equal to offset)
    out = []        # output for the slice src[:adv]
    stopped = False

    def emit(text):
        fragment = []
        for char in SPECIAL.split(text):
            if not char:
                continue
            match char:
                case '<':
                    fragment.append('&lt;')
                case '>':
                    fragment.append('&gt;')
                case '('|')'|'['|']' if italic:
                    if fragment:
                        out.append(''.join(fragment))
                        fragment = []
                    out.append(HtmlElement('span', char, kind='up'))
                case '!' if not italic:
                    if fragment:
                        out.append(''.join(fragment))
                        fragment = []
                    out.append(HtmlElement('i', char))
                case '₀':
                    fragment.append('&shy;')
                case '₁'|'₂'|'₃'|'₄'|'₅'|'₆'|'₇'|'₈'|'₉':
                    if fragment:
                        out.append(''.join(fragment))
                        fragment = []
                    out.append(HtmlElement('span', ' ', kind=SKIPCLASS[char]))
                case _:
                    fragment.append(char)
        if fragment:
            out.append(''.join(fragment))

    ini = None  # index of the sigil being examined

    def push(post, *expansion):
        # post        index of the first character after the delimited region
        # expansion   list of str/HtmlElement
        nonlocal offset
        nonlocal adv
        if ini > adv:
            emit(src[adv:ini])
        out.extend(expansion)
        offset = post
        adv = post

    while offset < len(src):
        sigil = INITIAL.search(src, offset)

        # There are no more sigils that could start a delimited region,
        #   so there can’t be any more delimited regions, so we tidy up
        #   and exit the loop.
        if sigil is None:
            # Only read up until the stop pattern.
            if stop is not None:
                cutoff = src.find(stop, offset)
                if cutoff != -1:
                    if cutoff > adv:
                        emit(src[adv:cutoff])
                        adv = cutoff
                    adv += len(stop)
                    stopped = True
                    break
            # Otherwise read to the end of the source.
            if adv < len(src):
                emit(src[adv:])
                adv = len(src)
            break

        # Check whether the stop pattern occurs at or before the next sigil.
        ini = sigil.start()
        if stop is not None:
            cutoff = src.find(stop, offset, ini + len(stop))
            if cutoff != -1:
                if cutoff > adv:
                    emit(src[adv:cutoff])
                    adv = cutoff
                adv += len(stop)
                stopped = True
                break

        # At the very least, the offset should be the index after the sigil.
        # If this is a valid entity, we will move it further (to the end of
        #   the entity).
        offset = sigil.end()

        match sigil.group():
            # HTML
            case '<':
                # Comment
                if src[offset:offset+3] == '!--':
                    offset += 3
                    end = src.find('-->', offset)
                    if end == -1:
                        push(offset, parse_error('&lt;!--'))
                    else:
                        push(end + 3)
                    continue

                # Unexpected closing tag
                #   (Note that we’re overly restrictive here.)
                if src[offset:offset+1] == '/':
                    offset += 1
                    push(offset, parse_error('&lt;/'))
                    continue

                # Less-than operator
                if not ELEMINI.fullmatch(src[offset:offset+1]):
                    continue

                # Plausible opening tag
                index = offset
                element = None
                attrs = {}

                # 1 Find the closing delimiter
                while True:
                    match = TAGBRK.search(src, index)
                    if match is None:
                        break
                    index = match.start()
                    char = match.group()
                    if char == '>':
                        tag = src[offset:index].removesuffix('/') \
                            .split(maxsplit=1)
                        index += 1
                        element = tag[0]
                        if len(tag) > 1:
                            attrs = parse_attributes(tag[1])
                        break
                    if char == '"' or char == "'":
                        index += 1
                        delim = src.find(char, index)
                        if delim == -1:
                            err = parse_error('&lt;' + src[offset:index])
                            push(index, err)
                            break
                        index = delim + 1
                        continue
                    raise AssertionError
                else:
                    push(offset, parse_error('&lt;'))
                    continue

                if element is None:
                    continue

                # 2 Check that the opening tag is well-formed
                if element not in ELEMENTS:
                    # This isn’t an HTML tag, although it looks like one.
                    #   We could ignore it, but it’s probably better to let
                    #   the author know.
                    push(index, parse_error(f'&lt;{src[offset:index-1]}&gt;'))
                    continue

                if attrs is None:
                    # The attributes are not well-formed.
                    push(index, parse_error(f'&lt;{src[offset:index-1]}&gt;'))
                    continue

                # 3 Find the closing tag
                if element in VOID:
                    # This is a void element, so there’s
                    #   no corresponding closing tag.
                    if element == 'include':
                        if 'href' not in attrs:
                            push(index)
                            continue
                        # TODO path ought to be relative to the file
                        with open(attrs['href']) as external:
                            content = external.read()
                        inner, _, _ = _parse(content.strip())
                        push(index, *inner)
                    else:
                        push(index, HtmlElement(element, **attrs))
                    continue

                special = element in ('style', 'python')
                if special:
                    cutoff = src.find('</', index)
                    complete = cutoff != -1
                    if complete:
                        inner = src[index:cutoff]
                        post = cutoff + 2
                else:
                    inner, post, complete = _parse(src, index, '</', italic)

                if not complete:
                    push(index, parse_error(f'&lt;{src[offset:index-1]}&gt;'))
                    continue

                # 4 Check that the closing tag matches
                end = src.find('>', post)
                if end == -1:
                    interior = f'&lt;{element}&gt;...' if special \
                        else HtmlElement(element, *inner, **attrs)
                    push(post, interior, parse_error(f'&lt;/'))
                    continue

                tag = src[post:end]
                if tag.strip() != element:
                    interior = f'&lt;{element}&gt;...' if special \
                        else HtmlElement(element, *inner, **attrs)
                    push(end + 1, interior, parse_error(f'&lt;/{tag}&gt;'))
                    continue

                if element == 'style':
                    # TODO parse CSS
                    push(end + 1)
                    continue

                if element == 'python':
                    # TODO unindent inner
                    GLOBALS['STREAM'].clear()
                    exec(inner, GLOBALS)
                    insert = GLOBALS['STREAM']
                    if insert:
                        push(end + 1, *insert)
                    else:
                        push(end + 1)
                    continue

                push(end + 1, HtmlElement(element, *inner, **attrs))

            # Hyperlinks
            case '@':
                if src[offset:offset+1] != '{':
                    continue
                offset += 1
                inner, post, complete = _parse(src, offset, '}', italic)
                if not complete:
                    push(offset, parse_error('@{'))
                    continue
                delim = NONSPACE.search(src, post)
                if delim is None:
                    push(post, parse_error(inner))
                    continue
                if delim.group() != '{':
                    push(delim.end(), *inner, parse_error(delim.group()))
                    continue
                start = delim.end()
                end = src.find('}', start)
                if end == -1:
                    push(start, *inner, parse_error('{'))
                    continue
                url = src[start:end].strip()
                if '{' in url or '"' in url or "'" in url:
                    push(end + 1, *inner, parse_error(url))
                else:
                    push(end + 1, HtmlElement('a', *inner, href=url))

            # Inline mathematics
            case '$':
                end = src.find('$', offset)
                if end == -1:
                    push(offset, parse_error('$'))
                else:
                    expr = src[offset:end]
                    result = parse_math(expr)
                    if result is None:
                        push(end + 1, parse_error(f'${expr}$'))
                    else:
                        push(end + 1, result.html(inline=True))

            # Inline code
            case '`':
                end = src.find('`', offset)
                if end == -1:
                    push(offset, parse_error('`'))
                else:
                    push(end + 1, HtmlElement('code', src[offset:end]))

            # Small capitals
            case '%':
                if src[offset:offset+1] == '{':
                    offset += 1
                    inner, post, complete = _parse(src, offset, '}', italic)
                    if complete:
                        push(post, HtmlElement('span', *inner, kind='sc'))
                    else:
                        push(offset, parse_error('%{'))
                else:
                    word = WORD.match(src, offset)
                    if word is None:
                        continue
                    span = HtmlElement('span', word.group(), kind='sc')
                    push(word.end(), span)

            # Variables
            case "'":
                if src[offset:offset+1] == '{':
                    offset += 1
                    inner, post, complete = _parse(src, offset, '}', italic)
                    if complete:
                        push(post, HtmlElement('var', *inner))
                    else:
                        push(offset, parse_error("'{"))
                else:
                    letter = LETTER.match(src, offset)
                    if letter is None:
                        continue
                    push(letter.end(), HtmlElement('var', letter.group()))

            # Superscripts and subscripts
            case '^' | '_':
                if src[offset:offset+1] == '{':
                    offset += 1
                    inner, post, complete = _parse(src, offset, '}', italic)
                    if complete:
                        element = 'sub' if sigil.group() == '_' else 'sup'
                        push(post, HtmlElement(element, *inner))
                    else:
                        push(offset, parse_error(sigil.group() + "{"))
                else:
                    numeral = NUMERAL.match(src, offset)
                    if numeral is None:
                        continue
                    charmap = SUBSCRIPT if sigil.group() == '_' else SUPERSCRIPT
                    replacement = ''.join(charmap[d] for d in numeral.group())
                    push(numeral.end(), replacement)

            # Italic
            case '*':
                if src[offset:offset+1] == '{':
                    offset += 1
                    inner, post, complete = _parse(src, offset, '}', True)
                    if complete:
                        push(post, HtmlElement('i', *inner))
                    else:
                        push(offset, parse_error('*{'))
                else:
                    word = WORD.match(src, offset)
                    if word is None:
                        continue
                    push(word.end(), HtmlElement('i', word.group()))

            # Bold
            case '&':
                if src[offset:offset+1] != '{':
                    continue
                offset += 1
                inner, post, complete = _parse(src, offset, '}', italic)
                if complete:
                    push(post, HtmlElement('b', *inner))
                else:
                    push(offset, parse_error('&{'))

            # Margin notes
            case '†':
                if src[offset:offset+1] != '{':
                    continue
                offset += 1
                inner, post, complete = _parse(src, offset, '}', italic)
                if complete:
                    push(post, HtmlElement('span', *inner, kind='margin-note'))
                else:
                    push(offset, parse_error('†{'))

            # Inline notes
            case '※':
                if src[offset:offset+2] == ' {':
                    offset += 2
                elif src[offset:offset+1] == '{':
                    offset += 1
                else:
                    continue
                inner, post, complete = _parse(src, offset, '}', italic)
                if complete:
                    push(post, HtmlElement('span', *inner, kind='inline-note'))
                else:
                    push(offset, parse_error(src[ini:offset]))

            # No-break spans
            case '{':
                inner, post, complete = _parse(src, offset, '}', italic)
                if complete:
                    push(post, HtmlElement('span', *inner, kind='nobr'))
                else:
                    push(offset, parse_error('{'))

            case '}':
                push(offset, parse_error('}'))

    return (out, adv, stopped)


def parse(src : str) -> list[str | HtmlElement]:
    out, _, _ = _parse(src)
    return out


GLOBALS = {
    'HtmlElement': HtmlElement,
    'parse':       parse,
    'STREAM':      []
}


def convert(src_lines : str) -> list[HtmlElement]:
    return []

def p(source):
    out = parse(source)
    buffer = []
    HtmlElement('p', *out).render(buffer)
    print(''.join(buffer))
