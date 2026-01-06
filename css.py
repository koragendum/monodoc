import re

from html import INDENT
from inspect import currentframe, getframeinfo
from typing import Optional

class Map:
    def __init__(self, constructor=None):
        self.keys = []
        self.data = {}
        self.default = constructor

    def __len__(self):
        return len(self.keys)

    def __contains__(self, key):
        return key in self.data

    def __getitem__(self, key):
        if key not in self.data and self.default is not None:
            self.keys.append(key)
            self.data[key] = self.default()
        return self.data[key]

    def __setitem__(self, key, value):
        if key not in self.data:
            self.keys.append(key)
        self.data[key] = value

    def delete(self, key):
        if key in self.data:
            self.keys.remove(key)
            del self.data[key]

    def __iter__(self):
        return iter(self.keys)

    def items(self):
        return ((key, self.data[key]) for key in self.keys)


class CssRules:
    def __init__(self):
        self.ruleset = Map(Map) # maps selector to declarations

    def __contains__(self, selector):
        return selector in self.ruleset

    def __getitem__(self, selector):
        return self.ruleset[selector]

    def delete(self, selector):
        self.ruleset.delete(selector)

    def render(self, buffer, depth=0):
        # NOTE that unlike HtmlElement.render, the elements of the buffer are
        #   expected to be joined with newlines rather than empty strings.
        outermargin = ' ' * (INDENT * depth)
        innermargin = ' ' * (INDENT * (depth + 1))
        for selector, declarations in self.ruleset.items():
            buffer.append(f'{outermargin}{selector} {{')
            for prop, value in declarations.items():
                buffer.append(f'{innermargin}{prop}: {value};')
            buffer.append(f'{outermargin}}}')


class StyleSheet:
    def __init__(self):
        self.base    = CssRules()
        self.media   = Map(CssRules)    # maps media query to CssRules
        self.other   = []   # list of instances of str
        # The items of self.other can contain newlines, but we expect them to
        #   be stripped (so that the first line has no leading whitespace and
        #   the last line has no trailing whitespace).
        # The list is used for block at-rules other than @media, such as
        #   @font-face and @font-feature-values.

    def __contains__(self, selector):
        return selector in self.base.ruleset

    def __getitem__(self, selector):
        return self.base.ruleset[selector]

    def render(self, buffer, depth=0):
        # NOTE that unlike HtmlElement.render, the elements of the buffer are
        #   expected to be joined with newlines rather than empty strings.
        margin = ' ' * (INDENT * depth)
        for other in self.other:
            buffer.extend(margin + ln for ln in other.split('\n'))
        self.base.render(buffer, depth)
        for query, css_rules in self.media.items():
            buffer.append(f'{margin}@media {query} {{')
            css_rules.render(buffer, depth + 1)
            buffer.append(f'{margin}}}')


def render(stylesheet, depth=0):
    buffer = []
    stylesheet.render(buffer, depth)
    return '\n'.join(buffer)


COMPACTSP = re.compile(r'[ \t\r\n]+')
REMOVERHS = re.compile('([' + re.escape('([') + ']) ')
REMOVELHS = re.compile(' ([' + re.escape(')],') + '])')
ENSURELHS = re.compile('(?<=[^ ])([>+~])(?!=)')
ENSURERHS = re.compile('([,>+~])(?=[^ =])')

def canonicalize_selector(sel):
    # We’re fairly circumspect about this. We only do the following:
    # • strip leading and trailing whitespace
    # • replace all whitespace sequences with single spaces
    # • remove space after “(” and “[”
    # • remove space before “)” and “]”
    # • remove space before “,”
    # • ensure there is space after “,”
    # • ensure there is space around “>” and “+” and “~”
    #   (unless followed by “=”)
    sel = COMPACTSP.sub(' ', sel.strip())
    sel = REMOVERHS.sub(r'\1', sel)
    sel = REMOVELHS.sub(r'\1', sel)
    sel = ENSURELHS.sub(r' \1', sel)
    sel = ENSURERHS.sub(r'\1 ', sel)
    return sel

QENSURELHS = re.compile('(?<=[^ ])([<>])')
QENSURERHS = re.compile('(,|[<>]=?)(?=[^ =])')

def canonicalize_query(query):
    # We expect “@media” to have already been removed.
    query = COMPACTSP.sub(' ', query.strip())
    query = REMOVERHS.sub(r'\1', query)
    query = REMOVELHS.sub(r'\1', query)
    query = QENSURELHS.sub(r' \1', query)
    query = QENSURERHS.sub(r'\1 ', query)
    return query

VENSURERHS = re.compile('(,)(?=[^ ])')

def canonicalize_value(value):
    value = COMPACTSP.sub(' ', value)
    value = REMOVERHS.sub(r'\1', value)
    value = REMOVELHS.sub(r'\1', value)
    value = VENSURERHS.sub(r'\1 ', value)
    return value


INITIAL = re.compile(r'(?:\{|\}|/\*|\*/)')

def _closing_brace(src : str, offset : int) -> Optional[int]:
    length = len(src)
    depth = 0
    while offset < length:
        sigil = INITIAL.search(src, offset)
        if sigil is None:
            return None
        ini = sigil.start()
        match sigil.group():
            case '{':
                offset = ini + 1
                depth += 1
            case '}':
                offset = ini + 1
                if depth == 0:
                    return offset
                depth -= 1
            case '/*':
                end = src.find('*/', ini+2)
                if end == -1:
                    return None
                offset = end + 2
            case '*/':
                return None


PROPERTY = re.compile(r'-{0,2}[a-z]+(?:-[a-z]+)*')
PROP_SIGIL = re.compile(r'[:;}]|/\*|\*/')

def _parse_property(src : str, offset : int) -> Optional[tuple[str, int]]:
    uncomment = []
    length = len(src)
    while offset < length:
        sigil = PROP_SIGIL.search(src, offset)
        if sigil is None:
            return None
        ini = sigil.start()
        match sigil.group():
            case ':':
                if uncomment:
                    uncomment.append(src[offset:ini])
                    prop = ''.join(uncomment).strip()
                else:
                    prop = src[offset:ini].strip()
                if PROPERTY.fullmatch(prop):
                    return (prop, ini + 1)
                return None
            case '/*':
                uncomment.append(src[offset:ini])
                end = src.find('*/', ini+2)
                if end == -1:
                    return None
                offset = end + 2
            case '*/':
                return None
            case _:
                return None


DEC_SIGIL = re.compile(r'[";}]|/\*|\*/')

def _parse_value(src : str, offset : int) -> Optional[tuple[str, int]]:
    uncomment = []
    atomic = []
    length = len(src)
    while offset < length:
        sigil = DEC_SIGIL.search(src, offset)
        if sigil is None:
            return None
        ini = sigil.start()
        segment = src[offset:ini]
        match sigil.group():
            case '"':
                uncomment.append(segment)
                end = src.find('"', ini+1)
                if end == -1:
                    return None
                uncomment.append('\ufffc')
                atomic.append(src[ini:end+1])
                offset = end + 1
            case '/*':
                uncomment.append(segment)
                end = src.find('*/', ini+2)
                if end == -1:
                    return None
                offset = end + 2
            case '*/':
                return None
            case _:
                if uncomment:
                    uncomment.append(segment)
                    value = ''.join(uncomment)
                else:
                    value = segment
                value = canonicalize_value(value)
                if atomic:
                    atomic = iter(atomic)
                    value = re.sub('\ufffc', lambda _: next(atomic), value)
                return (value, ini + 1)


def _parse(
    stylesheet : StyleSheet | CssRules,
    src    : str,
    offset : int = 0,
) -> int:
    # Returns the index following the last character parsed.

    def parse_error(text):
        line_number = getframeinfo(currentframe().f_back).lineno
        print(f"css: {line_number}: parse error at “{text}”")
        context = src[:offset].splitlines()
        context = context[-8:]
        lengths = ((len(ln), len(ln.lstrip())) for ln in context)
        leftskip = min(
            (total - trimmed for total, trimmed in lengths if trimmed > 0),
            default = 0
        )
        for ln in context:
            print('  ' + ln[leftskip:].rstrip())
        raise RuntimeError

    uncomment = []
    length = len(src)
    while offset < length:
        sigil = INITIAL.search(src, offset)
        if sigil is None:
            break

        ini = sigil.start()
        uncomment.append(src[offset:ini])
        match sigil.group():
            case '{':
                label = ''.join(uncomment).strip()
                uncomment.clear()
                offset = ini + 1

                # At-rules
                if label.startswith('@'):
                    # This is the one section we crash rather than recover.
                    assert isinstance(stylesheet, StyleSheet)
                    tokens = label.split(maxsplit=1)
                    match tokens[0]:
                        case '@media':
                            assert len(tokens) > 1
                            query = canonicalize_query(tokens[1])
                            css_rules = stylesheet.media[query]
                            offset = _parse(css_rules, src, offset)
                            if not css_rules.ruleset:
                                stylesheet.media.delete(query)

                        case '@font-face' | '@font-feature-values':
                            end = _closing_brace(src, offset)
                            if end is None:
                                parse_error(f'{label} {{{src[offset:]}')
                            inner = src[offset:end-1]
                            stylesheet.other.append(f'{label} {{{inner}}}')
                            offset = end

                        case _:
                            raise NotImplementedError

                    continue

                # Rulesets
                selector = canonicalize_selector(label)
                if not selector:
                    # This should be an error, but we forge ahead.
                    selector = None

                ruleset = stylesheet[selector]

                while offset < length:
                    prop = _parse_property(src, offset)
                    if prop is None:
                        dec = _parse_value(src, offset)
                        if dec is None:
                            parse_error(src[offset:])
                        excess, end = dec
                        if excess.strip():
                            parse_error(excess)
                        offset = end
                        if src[end-1] == '}':
                            break
                        continue

                    prop, offset = prop
                    dec = _parse_value(src, offset)
                    if dec is None:
                        parse_error(src[offset:])
                    value, end = dec
                    value = value.strip()
                    if not value:
                        parse_error(f'{prop}:')
                    if value == 'delete':
                        ruleset.delete(prop)
                        if not ruleset:
                            stylesheet.delete(selector)
                    else:
                        ruleset[prop] = value
                    offset = end
                    # NOTE we allow the omission of the final semicolon!
                    if src[end-1] == '}':
                        break

            case '}':
                label = ''.join(uncomment)
                uncomment.clear()
                if label.strip():
                    parse_error(label)
                offset = ini + 1
                break

            case '/*':
                end = src.find('*/', ini+2)
                if end == -1:
                    offset = length
                    break
                offset = end + 2

            case '*/':
                # Not actually an error, but something has probably gone wrong.
                offset = length
                break

    if uncomment:
        extraneous = ''.join(uncomment).strip()
        if extraneous:
            parse_error(extraneous)

    return offset


def parse(src : str, stylesheet : Optional[StyleSheet] = None) -> StyleSheet:
    if stylesheet is None:
        stylesheet = StyleSheet()
    _parse(stylesheet, src)
    return stylesheet
