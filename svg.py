from math import atan2, ceil, cos, floor, log, sin, sqrt, tau

def sample(f, a, b, n):
    # divides [a, b] into n regions (returns n + 1 points)
    d = 1.0 / n
    xs = []
    xs.append(a)
    xs.extend((a * (n - i) + b * i) * d for i in range(1, n))
    xs.append(b)
    return [(x, f(x)) for x in xs]

def adaptive_sample(f, a, b, n, r=0.015625, limit=10):
    # divides [a, b] into n regions (returns n + 1 points)
    #   and then subdivides as needed so that adjacent line
    #   segments are r radians or less from being colinear
    d = 1.0 / n
    xs = []
    xs.append(a)
    xs.extend((a * (n - i) + b * i) * d for i in range(1, n))
    xs.append(b)
    points = [(x, f(x)) for x in xs]
    angles = []
    for i in range(len(points) - 1):
        x0, y0 = points[i]
        x1, y1 = points[i + 1]
        angles.append(atan2(y1 - y0, x1 - x0))

    for _ in range(limit):
        stable = True
        subdiv_points = []
        subdiv_angles = []
        div_next = False
        for i in range(len(angles) - 1):
            t0 = angles[i]
            t1 = angles[i + 1]
            over = abs(t1 - t0) > r
            # subdivide points[i] to points[i + 1] and mark
            #   points[i + 1] to points[i + 2] for subdivision
            if div_next or over:
                x0, y0 = points[i]
                x1, y1 = points[i + 1]
                xm = (x0 + x1) * 0.5
                ym = f(xm)
                subdiv_points.append((x0, y0))
                subdiv_angles.append(atan2(xm - x0, ym - y0))
                subdiv_points.append((xm, ym))
                subdiv_angles.append(atan2(x1 - xm, y1 - ym))
                stable = False
            else:
                subdiv_points.append(points[i])
                subdiv_angles.append(t0)
            div_next = over

        if div_next:
            x0, y0 = points[-2]
            x1, y1 = points[-1]
            xm = (x0 + x1) * 0.5
            ym = f(xm)
            subdiv_points.append((x0, y0))
            subdiv_angles.append(atan2(xm - x0, ym - y0))
            subdiv_points.append((xm, ym))
            subdiv_angles.append(atan2(x1 - xm, y1 - ym))
        else:
            subdiv_points.append(points[-2])
            subdiv_angles.append(angles[-1])

        subdiv_points.append(points[-1])

        points = subdiv_points
        angles = subdiv_angles

        if stable:
            break

    return points

def resize(inp, out):
    # maps [a₀, b₀] to [a₁, b₁]
    a0, b0 = inp
    a1, b1 = out
    d = 1.0 / (b0 - a0)
    return lambda x: (a1 * (b0 - x) + b1 * (x - a0)) * d

def window(a, b, origin, detail, margin, radix=10):
    if origin:
        if a > 0.0: a = 0.0
        if b < 0.0: b = 0.0
    size = (b - a) / detail
    assert size != 0.0
    unit = radix ** round(log(size, radix))
    margin = (b - a) * margin
    a = floor((a - margin) / unit) * unit
    b =  ceil((b + margin) / unit) * unit
    return (a, b)

def guidestep(a, b, divisions, radix=10):
    size = (b - a) / divisions
    assert size != 0.0
    return radix ** round(log(size, radix))

def fallback(value, default):
    return default if value is None else value

def delinearize(x):
  if x > 0.0031308:
    return 1.055 * x ** (1.0 / 2.4) - 0.055
  return x * 12.92

def lch_to_srgb(l, c, h):
    h = h / 360.0 * tau
    a = c * cos(h)
    b = c * sin(h)
    # “f” for “far” instead of “l” for “long”
    f = l + a * 0.3963377774 + b * 0.2158037573
    m = l - a * 0.1055613458 - b * 0.0638541728
    s = l - a * 0.0894841775 - b * 1.2914855480
    f = f * f * f
    m = m * m * m
    s = s * s * s
    r = delinearize(f *  4.0767416621 - m * 3.3077115913 + s * 0.2309699292)
    g = delinearize(f * -1.2684380046 + m * 2.6097574011 - s * 0.3413193965)
    b = delinearize(f * -0.0041960863 - m * 0.7034186147 + s * 1.7076147010)
    r = round(r * 255.0)
    g = round(g * 255.0)
    b = round(b * 255.0)
    assert all(-1 < channel < 256 for channel in (r, g, b))
    return f'#{r:02x}{g:02x}{b:02x}'

def color_to_rgba(color):
    assert color is not None
    if isinstance(color, (int, float)):
        l, c, h, alpha = color, 0, 0, 1
    elif len(color) > 3:
        l, c, h, alpha = color
        alpha = round(alpha, 3)
    else:
        l, c, h = color
        alpha = 1
    return (lch_to_srgb(l, c, h), alpha)

def square_distances(pairs):
    for i in range(len(pairs) - 1):
        x0, y0 = pairs[i]
        x1, y1 = pairs[i + 1]
        dx = x1 - x0
        dy = y1 - y0
        yield dx * dx + dy * dy

class SVG:
    def __init__(self,
        width,          # pixels
        height,         # pixels
        margin=0,       # pixels
        xrange=None,    # (low, high)
        yrange=None,    # (low, high)
        stroke=None,    # pixels
        fgcolor=(0.9, 0, 0),    # (l, c, h) or (l, c, h, α)
        bgcolor=None,           # (l, c, h) or (l, c, h, α) or None
        radius=None,
    ):
        self.width   = width
        self.height  = height
        self.margin  = margin
        self.xrange  = xrange
        self.yrange  = yrange
        self.stroke  = stroke
        self.fgcolor = fgcolor
        self.bgcolor = bgcolor
        self.radius  = radius
        self.xauto = {
            'origin': None,
            'detail': None,
            'margin': None,
            'radix':  None,
        }
        self.yauto = {
            'origin': None,
            'detail': None,
            'margin': None,
            'radix':  None,
        }
        self.guides   = []
        self.elements = []

    def auto_window(self, axis, **kwargs):
        match axis:
            case 'x': self.xauto.update(kwargs)
            case 'y': self.yauto.update(kwargs)
            case  _ : raise AssertionError(f'"{axis}" is not an axis')

    def add_rule(
        self,
        axis,
        value=0,
        stroke=None,    # defaults to the global default stroke
        color=None,     # defaults to the foreground color
    ):
        self.guides.append(('rule', axis, stroke, color, value))

    def add_graticule(
        self,
        axis,
        stroke=None,    # defaults to the global default stroke
        color=None,     # defaults to the foreground color
        divs=32,
        radix=10,
    ):
        self.guides.append(('graticule', axis, stroke, color, divs, radix))

    def add_points(
        self,
        pairs,
        diameter=None,  # see below
        color=None,     # defaults to the foreground color
    ):
        # If diameter is None, the diameter defaults to a fixed size or a
        # fraction of the smallest interpoint distance, whichever is less,
        # but is clamped to a minimum size.
        self.elements.append(('points', pairs, color, diameter))

    def add_lines(
        self,
        pairs,
        stroke=None,    # defaults to the global default stroke
        color=None,     # defaults to the foreground color
        gap=None,       # see below
        gapcolor=None,  # defaults to the background color
    ):
        # If gap is not None, before drawing the line as usual, a line through
        # the same points is drawn with a width of (stroke + gap × 2).
        self.elements.append(
            ('lines', pairs, color, stroke, gap, gapcolor)
        )

    def render(self):
        xrange = self.xrange
        if xrange is None:
            xmin = min(x for (_, pairs, *_) in self.elements for x, _ in pairs)
            xmax = max(x for (_, pairs, *_) in self.elements for x, _ in pairs)
            origin = fallback(self.xauto['origin'], False)
            detail = fallback(self.xauto['detail'], 8.0)
            margin = fallback(self.xauto['margin'], 0.0)
            radix  = fallback(self.xauto['radix' ], 10)
            xrange = window(xmin, xmax, origin, detail, margin, radix)

        yrange = self.yrange
        if yrange is None:
            ymin = min(y for (_, pairs, *_) in self.elements for _, y in pairs)
            ymax = max(y for (_, pairs, *_) in self.elements for _, y in pairs)
            origin = fallback(self.yauto['origin'], False)
            detail = fallback(self.yauto['detail'], 8.0)    # 16.0
            margin = fallback(self.yauto['margin'], 0.0)    # 0.03125
            radix  = fallback(self.yauto['radix' ], 10)
            yrange = window(ymin, ymax, origin, detail, margin, radix)

        dimension = max(self.width, self.height)

        auto_stroke = max(1, round((dimension / 512) * 2) / 2)

        default_stroke = fallback(self.stroke, auto_stroke)

        xconversion = resize(xrange, (self.margin, self.width - self.margin))
        yconversion = resize(yrange, (self.height - self.margin, self.margin))

        output = [
            '<svg'
            ' version="1.1"'
            ' xmlns="http://www.w3.org/2000/svg"'
            ' xmlns:svg="http://www.w3.org/2000/svg"'
            f' width="{self.width}"'
            f' height="{self.width}"'
            f' viewBox="0 0 {self.width} {self.height}">'
        ]

        if self.bgcolor is not None:
            bgcolor, bgalpha = color_to_rgba(self.bgcolor)

            attributes = [
                f'x="0" y="0" width="{self.width}" height="{self.height}"'
            ]

            if self.radius:
                attributes.append(f'rx="{self.radius}" ry="{self.radius}"')

            attributes.append(f'stroke="none" fill="{bgcolor}"')

            if bgalpha < 1:
                attributes.append(f'fill-opacity="{bgalpha}"')

            attributes = ' '.join(attributes)
            output.append(f'  <rect {attributes}/>')

        for guide in self.guides:
            kind, axis, stroke, color, *miscellania = guide

            stroke = fallback(stroke, default_stroke)

            color, alpha = color_to_rgba(fallback(color, self.fgcolor))

            attributes = [
                f'stroke-width="{round(stroke, 2)}"',
                f'stroke="{color}"',
                'stroke-linecap="square"',
            ]
            if alpha < 1:
                attributes.append(f'stroke-opacity="{alpha}"')
            attributes = ' '.join(attributes)

            if kind == 'rule':
                value, = miscellania

                if axis == 'x':
                    a, b = xrange
                    conv = xconversion
                    cmpl = 'y'
                    u, v = tuple(round(yconversion(y), 2) for y in yrange)
                if axis == 'y':
                    a, b = yrange
                    conv = yconversion
                    cmpl = 'x'
                    u, v = tuple(round(xconversion(x), 2) for x in xrange)

                if value < a or b < value:
                    continue

                mark = round(conv(value), 2)
                output.append(
                    '  <line'
                    f' {axis}1="{mark}" {cmpl}1="{u}"'
                    f' {axis}2="{mark}" {cmpl}2="{v}"'
                    f' {attributes}/>'
                )

            if kind == 'graticule':
                divs, radix = miscellania

                if axis == 'x':
                    divs *= self.width / dimension
                    a, b = xrange
                    conv = xconversion
                    cmpl = 'y'
                    u, v = tuple(round(yconversion(y), 2) for y in yrange)
                if axis == 'y':
                    divs *= self.width / dimension
                    a, b = yrange
                    conv = yconversion
                    cmpl = 'x'
                    u, v = tuple(round(xconversion(x), 2) for x in xrange)

                step = guidestep(a, b, divs, radix)
                sA =  ceil(round(a / step, 2))
                sB = floor(round(b / step, 2))

                if sA >= sB:
                    continue

                output.append(f'  <g {attributes}>')
                for i in range(sA, sB + 1):
                    mark = round(conv(i * step), 2)
                    output.append(
                        '    <line'
                        f' {axis}1="{mark}" {cmpl}1="{u}"'
                        f' {axis}2="{mark}" {cmpl}2="{v}"/>'
                    )
                output.append('  </g>')

        for element in self.elements:
            kind, pairs, color, *miscellania = element

            pairs = [
                (round(xconversion(x), 2), round(yconversion(y), 2))
                for x, y in pairs
            ]

            color, alpha = color_to_rgba(fallback(color, self.fgcolor))

            if kind == 'points':
                diameter, = miscellania

                if not diameter:
                    interpoint = sqrt(min(square_distances(pairs)))
                    # interpoint = round(interpoint, 2)
                    # interpoint = floor(interpoint * 2) / 2
                    # diameter = min(interpoint / 2, default_stroke * 2)
                    diameter = min(round(interpoint) / 2, default_stroke * 2)
                    diameter = max(1, diameter)

                radius = round(diameter / 2, 3)

                attributes = [
                    'stroke="none"',
                    f'fill="{color}"',
                ]
                if alpha < 1:
                    attributes.append(f'fill-opacity="{alpha}"')
                attributes = ' '.join(attributes)

                output.append(f'  <g {attributes}>')
                for x, y in pairs:
                    output.append(
                        f'    <circle cx="{x}" cy="{y}" r="{radius}"/>'
                    )
                output.append('  </g>')

            if kind == 'lines':
                stroke, gap, gapcolor = miscellania

                stroke = fallback(stroke, default_stroke)

                data = ' '.join(f'{x},{y}' for x, y in pairs)

                if gap:
                    gapstroke = stroke + gap * 2
                    gapcolor, gapalpha = color_to_rgba(
                        fallback(gapcolor, self.bgcolor)
                    )

                    attributes = [
                        'fill="none"',
                        f'stroke-width="{round(gapstroke, 2)}"',
                        f'stroke="{gapcolor}"',
                        'stroke-linecap="round"',
                        'stroke-linejoin="round"',
                    ]
                    if gapalpha < 1:
                        attributes.append(f'stroke-opacity="{gapalpha}"')
                    attributes = ' '.join(attributes)
                    output.append(f'  <polyline points="{data}" {attributes}/>')

                attributes = [
                    'fill="none"',
                    f'stroke-width="{round(stroke, 2)}"',
                    f'stroke="{color}"',
                    'stroke-linecap="round"',
                    'stroke-linejoin="round"',
                ]
                if alpha < 1:
                    attributes.append(f'stroke-opacity="{alpha}"')
                attributes = ' '.join(attributes)
                output.append(f'  <polyline points="{data}" {attributes}/>')

        output.append('</svg>')
        return '\n'.join(output)

# TODO unit for graticule (separate for radix)
#   e.g. drawing lines at multiples of 15
# TODO numeric labels

# svg = SVG(1024, 1024, margin=8, stroke=3)
# svg.add_graticule('x', stroke=1, divs=32, color=0.25)
# svg.add_graticule('y', stroke=1, divs=32, color=0.25)
# svg.add_graticule('x', stroke=3, divs=4,  color=0.25)
# svg.add_graticule('y', stroke=3, divs=4,  color=0.25)
# svg.add_rule('x', stroke=5, color=0.25)
# svg.add_rule('y', stroke=5, color=0.25)
# svg.add_lines(adaptive_sample(lambda x: 2 ** x,        -1, 1.4, 8), color=(0.7, 0.15,  45), gap=1, gapcolor=0)
# # svg.add_lines(adaptive_sample(lambda x: x,             -1, 1.4, 8), color=0.8,              gap=1, gapcolor=0)
# # svg.add_lines(adaptive_sample(lambda x: x * x,         -1, 1.4, 8), color=(0.7, 0.15, 285), gap=1, gapcolor=0)
# # svg.add_lines(adaptive_sample(lambda x: x * x * x,     -1, 1.4, 8), color=(0.7, 0.15,  30), gap=1, gapcolor=0)
# # svg.add_lines(adaptive_sample(lambda x: x * x * x * x, -1, 1.4, 8), color=(0.7, 0.15, 150), gap=1, gapcolor=0)
# svg.add_points(adaptive_sample(lambda x: 2 ** x,        -1, 1.4, 8), color=(0.7, 0.15,  45))
# svg.add_points(adaptive_sample(lambda x: x,             -1, 1.4, 8), color=0.8,            )
# svg.add_points(adaptive_sample(lambda x: x * x,         -1, 1.4, 8), color=(0.7, 0.15, 285))
# svg.add_points(adaptive_sample(lambda x: x * x * x,     -1, 1.4, 8), color=(0.7, 0.15,  30))
# svg.add_points(adaptive_sample(lambda x: x * x * x * x, -1, 1.4, 8), color=(0.7, 0.15, 150))
# print(svg.render())
