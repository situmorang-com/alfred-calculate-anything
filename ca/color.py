# -*- coding: utf-8 -*-
"""Color conversion (the `color` keyword).

    color #ff6600                    every format at once
    color #ff6600 to hsl             hsl(24, 100%, 50%)
    color rgb(255, 102, 0) to hex    #ff6600
    color tomato to cmyk             also understands CSS color names

Reads hex, rgb(a), hsl(a), hwb, hsv/hsb, cmyk, lab and oklch; writes those plus
xyz and yuv. The code for this existed in the original workflow but was never wired
to a keyword, and its hex output dropped leading zeros.
"""
import math
import os
import re

from .core import cache_dir, clean_query, item, message

NAMED = {
    'aliceblue': 'f0f8ff', 'antiquewhite': 'faebd7', 'aqua': '00ffff', 'aquamarine': '7fffd4', 'azure': 'f0ffff',
    'beige': 'f5f5dc', 'bisque': 'ffe4c4', 'black': '000000', 'blanchedalmond': 'ffebcd', 'blue': '0000ff',
    'blueviolet': '8a2be2', 'brown': 'a52a2a', 'burlywood': 'deb887', 'cadetblue': '5f9ea0',
    'chartreuse': '7fff00', 'chocolate': 'd2691e', 'coral': 'ff7f50', 'cornflowerblue': '6495ed',
    'cornsilk': 'fff8dc', 'crimson': 'dc143c', 'cyan': '00ffff', 'darkblue': '00008b', 'darkcyan': '008b8b',
    'darkgoldenrod': 'b8860b', 'darkgray': 'a9a9a9', 'darkgreen': '006400', 'darkgrey': 'a9a9a9',
    'darkkhaki': 'bdb76b', 'darkmagenta': '8b008b', 'darkolivegreen': '556b2f', 'darkorange': 'ff8c00',
    'darkorchid': '9932cc', 'darkred': '8b0000', 'darksalmon': 'e9967a', 'darkseagreen': '8fbc8f',
    'darkslateblue': '483d8b', 'darkslategray': '2f4f4f', 'darkslategrey': '2f4f4f', 'darkturquoise': '00ced1',
    'darkviolet': '9400d3', 'deeppink': 'ff1493', 'deepskyblue': '00bfff', 'dimgray': '696969',
    'dimgrey': '696969', 'dodgerblue': '1e90ff', 'firebrick': 'b22222', 'floralwhite': 'fffaf0',
    'forestgreen': '228b22', 'fuchsia': 'ff00ff', 'gainsboro': 'dcdcdc', 'ghostwhite': 'f8f8ff',
    'gold': 'ffd700', 'goldenrod': 'daa520', 'gray': '808080', 'green': '008000', 'greenyellow': 'adff2f',
    'grey': '808080', 'honeydew': 'f0fff0', 'hotpink': 'ff69b4', 'indianred': 'cd5c5c', 'indigo': '4b0082',
    'ivory': 'fffff0', 'khaki': 'f0e68c', 'lavender': 'e6e6fa', 'lavenderblush': 'fff0f5',
    'lawngreen': '7cfc00', 'lemonchiffon': 'fffacd', 'lightblue': 'add8e6', 'lightcoral': 'f08080',
    'lightcyan': 'e0ffff', 'lightgoldenrodyellow': 'fafad2', 'lightgray': 'd3d3d3', 'lightgreen': '90ee90',
    'lightgrey': 'd3d3d3', 'lightpink': 'ffb6c1', 'lightsalmon': 'ffa07a', 'lightseagreen': '20b2aa',
    'lightskyblue': '87cefa', 'lightslategray': '778899', 'lightslategrey': '778899',
    'lightsteelblue': 'b0c4de', 'lightyellow': 'ffffe0', 'lime': '00ff00', 'limegreen': '32cd32',
    'linen': 'faf0e6', 'magenta': 'ff00ff', 'maroon': '800000', 'mediumaquamarine': '66cdaa',
    'mediumblue': '0000cd', 'mediumorchid': 'ba55d3', 'mediumpurple': '9370db', 'mediumseagreen': '3cb371',
    'mediumslateblue': '7b68ee', 'mediumspringgreen': '00fa9a', 'mediumturquoise': '48d1cc',
    'mediumvioletred': 'c71585', 'midnightblue': '191970', 'mintcream': 'f5fffa', 'mistyrose': 'ffe4e1',
    'moccasin': 'ffe4b5', 'navajowhite': 'ffdead', 'navy': '000080', 'oldlace': 'fdf5e6', 'olive': '808000',
    'olivedrab': '6b8e23', 'orange': 'ffa500', 'orangered': 'ff4500', 'orchid': 'da70d6',
    'palegoldenrod': 'eee8aa', 'palegreen': '98fb98', 'paleturquoise': 'afeeee', 'palevioletred': 'db7093',
    'papayawhip': 'ffefd5', 'peachpuff': 'ffdab9', 'peru': 'cd853f', 'pink': 'ffc0cb', 'plum': 'dda0dd',
    'powderblue': 'b0e0e6', 'purple': '800080', 'rebeccapurple': '663399', 'red': 'ff0000',
    'rosybrown': 'bc8f8f', 'royalblue': '4169e1', 'saddlebrown': '8b4513', 'salmon': 'fa8072',
    'sandybrown': 'f4a460', 'seagreen': '2e8b57', 'seashell': 'fff5ee', 'sienna': 'a0522d', 'silver': 'c0c0c0',
    'skyblue': '87ceeb', 'slateblue': '6a5acd', 'slategray': '708090', 'slategrey': '708090', 'snow': 'fffafa',
    'springgreen': '00ff7f', 'steelblue': '4682b4', 'tan': 'd2b48c', 'teal': '008080', 'thistle': 'd8bfd8',
    'tomato': 'ff6347', 'turquoise': '40e0d0', 'violet': 'ee82ee', 'wheat': 'f5deb3', 'white': 'ffffff',
    'whitesmoke': 'f5f5f5', 'yellow': 'ffff00', 'yellowgreen': '9acd32',
}

FORMATS = ('hex', 'rgb', 'hsl', 'hwb', 'hsv', 'cmyk', 'lab', 'oklch', 'xyz', 'yuv')
SHOWN_BY_DEFAULT = ('hex', 'rgb', 'hsl', 'hwb', 'hsv', 'cmyk', 'lab', 'oklch')
ALIASES = {'rgba': 'rgb', 'hsla': 'hsl', 'hsb': 'hsv', 'cielab': 'lab', 'hexadecimal': 'hex', '#': 'hex'}


def _clamp(value, low=0.0, high=255.0):
    return max(low, min(high, value))


def _text(number, places=2):
    """A float without trailing zeros: 50.0 -> "50", 0.5 -> "0.5"."""
    out = ('%.*f' % (places, number)).rstrip('0').rstrip('.')
    return '0' if out in ('', '-0') else out


# --------------------------------------------------------------------------- to RGB

def from_hsl(hue, saturation, lightness):
    hue = hue % 360.0
    saturation, lightness = _clamp(saturation, 0, 1), _clamp(lightness, 0, 1)
    chroma = (1 - abs(2 * lightness - 1)) * saturation
    second = chroma * (1 - abs((hue / 60.0) % 2 - 1))
    base = lightness - chroma / 2.0
    sector = int(hue // 60) % 6
    red, green, blue = [(chroma, second, 0), (second, chroma, 0), (0, chroma, second),
                        (0, second, chroma), (second, 0, chroma), (chroma, 0, second)][sector]
    return ((red + base) * 255.0, (green + base) * 255.0, (blue + base) * 255.0)


def from_hsv(hue, saturation, value):
    hue = hue % 360.0
    saturation, value = _clamp(saturation, 0, 1), _clamp(value, 0, 1)
    chroma = value * saturation
    second = chroma * (1 - abs((hue / 60.0) % 2 - 1))
    base = value - chroma
    sector = int(hue // 60) % 6
    red, green, blue = [(chroma, second, 0), (second, chroma, 0), (0, chroma, second),
                        (0, second, chroma), (second, 0, chroma), (chroma, 0, second)][sector]
    return ((red + base) * 255.0, (green + base) * 255.0, (blue + base) * 255.0)


def from_hwb(hue, white, black):
    white, black = _clamp(white, 0, 1), _clamp(black, 0, 1)
    if white + black >= 1:
        gray = white / (white + black) * 255.0
        return (gray, gray, gray)
    pure = from_hsv(hue, 1.0, 1.0)
    return tuple(channel * (1 - white - black) + white * 255.0 for channel in pure)


def from_cmyk(cyan, magenta, yellow, key):
    return tuple(255.0 * (1 - _clamp(part, 0, 1)) * (1 - _clamp(key, 0, 1)) for part in (cyan, magenta, yellow))


def _companded(linear):
    return 12.92 * linear if linear <= 0.0031308 else 1.055 * (linear ** (1 / 2.4)) - 0.055


def _linear(channel):
    channel /= 255.0
    return channel / 12.92 if channel <= 0.04045 else ((channel + 0.055) / 1.055) ** 2.4


def from_xyz(x, y, z):
    x, y, z = x / 100.0, y / 100.0, z / 100.0
    red = x * 3.2404542 + y * -1.5371385 + z * -0.4985314
    green = x * -0.9692660 + y * 1.8760108 + z * 0.0415560
    blue = x * 0.0556434 + y * -0.2040259 + z * 1.0572252
    return tuple(_clamp(_companded(part) * 255.0) for part in (red, green, blue))


def from_lab(lightness, a, b):
    fy = (lightness + 16) / 116.0
    fx, fz = a / 500.0 + fy, fy - b / 200.0

    def expand(value):
        return value ** 3 if value ** 3 > 0.008856 else (value - 16 / 116.0) / 7.787
    return from_xyz(95.047 * expand(fx), 100.0 * expand(fy), 108.883 * expand(fz))


def from_oklch(lightness, chroma, hue):
    a, b = chroma * math.cos(math.radians(hue)), chroma * math.sin(math.radians(hue))
    long_ = (lightness + 0.3963377774 * a + 0.2158037573 * b) ** 3
    medium = (lightness - 0.1055613458 * a - 0.0638541728 * b) ** 3
    short = (lightness - 0.0894841775 * a - 1.2914855480 * b) ** 3
    red = 4.0767416621 * long_ - 3.3077115913 * medium + 0.2309699292 * short
    green = -1.2684380046 * long_ + 2.6097574011 * medium - 0.3413193965 * short
    blue = -0.0041960863 * long_ - 0.7034186147 * medium + 1.7076147010 * short
    return tuple(_clamp(_companded(max(part, 0.0)) * 255.0) for part in (red, green, blue))


# --------------------------------------------------------------------------- reading input

_NUMBER = r'-?\d*\.?\d+'


def _numbers(body):
    """Numbers inside the brackets, each with whether it carried a percent sign."""
    return [(float(value), bool(percent)) for value, percent in re.findall(r'(%s)\s*(%%?)' % _NUMBER, body)]


def _alpha(parts, index):
    if len(parts) <= index:
        return None
    value, percent = parts[index]
    return _clamp(value / 100.0 if percent else value, 0, 1)


def _unit(part):
    """A component given as 50% or 0.5 or 50 -> 0.5."""
    value, percent = part
    return value / 100.0 if (percent or value > 1) else value


def parse_color(text):
    """(red, green, blue, alpha) with channels 0-255 and alpha 0-1 or None; None if not a color."""
    text = text.strip().lower().rstrip(';')
    if not text:
        return None
    if text in NAMED:
        text = '#' + NAMED[text]
    match = re.match(r'^#?([0-9a-f]{8}|[0-9a-f]{6}|[0-9a-f]{3,4})$', text)
    if match:
        digits = match.group(1)
        if len(digits) in (3, 4):
            digits = ''.join(ch * 2 for ch in digits)
        channels = [int(digits[i:i + 2], 16) for i in range(0, len(digits), 2)]
        alpha = channels[3] / 255.0 if len(channels) == 4 else None
        return (float(channels[0]), float(channels[1]), float(channels[2]), alpha)
    match = re.match(r'^(rgba?|hsla?|hwb|hsva?|hsba?|cmyk|cielab|lab|oklch)\s*\(?([^()]*)\)?$', text)
    if match:
        kind, parts = match.group(1), _numbers(match.group(2))
        if kind in ('rgb', 'rgba') and len(parts) >= 3:
            channels = [_clamp(value * 2.55 if percent else value) for value, percent in parts[:3]]
            return (channels[0], channels[1], channels[2], _alpha(parts, 3))
        if kind in ('hsl', 'hsla') and len(parts) >= 3:
            red, green, blue = from_hsl(parts[0][0], _unit(parts[1]), _unit(parts[2]))
            return (red, green, blue, _alpha(parts, 3))
        if kind == 'hwb' and len(parts) >= 3:
            red, green, blue = from_hwb(parts[0][0], _unit(parts[1]), _unit(parts[2]))
            return (red, green, blue, _alpha(parts, 3))
        if kind in ('hsv', 'hsva', 'hsb', 'hsba') and len(parts) >= 3:
            red, green, blue = from_hsv(parts[0][0], _unit(parts[1]), _unit(parts[2]))
            return (red, green, blue, _alpha(parts, 3))
        if kind == 'cmyk' and len(parts) >= 4:
            red, green, blue = from_cmyk(*[_unit(part) for part in parts[:4]])
            return (red, green, blue, None)
        if kind in ('lab', 'cielab') and len(parts) >= 3:
            red, green, blue = from_lab(parts[0][0], parts[1][0], parts[2][0])
            return (red, green, blue, _alpha(parts, 3))
        if kind == 'oklch' and len(parts) >= 3:
            lightness = parts[0][0] / 100.0 if (parts[0][1] or parts[0][0] > 1) else parts[0][0]
            red, green, blue = from_oklch(lightness, parts[1][0], parts[2][0])
            return (red, green, blue, _alpha(parts, 3))
        return None
    match = re.match(r'^(\d{1,3})[ ,]+(\d{1,3})[ ,]+(\d{1,3})$', text)        # bare "255, 102, 0"
    if match:
        channels = [float(value) for value in match.groups()]
        if all(value <= 255 for value in channels):
            return (channels[0], channels[1], channels[2], None)
    return None


# --------------------------------------------------------------------------- writing output

def _hue_sat(red, green, blue):
    red, green, blue = red / 255.0, green / 255.0, blue / 255.0
    high, low = max(red, green, blue), min(red, green, blue)
    spread = high - low
    if spread == 0:
        hue = 0.0
    elif high == red:
        hue = 60.0 * (((green - blue) / spread) % 6)
    elif high == green:
        hue = 60.0 * ((blue - red) / spread + 2)
    else:
        hue = 60.0 * ((red - green) / spread + 4)
    return hue % 360.0, high, low, spread


def to_xyz(red, green, blue):
    red, green, blue = _linear(red) * 100.0, _linear(green) * 100.0, _linear(blue) * 100.0
    return (red * 0.4124564 + green * 0.3575761 + blue * 0.1804375,
            red * 0.2126729 + green * 0.7151522 + blue * 0.0721750,
            red * 0.0193339 + green * 0.1191920 + blue * 0.9503041)


def to_oklch(red, green, blue):
    red, green, blue = _linear(red), _linear(green), _linear(blue)
    long_ = (0.4122214708 * red + 0.5363325363 * green + 0.0514459929 * blue) ** (1 / 3.0)
    medium = (0.2119034982 * red + 0.6806995451 * green + 0.1073969566 * blue) ** (1 / 3.0)
    short = (0.0883024619 * red + 0.2817188376 * green + 0.6299787005 * blue) ** (1 / 3.0)
    lightness = 0.2104542553 * long_ + 0.7936177850 * medium - 0.0040720468 * short
    a = 1.9779984951 * long_ - 2.4285922050 * medium + 0.4505937099 * short
    b = 0.0259040371 * long_ + 0.7827717662 * medium - 0.8086757660 * short
    chroma = math.hypot(a, b)
    hue = math.degrees(math.atan2(b, a)) % 360.0 if chroma > 1e-4 else 0.0
    return lightness, chroma, hue


def render(kind, color):
    red, green, blue, alpha = color
    r, g, b = int(round(_clamp(red))), int(round(_clamp(green))), int(round(_clamp(blue)))
    translucent = alpha is not None and alpha < 1
    if kind == 'hex':
        out = '#%02x%02x%02x' % (r, g, b)
        return out + ('%02x' % int(round(alpha * 255)) if translucent else '')
    if kind == 'rgb':
        if translucent:
            return 'rgba(%d, %d, %d, %s)' % (r, g, b, _text(alpha))
        return 'rgb(%d, %d, %d)' % (r, g, b)
    hue, high, low, spread = _hue_sat(r, g, b)
    if kind == 'hsl':
        lightness = (high + low) / 2.0
        saturation = 0.0 if spread == 0 else spread / (1 - abs(2 * lightness - 1))
        body = '%d, %d%%, %d%%' % (round(hue) % 360, round(saturation * 100), round(lightness * 100))
        return 'hsla(%s, %s)' % (body, _text(alpha)) if translucent else 'hsl(%s)' % body
    if kind == 'hwb':
        return 'hwb(%d %d%% %d%%)' % (round(hue) % 360, round(low * 100), round((1 - high) * 100))
    if kind == 'hsv':
        saturation = 0.0 if high == 0 else spread / high
        return 'hsv(%d, %d%%, %d%%)' % (round(hue) % 360, round(saturation * 100), round(high * 100))
    if kind == 'cmyk':
        key = 1 - high
        if key >= 1:
            return 'cmyk(0%, 0%, 0%, 100%)'
        parts = [(1 - channel / 255.0 - key) / (1 - key) for channel in (r, g, b)]
        return 'cmyk(%d%%, %d%%, %d%%, %d%%)' % tuple(round(part * 100) for part in parts + [key])
    x, y, z = to_xyz(r, g, b)
    if kind == 'xyz':
        return 'color(xyz %s %s %s)' % (_text(x / 100.0, 4), _text(y / 100.0, 4), _text(z / 100.0, 4))
    if kind == 'lab':
        def squash(value):
            return value ** (1 / 3.0) if value > 0.008856 else 7.787 * value + 16 / 116.0
        fx, fy, fz = squash(x / 95.047), squash(y / 100.0), squash(z / 108.883)
        return 'lab(%s%% %s %s)' % (_text(116 * fy - 16), _text(500 * (fx - fy)), _text(200 * (fy - fz)))
    if kind == 'oklch':
        lightness, chroma, hue_ok = to_oklch(r, g, b)
        return 'oklch(%s%% %s %s)' % (_text(lightness * 100), _text(chroma, 4), _text(hue_ok))
    if kind == 'yuv':
        luma = 0.299 * r + 0.587 * g + 0.114 * b
        return 'yuv(%d, %d, %d)' % (round(luma), round((b - luma) * 0.493 + 128), round((r - luma) * 0.877 + 128))
    return ''


# --------------------------------------------------------------------------- swatch icon

def swatch(color):
    """A small PNG of the color so the result row shows what it looks like."""
    try:
        import struct
        import zlib
        r, g, b = [int(round(_clamp(part))) for part in color[:3]]
        folder = os.path.join(cache_dir(), 'swatches')
        os.makedirs(folder, exist_ok=True)
        path = os.path.join(folder, '%02x%02x%02x.png' % (r, g, b))
        if os.path.exists(path):
            return path
        if len(os.listdir(folder)) > 300:              # typing a color creates one per keystroke
            for name in os.listdir(folder):
                try:
                    os.remove(os.path.join(folder, name))
                except OSError:
                    pass
        size, radius = 64, 14
        edge = max(0, r - 40), max(0, g - 40), max(0, b - 40)   # keeps pale colors visible on a light theme
        rows = bytearray()
        for y in range(size):
            rows.append(0)
            for x in range(size):
                dx = max(radius - x, 0, x - (size - 1 - radius))
                dy = max(radius - y, 0, y - (size - 1 - radius))
                distance = math.hypot(dx, dy)
                if distance > radius:
                    rows.extend((0, 0, 0, 0))
                elif distance > radius - 2 or min(x, y, size - 1 - x, size - 1 - y) < 2:
                    rows.extend((edge[0], edge[1], edge[2], 255))
                else:
                    rows.extend((r, g, b, 255))

        def chunk(tag, data):
            return (struct.pack('>I', len(data)) + tag + data +
                    struct.pack('>I', zlib.crc32(tag + data) & 0xffffffff))
        png = (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', size, size, 8, 6, 0, 0, 0)) +
               chunk(b'IDAT', zlib.compress(bytes(rows), 9)) + chunk(b'IEND', b''))
        with open(path, 'wb') as handle:
            handle.write(png)
        return path
    except Exception:
        return None


# --------------------------------------------------------------------------- the keyword

def keyword(ctx, query):
    strings = ctx.lang.section('color')
    invalid = [message('...', strings.get('notvalid_subtitle') or 'Enter a valid color')]
    text = clean_query(query or '')
    if not text:
        return invalid

    target = ''
    stops = ctx.lang.stop_words('color')
    words = text.split(' ')
    if len(words) > 1:
        last = ALIASES.get(words[-1], words[-1])
        before = words[:-1]
        had_stop = bool(before) and before[-1] in stops
        if had_stop:
            before = before[:-1]
        if last in FORMATS and before:
            target, text = last, ' '.join(before)
        elif had_stop:
            color = parse_color(' '.join(before))
            if color is None:
                return invalid
            return [message((strings.get('unsupported') or 'There is no support for the %s color space yet')
                            % words[-1])]

    color = parse_color(text)
    if color is None:
        trimmed = ' '.join(word for word in text.split(' ') if word not in stops)
        color = parse_color(trimmed)
    if color is None:
        return invalid

    icon = swatch(color)
    hint = strings.get('copy') or ctx.text('general', 'action_copy')
    rows = []
    for kind in ([target] if target else SHOWN_BY_DEFAULT):
        value = render(kind, color)
        rows.append(item(value, '%s  ·  %s' % (kind.upper(), hint), arg=value, icon=icon))
    return rows
