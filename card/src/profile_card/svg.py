from xml.sax.saxutils import escape

from .spec import Spec
from .typeset import Face, Run, fmt


def card_svg(spec: Spec, face: Face, watermark: Face) -> str:
    card = spec.card
    w, h = card.width, card.height
    ox, oy = card.offset
    cw, ch = w + 2 * ox, h + oy + card.bottom
    ink = " ".join(
        Run(face, ln.text, ln.size * card.size_scale, ln.tracking).path(ln.x, ln.y, ln.anchor) for ln in card.lines
    )
    wm = card.watermark
    mark = Run(watermark, wm.text, wm.size, wm.tracking).path(wm.x, wm.y, wm.anchor)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {cw} {ch}" width="{cw}" height="{ch}" role="img" aria-labelledby="t">
<title id="t">{escape(card.alt)}</title>
<defs>
<filter id="drop" x="-10%" y="-10%" width="120%" height="135%">
<feGaussianBlur in="SourceAlpha" stdDeviation="17"/><feOffset dy="20" result="o1"/>
<feComponentTransfer in="o1" result="s1"><feFuncA type="linear" slope="0.30"/></feComponentTransfer>
<feGaussianBlur in="SourceAlpha" stdDeviation="1.4"/><feOffset dy="1.6" result="o2"/>
<feComponentTransfer in="o2" result="s2"><feFuncA type="linear" slope="0.30"/></feComponentTransfer>
<feMerge><feMergeNode in="s1"/><feMergeNode in="s2"/><feMergeNode in="SourceGraphic"/></feMerge>
</filter>
<filter id="grain" x="0" y="0" width="100%" height="100%">
<feTurbulence type="fractalNoise" baseFrequency="0.95" numOctaves="3" seed="11" stitchTiles="stitch"/>
<feColorMatrix type="matrix" values="0 0 0 0 0.25  0 0 0 0 0.21  0 0 0 0 0.15  1.1 0 0 0 -0.46"/>
</filter>
<filter id="fiber" x="0" y="0" width="100%" height="100%">
<feTurbulence type="fractalNoise" baseFrequency="0.006 0.22" numOctaves="2" seed="4"/>
<feColorMatrix type="matrix" values="0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  1.4 0 0 0 -0.62"/>
</filter>
<filter id="soft" x="-5%" y="-5%" width="110%" height="110%"><feGaussianBlur stdDeviation="0.45"/></filter>
<filter id="wmblur" x="-5%" y="-5%" width="110%" height="110%"><feGaussianBlur stdDeviation="3"/></filter>
<linearGradient id="light" x1="0" y1="0" x2="1" y2="1">
<stop offset="0" stop-color="#fff" stop-opacity="0.34"/>
<stop offset="0.5" stop-color="#fff" stop-opacity="0"/>
<stop offset="1" stop-color="#000" stop-opacity="0.07"/>
</linearGradient>
<clipPath id="stock"><rect width="{w}" height="{h}" rx="5"/></clipPath>
<path id="ink" d="{ink}"/>
</defs>
<g transform="translate({ox} {oy})">
<rect width="{w}" height="{h}" rx="5" fill="{card.stock}" filter="url(#drop)"/>
<g clip-path="url(#stock)">
<rect width="{w}" height="{h}" filter="url(#fiber)" opacity="0.30"/>
<rect width="{w}" height="{h}" filter="url(#grain)" opacity="0.55"/>
<path d="{mark}" fill="#fff" opacity="0.13" filter="url(#wmblur)"/>
<rect width="{w}" height="{h}" fill="url(#light)"/>
</g>
<rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="5" fill="none" stroke="#000" stroke-opacity="0.07"/>
<use href="#ink" fill="#000" opacity="0.26" transform="translate(0.8 1.1)" filter="url(#soft)"/>
<use href="#ink" fill="#fff" opacity="0.55" transform="translate(-0.6 -0.6)"/>
<use href="#ink" fill="{card.ink}"/>
</g>
</svg>
"""


def signature_svg(spec: Spec, face: Face, color: str) -> str:
    sig = spec.signature
    run = Run(face, sig.text, sig.size, 0.0)
    x0, y0, x1, y1 = run.bounds(0, 0)
    pad = sig.pad
    d = run.path(-x0 + pad, -y0 + pad)
    w, h = (x1 - x0) + 2 * pad, (y1 - y0) + 2 * pad
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {fmt(w)} {fmt(h)}" width="{fmt(w)}" height="{fmt(h)}" role="img" aria-label="{escape(sig.text, {'"': "&quot;"})}"><path d="{d}" fill="{color}"/></svg>
"""


def assets(spec: Spec, card_face: Face, watermark_face: Face, signature_face: Face) -> dict[str, str]:
    return {
        "card.svg": card_svg(spec, card_face, watermark_face),
        "signature-light.svg": signature_svg(spec, signature_face, spec.signature.light),
        "signature-dark.svg": signature_svg(spec, signature_face, spec.signature.dark),
    }
