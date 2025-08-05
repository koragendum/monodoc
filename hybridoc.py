#! /usr/bin/python

import re

from html    import HtmlElement
from mathml  import parse as parseMath
from inspect import currentframe, getframeinfo
from re      import Match as MatchObject
from typing  import Optional

def parse_error(text):
    text = text.replace('<', '&lt;').replace('>', '&gt;')
    kwargs = {
        'class': 'hybridoc-error',
        'line-number': getframeinfo(currentframe().f_back).lineno
    }
    if isinstance(text, str):
        return HtmlElement('span', text, **kwargs)
    else:
        return HtmlElement('span', *text, **kwargs)

INITIAL = re.compile('[' + re.escape("$%&'*<@^_`{}\u2020\u203B") + ']')
NONSPACE = re.compile('[^ \t\n\r]')

WORD    = re.compile('[a-zA-Z]+(?:-[a-zA-Z]+)*')
LETTER  = re.compile('[a-zA-Zα-ωΑ-Ω]')
NUMERAL = re.compile('[+−]?[0-9]+') # U+2212 MINUS SIGN not U+002D HYPHEN-MINUS

def parse(
    src    : str,
    offset : int           = 0,
    stop   : Optional[str] = None,
    italic : bool          = False
) -> tuple[list[str | HtmlElement], int, bool]:
    # Returns HTML output, the index following the last character parsed,
    #   and whether the parse ended because the stop pattern was matched.
    #  (If the stop pattern is matched, the returned index is the start
    #   of the stop pattern.)
    #
    # hyperlinks               @{...}{...}
    # inline math               $...$   automatically no-break
    # inline code               `...`
    # small capitals    %word  %{...}
    # variables         'letr  '{...}   using <var>
    # superscripts      ^nmrl  ^{...}   using <sup> or U+2070–208F
    # subscripts        _nmrl  _{...}
    # italic            *word  *{...}
    # bold              &word  &{...}
    # margin notes             †{...}
    # inline notes            ※ {...}
    # no-break spans            {...}
    # fixed whitespace  ₁₂₃₄

    # offset        # number of characters scanned
    adv = offset    # number of characters taken (less than or equal to offset)
    out = []        # output for the slice src[:adv]
    stopped = False

    def emit(text):
        # TODO unitalicize delimiters if italic flag is set
        # TODO fixed whitespace
        # TODO escape &lt;
        # TODO italicize exclamation marks
        out.append(text)

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
                stopped = True
                break

        # At the very least, the offset should be the index after the sigil.
        # If this is a valid entity, we will move it further (to the end of
        #   the entity).
        offset = sigil.end()

        # Each arm needs to either
        # • continue, or
        # • define “expansion” (a list of str/HtmlElement) and “post”
        #   (the index of the first character after the delimited region).
        match sigil.group():
            # HTML
            case '<':
                continue

            # Hyperlinks
            case '@':
                if src[offset:offset+1] != '{':
                    continue
                offset += 1
                inner, stop_idx, complete = parse(src, offset, '}', italic)
                if complete:
                    delim = NONSPACE.search(src, stop_idx+1)
                    if delim is None:
                        expansion = parse_error(inner)
                        post = stop_idx + 1
                    elif delim.group() != '{':
                        expansion = [*inner, parse_error(delim.group())]
                        post = delim.end()
                    else:
                        start = delim.end()
                        end = src.find('}', start)
                        if end == -1:
                            expansion = [*inner, parse_error(delim.group())]
                            post = start
                        else:
                            url = src[start:end].strip()
                            if '{' in url or '"' in url or "'" in url:
                                expansion = [*inner, parse_error(url)]
                            else:
                                expansion = HtmlElement('a', *inner, href=url)
                            post = end + 1
                else:
                    expansion = parse_error('@{')
                    post = offset

            # Inline mathematics
            case '$':
                end = src.find('$', offset)
                if end == -1:
                    expansion = parse_error('$')
                    post = offset
                else:
                    expr = src[offset:end]
                    result = parseMath(expr)
                    if result is None:
                        expansion = parse_error(f'${expr}$')
                    else:
                        expansion = result.html(inline=True)
                    post = end + 1

            # Inline code
            case '`':
                end = src.find('`', offset)
                if end == -1:
                    expansion = parse_error('`')
                    post = offset
                else:
                    expansion = HtmlElement('code', src[offset:end])
                    post = end + 1

            # Small capitals
            case '%':
                if src[offset:offset+1] == '{':
                    offset += 1
                    inner, stop_idx, complete = parse(src, offset, '}', italic)
                    if complete:
                        expansion = HtmlElement('span', *inner, class_='sc')
                        post = stop_idx + 1
                    else:
                        expansion = parse_error('%{')
                        post = offset
                else:
                    word = WORD.match(src, offset)
                    if word is None:
                        continue
                    expansion = HtmlElement('span', word.group(), class_='sc')
                    post = word.end()

            # Variables
            case "'":
                continue

            # Superscripts
            case '^':
                continue

            # Subscripts
            case '_':
                continue

            # Italic
            case '*':
                if src[offset:offset+1] == '{':
                    offset += 1
                    inner, stop_idx, complete = parse(src, offset, '}', True)
                    if complete:
                        expansion = HtmlElement('i', *inner)
                        post = stop_idx + 1
                    else:
                        expansion = parse_error('*{')
                        post = offset
                else:
                    word = WORD.match(src, offset)
                    if word is None:
                        continue
                    expansion = HtmlElement('i', word.group())
                    post = word.end()

            # Bold
            case '&':
                if src[offset:offset+1] == '{':
                    offset += 1
                    inner, stop_idx, complete = parse(src, offset, '}', italic)
                    if complete:
                        expansion = HtmlElement('b', *inner)
                        post = stop_idx + 1
                    else:
                        expansion = parse_error('&{')
                        post = offset
                else:
                    word = WORD.match(src, offset)
                    if word is None:
                        continue
                    expansion = HtmlElement('b', word.group())
                    post = word.end()

            # Margin notes
            case '†':
                if src[offset:offset+1] != '{':
                    continue
                offset += 1
                inner, stop_idx, complete = parse(src, offset, '}', italic)
                if complete:
                    expansion = HtmlElement('span', *inner, class_='margin-note')
                    post = stop_idx + 1
                else:
                    expansion = parse_error('†{')
                    post = offset

            # Inline notes
            case '※':
                if src[offset:offset+1] == ' ':
                    if src[offset+1:offset+2] != '{':
                        continue
                    offset += 2
                else:
                    if src[offset:offset+1] != '{':
                        continue
                    offset += 1
                inner, stop_idx, complete = parse(src, offset, '}', italic)
                if complete:
                    expansion = HtmlElement('span', *inner, class_='inline-note')
                    post = stop_idx + 1
                else:
                    expansion = parse_error('※{')
                    post = offset

            # No-break spans
            case '{':
                inner, stop_idx, complete = parse(src, offset, '}', italic)
                if complete:
                    expansion = HtmlElement('span', *inner, class_='nobr')
                    post = stop_idx + 1
                else:
                    expansion = parse_error('{')
                    post = offset

            case '}':
                expansion = parse_error('}')
                post = offset

        if ini > adv:
            emit(src[adv:ini])

        if isinstance(expansion, list):
            out.extend(expansion)
        else:
            out.append(expansion)
        offset = post
        adv = post

    # TODO
    #   spacing corrections (delimiters, operators, quote marks)
    #   italic corrections  (delimiters, exclamation marks)

    return (out, adv, stopped)


def convert(src_lines : str) -> list[HtmlElement]:
    # headings <h2–6>       # ...  # {...} ...  # !{...} ...
    # paragraphs
    #   indent              |⟩ |...⟩
    # lists                 - +
    # tables                |
    # code blocks           ```
    # block quotes          >               <blockquote>
    # block notes           *
    return []

def p(source):
    out, advance, stopped = parse(source)
    buffer = []
    HtmlElement('p', *out).render(buffer)
    print(''.join(buffer))
    if advance < len(source):
        print(source[advance:])
