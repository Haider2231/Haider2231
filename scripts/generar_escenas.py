"""Genera todas las escenas animadas del perfil.

Uso:  python scripts/generar_escenas.py
Lee assets/fuentes/*.jpg y escribe en assets/:
  banner-vivo.svg      el banner con ojos, rayos y brasas animados
  antimagia.svg        Black Asta con "Supera tus límites. Aquí y ahora."
  sistema.svg          ventana de estado estilo Solo Leveling
  arise.svg            Igris y el ejército de sombras de Jin-Woo
  camino-*.svg         las tarjetas de los tres caminos
"""

import base64
import io
import math
import random
from pathlib import Path

from PIL import Image

RAIZ = Path(__file__).resolve().parent.parent
ASSETS = RAIZ / "assets"
BANNER = ASSETS / "fuentes" / "banner.jpg"
ASTA = ASSETS / "fuentes" / "asta.jpg"
IGRIS = ASSETS / "fuentes" / "igris.jpg"
EJERCITO = ASSETS / "fuentes" / "ejercito.jpg"

FUENTE_TITULO = "'Arial Black', 'Segoe UI Black', Impact, 'Helvetica Neue', Arial, sans-serif"
FUENTE_TEXTO = "'Segoe UI', 'Helvetica Neue', Arial, sans-serif"
FUENTE_MONO = "'Consolas', 'Courier New', monospace"

MOVIMIENTO_REDUCIDO = """
    @media (prefers-reduced-motion: reduce) {
      * { animation: none !important; }
      .solo-animado { display: none; }
    }"""


# ---------------------------------------------------------------- utilidades

def jpeg_base64(img: Image.Image, calidad: int = 82) -> str:
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=calidad, optimize=True, progressive=True)
    return base64.b64encode(buf.getvalue()).decode("ascii")


def rayo(rng: random.Random, x0, y0, x1, y1, pasos=9, desvio=18) -> str:
    """Camino quebrado entre dos puntos, como un relámpago."""
    puntos = [(x0, y0)]
    for i in range(1, pasos):
        t = i / pasos
        x = x0 + (x1 - x0) * t + rng.uniform(-desvio, desvio)
        y = y0 + (y1 - y0) * t + rng.uniform(-desvio / 2, desvio / 2)
        puntos.append((x, y))
    puntos.append((x1, y1))
    return "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in puntos)


def llamas(rng: random.Random, x0, x1, base, alto_min, alto_max, ancho=38) -> str:
    """Lenguas de fuego a lo largo de una línea base."""
    d = [f"M {x0} {base + 40}", f"L {x0} {base}"]
    x = x0
    while x < x1:
        w = rng.uniform(ancho * 0.6, ancho * 1.3)
        h = rng.uniform(alto_min, alto_max)
        punta = x + w / 2 + rng.uniform(-w * 0.3, w * 0.3)
        d.append(
            f"C {x + w * 0.1:.1f} {base - h * 0.45:.1f} {punta - w * 0.15:.1f} {base - h * 0.75:.1f} {punta:.1f} {base - h:.1f}"
        )
        d.append(
            f"C {punta + w * 0.1:.1f} {base - h * 0.7:.1f} {x + w * 0.9:.1f} {base - h * 0.4:.1f} {x + w:.1f} {base:.1f}"
        )
        x += w
    d.append(f"L {x:.1f} {base + 40} Z")
    return " ".join(d)


def chispas(rng: random.Random, n, x0, x1, y, colores, clase="chispa", r=(1.5, 3.5), dur=(3.0, 5.5)) -> str:
    out = []
    for _ in range(n):
        out.append(
            f'<circle cx="{rng.uniform(x0, x1):.0f}" cy="{y}" r="{rng.uniform(*r):.1f}" fill="{rng.choice(colores)}" '
            f'class="{clase} solo-animado" style="animation-delay:{rng.uniform(0, 5):.2f}s;animation-duration:{rng.uniform(*dur):.2f}s"/>'
        )
    return "\n    ".join(out)


def trebol(r: float, relleno: str, borde: str, ancho_borde: float = 2) -> str:
    """Trébol de cinco hojas (grimorio de Asta), centrado en el origen."""
    s = r / 70
    hoja = (
        f"M 0 0 C {-30*s:.1f} {-20*s:.1f} {-46*s:.1f} {-55*s:.1f} {-23*s:.1f} {-70*s:.1f} "
        f"C {-10*s:.1f} {-78*s:.1f} 0 {-68*s:.1f} 0 {-58*s:.1f} "
        f"C 0 {-68*s:.1f} {10*s:.1f} {-78*s:.1f} {23*s:.1f} {-70*s:.1f} "
        f"C {46*s:.1f} {-55*s:.1f} {30*s:.1f} {-20*s:.1f} 0 0 Z"
    )
    hojas = "".join(
        f'<path d="{hoja}" transform="rotate({i * 72})" fill="{relleno}" stroke="{borde}" stroke-width="{ancho_borde}" stroke-linejoin="round"/>'
        for i in range(5)
    )
    tallo = f'<path d="M 0 0 Q {8*s:.1f} {30*s:.1f} {-6*s:.1f} {58*s:.1f}" stroke="{borde}" stroke-width="{ancho_borde * 1.6}" fill="none" stroke-linecap="round"/>'
    return tallo + hojas


# ------------------------------------------------------------ banner vivo

def banner_vivo() -> str:
    banner = Image.open(BANNER).convert("RGB")
    w, h = banner.size
    rng = random.Random(7)

    # Ojos y destellos ubicados sobre la imagen (coordenadas del banner 1280x558)
    ojos_sombras = [(352, 31), (375, 29), (162, 114), (177, 115), (770, 175), (790, 175),
                    (850, 195), (867, 195), (987, 122), (1005, 125), (1075, 217), (1085, 218),
                    (1190, 222), (1202, 222), (239, 174), (252, 167)]
    ojos_jinwoo = [(647, 77), (698, 106)]
    lanzas = [(1075, 45), (1170, 140)]

    ojos = []
    for i, (x, y) in enumerate(ojos_sombras):
        ojos.append(f'<circle cx="{x}" cy="{y}" r="5" fill="#A5B4FC" class="ojo" style="animation-delay:{rng.uniform(0, 3):.2f}s"/>')
    for x, y in ojos_jinwoo:
        ojos.append(f'<circle cx="{x}" cy="{y}" r="9" fill="#60A5FA" class="ojo-jinwoo"/>')
    destellos = []
    for i, (x, y) in enumerate(lanzas):
        destellos.append(
            f'<g transform="translate({x} {y})"><g class="destello" style="animation-delay:{1.2 + i * 2.1}s">'
            f'<path d="M 0 -26 L 3 -3 L 26 0 L 3 3 L 0 26 L -3 3 L -26 0 L -3 -3 Z" fill="#E0E7FF"/>'
            f'<circle r="6" fill="#FFFFFF"/></g></g>'
        )

    rayos = []
    zonas = [(300, 60, 380, 220), (440, 120, 520, 260), (820, 140, 900, 280), (930, 60, 1010, 200), (60, 150, 140, 300)]
    for i, (a, b, c, d) in enumerate(zonas):
        path = rayo(rng, a, b, c, d, pasos=8, desvio=22)
        rayos.append(
            f'<g class="rayo solo-animado" style="animation-delay:{i * 1.37:.2f}s">'
            f'<path d="{path}" stroke="#A855F7" stroke-width="6" fill="none" filter="url(#brilloRayo)"/>'
            f'<path d="{path}" stroke="#F5F3FF" stroke-width="1.8" fill="none"/></g>'
        )

    css = """
    .ojo { animation: ojo 3.2s ease-in-out infinite; opacity: 0; }
    @keyframes ojo { 0%, 100% { opacity: 0.15; } 50% { opacity: 0.95; } }
    .ojo-jinwoo { animation: jinwoo 2.6s ease-in-out infinite; }
    @keyframes jinwoo { 0%, 100% { opacity: 0.35; } 50% { opacity: 1; } }
    .destello { animation: destello 4.2s ease-out infinite; opacity: 0; transform-box: fill-box; transform-origin: center; }
    @keyframes destello { 0%, 70%, 100% { opacity: 0; transform: scale(0.2) rotate(0deg); } 76% { opacity: 1; transform: scale(1) rotate(45deg); } 86% { opacity: 0; transform: scale(0.4) rotate(90deg); } }
    .rayo { animation: rayo 6.8s steps(1) infinite; opacity: 0; }
    @keyframes rayo { 0%, 100% { opacity: 0; } 80% { opacity: 1; } 81.5% { opacity: 0.1; } 83% { opacity: 1; } 85% { opacity: 0; } }
    .brasa { animation: brasa 4s ease-in infinite; opacity: 0; }
    @keyframes brasa { 0% { opacity: 0; transform: translate(0, 0); } 15% { opacity: 1; } 100% { opacity: 0; transform: translate(-40px, -260px); } }
    .niebla { animation: niebla 14s ease-in-out infinite alternate; }
    @keyframes niebla { from { transform: translateX(-60px); } to { transform: translateX(60px); } }
    .aviso { animation: aviso 9s ease-in-out 1s infinite; opacity: 0; }
    @keyframes aviso { 0% { opacity: 0; transform: translateY(-14px); } 6%, 60% { opacity: 1; transform: none; } 68%, 100% { opacity: 0; transform: none; } }
    .aviso-texto { font: 700 15px """ + FUENTE_MONO + """; letter-spacing: 1px; }
    """ + MOVIMIENTO_REDUCIDO

    return f"""<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="t">
  <title id="t">Ayanokoji, Sung Jin-Woo y Asta con el ejército de sombras</title>
  <defs>
    <filter id="brilloOjo" x="-200%" y="-200%" width="500%" height="500%"><feGaussianBlur stdDeviation="4"/></filter>
    <filter id="brilloRayo" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="4"/></filter>
    <filter id="borroso" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="28"/></filter>
    <radialGradient id="vineta" cx="50%" cy="45%" r="75%">
      <stop offset="0.6" stop-color="#000" stop-opacity="0"/>
      <stop offset="1" stop-color="#000" stop-opacity="0.55"/>
    </radialGradient>
  </defs>
  <style>{css}</style>

  <image width="{w}" height="{h}" href="data:image/jpeg;base64,{jpeg_base64(banner)}"/>

  <g class="niebla solo-animado" filter="url(#borroso)" opacity="0.45">
    <ellipse cx="240" cy="330" rx="260" ry="40" fill="#6D28D9"/>
    <ellipse cx="760" cy="300" rx="220" ry="34" fill="#4C1D95"/>
  </g>
  <g filter="url(#brilloOjo)">
    {"".join(ojos)}
  </g>
  {"".join(rayos)}
  {"".join(destellos)}
  <g>
    {chispas(rng, 26, 860, 1280, h, ["#EF4444", "#F97316", "#DC2626", "#FCA5A5"], clase="brasa", r=(1.5, 3.8))}
  </g>
  <rect width="{w}" height="{h}" fill="url(#vineta)"/>

  <g class="aviso solo-animado" transform="translate(28 26)">
    <rect width="370" height="46" rx="6" fill="#030712" fill-opacity="0.78" stroke="#60A5FA" stroke-width="1.5"/>
    <circle cx="24" cy="23" r="11" fill="none" stroke="#60A5FA" stroke-width="2"/>
    <text x="24" y="28" text-anchor="middle" class="aviso-texto" fill="#60A5FA">!</text>
    <text x="46" y="28" class="aviso-texto" fill="#DBEAFE">[SISTEMA] Jugador detectado: Haider</text>
  </g>
</svg>
"""


# --------------------------------------------------------------- antimagia

def mascara(img: Image.Image, condicion, desenfoque: float = 1.5) -> str:
    """Máscara en escala de grises (JPEG base64) con los píxeles que cumplen la condición."""
    from PIL import ImageFilter

    datos = [255 if condicion(*p) else 0 for p in img.get_flattened_data()]
    m = Image.new("L", img.size)
    m.putdata(datos)
    m = m.filter(ImageFilter.GaussianBlur(desenfoque))
    buf = io.BytesIO()
    m.save(buf, format="JPEG", quality=70, optimize=True)
    return base64.b64encode(buf.getvalue()).decode("ascii")


def antimagia() -> str:
    rng = random.Random(11)
    W, H = 1000, 520
    asta = Image.open(ASTA).convert("RGB").resize((1000, 1777), Image.LANCZOS).crop((0, 630, 1000, 1150))
    base = jpeg_base64(asta, 80)
    m_rojo = mascara(asta, lambda r, g, b: r > 200 and g < 60 and b < 60, 2)
    m_rayos = mascara(asta, lambda r, g, b: r > 235 and r - g > 60 and g > 60, 1.2)
    m_violeta = mascara(asta, lambda r, g, b: b > 140 and b - g > 70 and r > 70, 2)
    ojos = [(454, 224), (535, 224)]

    rayos_negros = []
    for i, (a, b, c, d) in enumerate([(30, 20, 130, 260), (970, 20, 870, 260)]):
        path = rayo(rng, a, b, c, d, pasos=10, desvio=26)
        rayos_negros.append(
            f'<g class="rayo-negro solo-animado" style="animation-delay:{0.6 + i * 1.6:.2f}s">'
            f'<path d="{path}" stroke="#EF4444" stroke-width="9" fill="none" filter="url(#neon)"/>'
            f'<path d="{path}" stroke="#000000" stroke-width="4" fill="none" stroke-linejoin="bevel"/>'
            f'<path d="{path}" stroke="#FCA5A5" stroke-width="0.8" fill="none"/></g>'
        )

    css = """
    .titulo { font: 900 74px """ + FUENTE_TITULO + """; }
    .ahora  { font: 900 60px """ + FUENTE_TITULO + """; }
    .etiqueta { font: 700 14px """ + FUENTE_MONO + """; letter-spacing: 6px; }
    .cita { font: italic 400 15px """ + FUENTE_TEXTO + """; }

    .entra   { animation: entrar 0.9s cubic-bezier(.2,.9,.3,1.2) 0.3s both; }
    .entra-2 { animation: entrar 0.9s cubic-bezier(.2,.9,.3,1.2) 0.75s both; }
    .entra-3 { animation: aparecer 1.2s ease 1.3s both; }
    @keyframes entrar { from { opacity: 0; transform: translateY(26px); } to { opacity: 1; transform: none; } }
    @keyframes aparecer { from { opacity: 0; } to { opacity: 1; } }

    .camara { animation: camara 18s ease-in-out infinite alternate; transform-origin: 495px 230px; }
    @keyframes camara { from { transform: scale(1); } to { transform: scale(1.07); } }
    .sacudida { animation: sacudir 5.5s linear 2.2s infinite; }
    @keyframes sacudir {
      0%, 4%, 12%, 100% { transform: none; }
      5% { transform: translate(-7px, 4px); } 6% { transform: translate(6px, -5px); }
      7% { transform: translate(-5px, -3px); } 8% { transform: translate(4px, 4px); }
      9% { transform: translate(-2px, 1px); } 10% { transform: translate(1px, -1px); }
    }

    .marcas { animation: marcas 2.4s ease-in-out infinite; }
    @keyframes marcas { 0%, 100% { opacity: 0; } 50% { opacity: 0.45; } }
    .relampago { animation: relampago 3.7s steps(1) infinite; opacity: 0; }
    @keyframes relampago { 0%, 100% { opacity: 0; } 62% { opacity: 1; } 64% { opacity: 0.2; } 66% { opacity: 0.9; } 70% { opacity: 0; } 88% { opacity: 0.7; } 90% { opacity: 0; } }
    .haz { animation: haz 1.6s ease-in-out infinite; }
    @keyframes haz { 0%, 100% { opacity: 0.3; } 50% { opacity: 1; } }
    .ojo { animation: ojo 2.4s ease-in-out infinite; }
    @keyframes ojo { 0%, 100% { opacity: 0.4; } 50% { opacity: 1; } }

    .humo-1 { animation: humo 16s ease-in-out infinite alternate; }
    .humo-2 { animation: humo 12s ease-in-out infinite alternate-reverse; }
    @keyframes humo { from { transform: translateX(-80px); } to { transform: translateX(80px); } }

    .pulso { animation: pulso 1.8s ease-in-out infinite; }
    @keyframes pulso { 0%, 100% { opacity: 0.55; } 50% { opacity: 1; } }
    .barrido { animation: barrer 5s ease-in-out 1.6s infinite; }
    @keyframes barrer { 0% { transform: translateX(-320px); } 35%, 100% { transform: translateX(1100px); } }
    .glitch-a { animation: glitchA 4.2s steps(1) 2s infinite; opacity: 0; }
    .glitch-b { animation: glitchB 4.2s steps(1) 2s infinite; opacity: 0; }
    @keyframes glitchA { 0%, 89%, 100% { opacity: 0; transform: none; } 90% { opacity: .85; transform: translate(-6px, 2px); } 93% { opacity: .85; transform: translate(4px, -2px); } 96% { opacity: .85; transform: translate(-3px, 0); } }
    @keyframes glitchB { 0%, 89%, 100% { opacity: 0; transform: none; } 90% { opacity: .85; transform: translate(6px, -2px); } 93% { opacity: .85; transform: translate(-4px, 2px); } 96% { opacity: .85; transform: translate(3px, 1px); } }

    .revela { stroke-dasharray: 1500; stroke-dashoffset: 1500; animation: revelar 5.5s cubic-bezier(.7,0,.2,1) 2.2s infinite; }
    @keyframes revelar { 0% { stroke-dashoffset: 1500; } 5%, 100% { stroke-dashoffset: 0; } }
    .tajo { animation: tajo 5.5s ease-out 2.2s infinite; opacity: 0; }
    @keyframes tajo { 0% { opacity: 1; } 8% { opacity: 1; } 18%, 100% { opacity: 0; } }
    .destello-tajo { animation: flash 5.5s ease-out 2.2s infinite; opacity: 0; }
    @keyframes flash { 0%, 100% { opacity: 0; } 4% { opacity: 0.22; } 9% { opacity: 0; } }

    .rayo-negro { animation: rayo 5.2s steps(1) infinite; opacity: 0; }
    @keyframes rayo { 0%, 100% { opacity: 0; } 78% { opacity: 1; } 80% { opacity: 0.15; } 82% { opacity: 1; } 85% { opacity: 0; } }
    .chispa { animation: subir 4s ease-in infinite; opacity: 0; }
    @keyframes subir { 0% { opacity: 0; transform: translateY(0); } 15% { opacity: 1; } 100% { opacity: 0; transform: translateY(-360px); } }
    .parpadeo { animation: parpadear 1.1s steps(1) infinite; }
    @keyframes parpadear { 50% { opacity: 0; } }
    """ + MOVIMIENTO_REDUCIDO

    tajo = "M 40 470 Q 470 420 965 60 Q 540 370 40 470 Z"
    filo = "M 40 470 Q 500 400 965 60"
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="t d">
  <title id="t">Supera tus límites. Aquí y ahora.</title>
  <desc id="d">Black Asta (Black Clover) en modo demonio, con antimagia animada y la frase "Supera tus límites. Aquí y ahora."</desc>
  <defs>
    <clipPath id="marco"><rect width="{W}" height="{H}" rx="18"/></clipPath>
    <mask id="mRojo" maskUnits="userSpaceOnUse" x="0" y="0" width="{W}" height="{H}"><image width="{W}" height="{H}" href="data:image/jpeg;base64,{m_rojo}"/></mask>
    <mask id="mRayos" maskUnits="userSpaceOnUse" x="0" y="0" width="{W}" height="{H}"><image width="{W}" height="{H}" href="data:image/jpeg;base64,{m_rayos}"/></mask>
    <mask id="mVioleta" maskUnits="userSpaceOnUse" x="0" y="0" width="{W}" height="{H}"><image width="{W}" height="{H}" href="data:image/jpeg;base64,{m_violeta}"/></mask>
    <mask id="mascaraTajo" maskUnits="userSpaceOnUse" x="0" y="0" width="{W}" height="{H}">
      <path d="{filo}" stroke="#FFFFFF" stroke-width="110" fill="none" class="revela"/>
    </mask>
    <linearGradient id="sombraTexto" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#000" stop-opacity="0"/>
      <stop offset="0.45" stop-color="#000" stop-opacity="0.7"/>
      <stop offset="1" stop-color="#000" stop-opacity="0.92"/>
    </linearGradient>
    <linearGradient id="sombraArriba" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#000" stop-opacity="0.75"/>
      <stop offset="1" stop-color="#000" stop-opacity="0"/>
    </linearGradient>
    <radialGradient id="tinte" cx="50%" cy="38%" r="65%">
      <stop offset="0.5" stop-color="#000000" stop-opacity="0"/>
      <stop offset="1" stop-color="#000000" stop-opacity="0.45"/>
    </radialGradient>
    <linearGradient id="metal" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#FFFFFF"/>
      <stop offset="0.55" stop-color="#FECACA"/>
      <stop offset="1" stop-color="#EF4444"/>
    </linearGradient>
    <linearGradient id="brillo" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#FFFFFF" stop-opacity="0"/>
      <stop offset="0.5" stop-color="#FFFFFF" stop-opacity="0.9"/>
      <stop offset="1" stop-color="#FFFFFF" stop-opacity="0"/>
    </linearGradient>
    <filter id="neon" x="-20%" y="-50%" width="140%" height="200%">
      <feGaussianBlur stdDeviation="7" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <filter id="resplandor" x="-5%" y="-5%" width="110%" height="110%">
      <feGaussianBlur stdDeviation="5" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <filter id="borroso" x="-50%" y="-100%" width="200%" height="300%"><feGaussianBlur stdDeviation="30"/></filter>
    <filter id="brilloOjo" x="-300%" y="-300%" width="700%" height="700%"><feGaussianBlur stdDeviation="5"/></filter>
    <clipPath id="recorteTitulo">
      <text x="500" y="420" text-anchor="middle" class="titulo" textLength="880" lengthAdjust="spacingAndGlyphs">SUPERA TUS LÍMITES</text>
    </clipPath>
  </defs>
  <style>{css}</style>

  <g clip-path="url(#marco)">
    <rect width="{W}" height="{H}" fill="#050505"/>
    <g class="sacudida">
      <g class="camara">
        <image width="{W}" height="{H}" href="data:image/jpeg;base64,{base}"/>
        <!-- Marcas rojas que palpitan -->
        <g filter="url(#resplandor)" class="marcas">
          <rect width="{W}" height="{H}" fill="#FF4D4D" mask="url(#mRojo)"/>
        </g>
        <!-- Haz violeta central -->
        <g filter="url(#resplandor)" class="haz">
          <rect width="{W}" height="{H}" fill="#C084FC" mask="url(#mVioleta)"/>
        </g>
        <!-- Rayos blancos de la imagen que destellan -->
        <g filter="url(#resplandor)" class="relampago solo-animado">
          <rect width="{W}" height="{H}" fill="#FFE4E6" mask="url(#mRayos)"/>
        </g>
        <g filter="url(#brilloOjo)">
          {"".join(f'<circle cx="{x}" cy="{y}" r="9" fill="#FF3B3B" class="ojo"/>' for x, y in ojos)}
        </g>
      </g>
    </g>
    <rect width="{W}" height="{H}" fill="url(#tinte)"/>

    <!-- Humo -->
    <g filter="url(#borroso)" opacity="0.3" class="solo-animado">
      <ellipse cx="200" cy="470" rx="260" ry="45" fill="#9CA3AF" class="humo-1"/>
      <ellipse cx="820" cy="450" rx="240" ry="40" fill="#6B7280" class="humo-2"/>
    </g>

    {"".join(rayos_negros)}
    <g>{chispas(rng, 22, 20, 980, H, ["#EF4444", "#F87171", "#DC2626", "#111111"], r=(1.5, 3.5))}</g>

    <rect width="{W}" height="120" fill="url(#sombraArriba)"/>
    <rect y="300" width="{W}" height="220" fill="url(#sombraTexto)"/>

    <!-- Etiqueta -->
    <g class="entra">
      <g transform="translate(283 40) scale(0.12)">{trebol(70, "#000000", "#EF4444", 10)}</g>
      <text x="500" y="45" text-anchor="middle" class="etiqueta" fill="#FCA5A5">MI MAGIA ES NO RENDIRME<tspan class="parpadeo" fill="#FFFFFF"> _</tspan></text>
      <g transform="translate(717 40) scale(0.12)">{trebol(70, "#000000", "#EF4444", 10)}</g>
    </g>

    <!-- SUPERA TUS LÍMITES -->
    <g class="entra">
      <text x="500" y="420" text-anchor="middle" class="titulo" textLength="880" lengthAdjust="spacingAndGlyphs" fill="#000000" opacity="0.6" transform="translate(0 4)">SUPERA TUS LÍMITES</text>
      <text x="500" y="420" text-anchor="middle" class="titulo" textLength="880" lengthAdjust="spacingAndGlyphs" fill="url(#metal)">SUPERA TUS LÍMITES</text>
    </g>
    <g clip-path="url(#recorteTitulo)">
      <g transform="skewX(-20)">
        <rect x="150" y="340" width="160" height="100" fill="url(#brillo)" class="barrido"/>
      </g>
    </g>

    <!-- AQUÍ Y AHORA. -->
    <g class="entra-2">
      <text x="500" y="486" text-anchor="middle" class="ahora glitch-a" textLength="500" lengthAdjust="spacingAndGlyphs" fill="#A855F7">AQUÍ Y AHORA.</text>
      <text x="500" y="486" text-anchor="middle" class="ahora glitch-b" textLength="500" lengthAdjust="spacingAndGlyphs" fill="#000000">AQUÍ Y AHORA.</text>
      <text x="500" y="486" text-anchor="middle" class="ahora pulso" textLength="500" lengthAdjust="spacingAndGlyphs" fill="#DC2626" filter="url(#neon)">AQUÍ Y AHORA.</text>
      <text x="500" y="486" text-anchor="middle" class="ahora" textLength="500" lengthAdjust="spacingAndGlyphs" fill="#FFF1F2">AQUÍ Y AHORA.</text>
    </g>
    <text x="500" y="510" text-anchor="middle" class="cita entra-3" fill="#D1D5DB">“Surpass your limits. Right here, right now.” — Black Clover</text>

    <!-- Tajo de espada antimagia -->
    <rect width="{W}" height="{H}" fill="#FEE2E2" class="destello-tajo solo-animado"/>
    <g class="solo-animado tajo" mask="url(#mascaraTajo)">
      <path d="{tajo}" fill="#EF4444" filter="url(#neon)"/>
      <path d="{tajo}" fill="#000000"/>
      <path d="{filo}" stroke="#FCA5A5" stroke-width="1.2" fill="none"/>
    </g>
  </g>
  <rect x="1.5" y="1.5" width="{W - 3}" height="{H - 3}" rx="17" fill="none" stroke="#DC2626" stroke-opacity="0.5" stroke-width="2"/>
</svg>
"""


# --------------------------------------------------------- ventana sistema

def sistema() -> str:
    habilidades = [
        ("Rust · Tauri", "Clientes de escritorio y conexiones remotas"),
        ("React · TypeScript", "Interfaces web y de escritorio"),
        ("Python", "Datos, modelos y automatización"),
        ("C# · .NET", "APIs y servicios backend"),
        ("IoT", "Raspberry Pi · Arduino · Jetson"),
    ]
    filas = []
    for i, (nombre, detalle) in enumerate(habilidades):
        y = 246 + i * 26
        filas.append(
            f'<g class="linea" style="animation-delay:{1.3 + i * 0.18:.2f}s">'
            f'<text x="60" y="{y}" class="valor" fill="#F8FAFC"><tspan fill="#60A5FA">▸ </tspan>{nombre}</text>'
            f'<text x="250" y="{y}" class="detalle" fill="#94A3B8">{detalle}</text></g>'
        )

    css = """
    .etq { font: 700 13px """ + FUENTE_MONO + """; letter-spacing: 2px; }
    .valor { font: 700 17px """ + FUENTE_TEXTO + """; }
    .detalle { font: 400 14px """ + FUENTE_TEXTO + """; }
    .cabecera { font: 900 22px """ + FUENTE_TITULO + """; letter-spacing: 8px; }
    .grande { font: 900 26px """ + FUENTE_TITULO + """; }

    .abre { animation: abrir 0.7s cubic-bezier(.2,.9,.3,1) both; transform-box: fill-box; transform-origin: center; }
    @keyframes abrir { from { opacity: 0; transform: scaleY(0.02) scaleX(0.6); } 60% { opacity: 1; transform: scaleY(0.02) scaleX(1); } to { opacity: 1; transform: none; } }
    .linea { animation: linea 0.5s ease-out both; }
    @keyframes linea { from { opacity: 0; transform: translateX(-16px); } to { opacity: 1; transform: none; } }

    .borde { stroke-dasharray: 160 2400; animation: recorrer 6s linear infinite; }
    @keyframes recorrer { to { stroke-dashoffset: -2560; } }
    .escaneo { animation: escanear 4s linear infinite; }
    @keyframes escanear { from { transform: translateY(-40px); } to { transform: translateY(420px); } }
    .parpadeo-panel { animation: parpadeoPanel 7s steps(1) infinite; }
    @keyframes parpadeoPanel { 0%, 100% { opacity: 1; } 92% { opacity: 0.55; } 93% { opacity: 1; } 94% { opacity: 0.7; } 95% { opacity: 1; } }
    .si { animation: si 1.4s ease-in-out 3s infinite; }
    @keyframes si { 0%, 100% { fill-opacity: 0.15; } 50% { fill-opacity: 0.6; } }
    .carga { animation: carga 2.4s ease-in-out infinite; }
    @keyframes carga { from { transform: translateX(-120px); } to { transform: translateX(380px); } }
    .ascenso { animation: ascenso 1.2s ease-in-out infinite; }
    @keyframes ascenso { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-4px); } }
    """ + MOVIMIENTO_REDUCIDO

    marco = "M 22 0 H 978 L 1000 22 V 398 L 978 420 H 22 L 0 398 V 22 Z"
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="420" viewBox="0 0 1000 420" role="img" aria-labelledby="t">
  <title id="t">Ventana de estado: Haider, desarrollador de software</title>
  <defs>
    <linearGradient id="panel" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#0B1A33"/>
      <stop offset="1" stop-color="#050B18"/>
    </linearGradient>
    <linearGradient id="haz" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#60A5FA" stop-opacity="0"/>
      <stop offset="1" stop-color="#60A5FA" stop-opacity="0.16"/>
    </linearGradient>
    <linearGradient id="barra" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#60A5FA" stop-opacity="0"/>
      <stop offset="0.5" stop-color="#93C5FD"/>
      <stop offset="1" stop-color="#60A5FA" stop-opacity="0"/>
    </linearGradient>
    <pattern id="lineas" width="4" height="4" patternUnits="userSpaceOnUse">
      <rect width="4" height="1" fill="#93C5FD" fill-opacity="0.05"/>
    </pattern>
    <filter id="neonAzul" x="-10%" y="-10%" width="120%" height="120%">
      <feGaussianBlur stdDeviation="5" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <clipPath id="dentro"><path d="{marco}"/></clipPath>
    <clipPath id="recorteBarra"><rect x="560" y="336" width="360" height="6" rx="3"/></clipPath>
  </defs>
  <style>{css}</style>

  <g class="abre">
    <g class="parpadeo-panel">
      <path d="{marco}" fill="url(#panel)" fill-opacity="0.96"/>
      <path d="{marco}" fill="url(#lineas)"/>
      <g clip-path="url(#dentro)"><rect y="0" width="1000" height="60" fill="url(#haz)" class="escaneo solo-animado"/></g>
      <path d="{marco}" fill="none" stroke="#3B82F6" stroke-width="2" filter="url(#neonAzul)"/>
      <path d="{marco}" fill="none" stroke="#DBEAFE" stroke-width="3" class="borde solo-animado"/>

      <!-- Cabecera -->
      <g class="linea" style="animation-delay:0.5s">
        <line x1="60" y1="52" x2="390" y2="52" stroke="#3B82F6" stroke-opacity="0.6"/>
        <line x1="610" y1="52" x2="940" y2="52" stroke="#3B82F6" stroke-opacity="0.6"/>
        <rect x="405" y="32" width="190" height="40" fill="#0B1A33" stroke="#60A5FA" stroke-width="1.5"/>
        <text x="500" y="61" text-anchor="middle" class="cabecera" fill="#DBEAFE">ESTADO</text>
      </g>

      <!-- Datos del jugador -->
      <g class="linea" style="animation-delay:0.75s">
        <text x="60" y="112" class="etq" fill="#60A5FA">NOMBRE</text>
        <text x="60" y="138" class="grande" fill="#F8FAFC">HAIDER</text>
        <text x="540" y="112" class="etq" fill="#60A5FA">NIVEL</text>
        <text x="540" y="138" class="grande" fill="#F8FAFC">EN ASCENSO <tspan fill="#60A5FA" class="ascenso">▲</tspan></text>
      </g>
      <g class="linea" style="animation-delay:0.95s">
        <text x="60" y="176" class="etq" fill="#60A5FA">CLASE</text>
        <text x="60" y="199" class="valor" fill="#F8FAFC">Desarrollador de software</text>
        <text x="540" y="176" class="etq" fill="#60A5FA">TÍTULO</text>
        <text x="540" y="199" class="valor" fill="#F8FAFC">El que nunca se rinde</text>
      </g>
      <line x1="60" y1="216" x2="940" y2="216" stroke="#3B82F6" stroke-opacity="0.35" class="linea" style="animation-delay:1.1s"/>

      <!-- Habilidades -->
      {"".join(filas)}

      <!-- Misión activa -->
      <g class="linea" style="animation-delay:2.3s">
        <rect x="540" y="232" width="400" height="128" fill="#0B1A33" stroke="#3B82F6" stroke-opacity="0.6"/>
        <text x="560" y="258" class="etq" fill="#60A5FA">MISIÓN ACTIVA</text>
        <text x="560" y="290" class="grande" fill="#F8FAFC">LaboRemoto</text>
        <text x="560" y="315" class="detalle" fill="#CBD5E1">Laboratorio remoto: SSH, SFTP, VNC, GPIO e IA</text>
        <rect x="560" y="336" width="360" height="6" rx="3" fill="#1E3A8A" fill-opacity="0.6"/>
        <g clip-path="url(#recorteBarra)"><rect x="560" y="336" width="120" height="6" fill="url(#barra)" class="carga solo-animado"/></g>
      </g>

      <!-- Pregunta final -->
      <g class="linea" style="animation-delay:2.8s">
        <text x="60" y="398" class="valor" fill="#DBEAFE">¿Aceptas la misión?</text>
        <rect x="245" y="378" width="70" height="28" fill="#3B82F6" class="si" stroke="#60A5FA"/>
        <text x="280" y="398" text-anchor="middle" class="valor" fill="#FFFFFF">SÍ</text>
        <rect x="330" y="378" width="70" height="28" fill="none" stroke="#334155"/>
        <text x="365" y="398" text-anchor="middle" class="valor" fill="#64748B">NO</text>
      </g>
    </g>
  </g>
</svg>
"""


# ---------------------------------------------------------------- arise

def arise() -> str:
    rng = random.Random(3)
    W, H = 1000, 440

    # Igris: panel izquierdo de 400x440 con sus capas de brillo
    igris = Image.open(IGRIS).convert("RGB").resize((400, 731), Image.LANCZOS).crop((0, 20, 400, 460))
    base_igris = jpeg_base64(igris, 84)
    m_runas = mascara(igris, lambda r, g, b: b > 170 and b - r > 50 and g > 90, 1.2)
    m_filo = mascara(igris, lambda r, g, b: min(r, g, b) > 200 and b >= r, 1.5)
    m_penacho = mascara(igris, lambda r, g, b: r > 150 and r - g > 80 and r - b > 80, 2)
    ojos_igris = [(160, 158), (190, 152)]

    # Ejército: 783x440, colocado en x=280 para que Jin-Woo quede en x≈640
    EX, EW = 280, 783
    ejercito = Image.open(EJERCITO).convert("RGB").resize((EW, H), Image.LANCZOS)
    base_ejercito = jpeg_base64(ejercito, 84)
    m_llamas = mascara(ejercito, lambda r, g, b: b > 160 and b - r > 60, 1.5)
    m_ojos = mascara(ejercito, lambda r, g, b: b > 200 and g > 150 and r > 120, 1)

    rayos = []
    for i, (a, b, c, d) in enumerate([(520, 0, 580, 130), (960, 0, 880, 150), (760, 0, 720, 80)]):
        path = rayo(rng, a, b, c, d, pasos=8, desvio=20)
        rayos.append(
            f'<g class="rayo solo-animado" style="animation-delay:{1 + i * 1.9:.2f}s">'
            f'<path d="{path}" stroke="#818CF8" stroke-width="7" fill="none" filter="url(#neonV)"/>'
            f'<path d="{path}" stroke="#EEF2FF" stroke-width="1.6" fill="none"/></g>'
        )

    runas = "".join(
        f'<text x="{math.cos(math.radians(a)) * 232:.1f}" y="{math.sin(math.radians(a)) * 232:.1f}" class="runa" '
        f'transform="rotate({a + 90:.0f} {math.cos(math.radians(a)) * 232:.1f} {math.sin(math.radians(a)) * 232:.1f})">{ch}</text>'
        for a, ch in zip(range(0, 360, 20), "ᚠᚢᚦᚨᚱᚲᚷᚹᚺᚾᛁᛃᛇᛈᛉᛊᛏᛒ")
    )
    brasas_penacho = "".join(
        f'<circle cx="{rng.uniform(170, 390):.0f}" cy="{rng.uniform(20, 170):.0f}" r="{rng.uniform(1.2, 3):.1f}" '
        f'fill="{rng.choice(["#F97316", "#EF4444", "#FDBA74"])}" class="brasa solo-animado" '
        f'style="animation-delay:{rng.uniform(0, 4):.2f}s;animation-duration:{rng.uniform(2.5, 4.5):.2f}s"/>'
        for _ in range(22)
    )

    css = """
    .arise { font: 900 92px """ + FUENTE_TITULO + """; letter-spacing: 20px; }
    .sub { font: 700 13px """ + FUENTE_MONO + """; letter-spacing: 3px; }
    .nombre { font: 900 15px """ + FUENTE_MONO + """; letter-spacing: 6px; }
    .runa { font: 400 18px 'Segoe UI Symbol', 'Noto Sans Runic', serif; fill: #A5B4FC; text-anchor: middle; dominant-baseline: middle; }

    .grito { animation: grito 12s ease-out infinite both; transform-box: fill-box; transform-origin: center; }
    @keyframes grito {
      0% { opacity: 0; transform: scale(1.6); }
      5% { opacity: 1; transform: scale(1); }
      84% { opacity: 1; transform: scale(1); }
      92%, 100% { opacity: 0; transform: scale(0.96); }
    }
    .onda { animation: onda 12s ease-out infinite; transform-box: fill-box; transform-origin: center; opacity: 0; }
    @keyframes onda { 0% { opacity: 0.9; transform: scale(0.3); } 8% { opacity: 0; transform: scale(1.5); } 100% { opacity: 0; } }
    .estallido { animation: estallido 12s ease-out infinite; opacity: 0; }
    @keyframes estallido { 0% { opacity: 0; } 3% { opacity: 0.55; } 14% { opacity: 0; } 100% { opacity: 0; } }
    .circulo { animation: girar 30s linear infinite; transform-box: fill-box; transform-origin: center; }
    .circulo-inverso { animation: girar 20s linear infinite reverse; transform-box: fill-box; transform-origin: center; }
    @keyframes girar { to { transform: rotate(360deg); } }
    .pulso { animation: pulso 2.4s ease-in-out infinite; }
    @keyframes pulso { 0%, 100% { opacity: 0.45; } 50% { opacity: 1; } }
    .llamas { animation: llamas 2.2s ease-in-out infinite; }
    @keyframes llamas { 0%, 100% { opacity: 0.05; } 50% { opacity: 0.45; } }
    .ojos-ejercito { animation: ojosEjercito 3s steps(1) infinite; }
    @keyframes ojosEjercito { 0%, 100% { opacity: 1; } 40% { opacity: 0.3; } 42% { opacity: 1; } 70% { opacity: 0.5; } 72% { opacity: 1; } }
    .camara { animation: camara 16s ease-in-out infinite alternate; transform-origin: 640px 330px; }
    @keyframes camara { from { transform: scale(1); } to { transform: scale(1.06); } }
    .niebla { animation: niebla 9s ease-in-out infinite alternate; }
    @keyframes niebla { from { transform: translateX(-40px); opacity: 0.45; } to { transform: translateX(40px); opacity: 0.8; } }
    .rayo { animation: rayo 6s steps(1) infinite; opacity: 0; }
    @keyframes rayo { 0%, 100% { opacity: 0; } 80% { opacity: 1; } 81.5% { opacity: 0.1; } 83% { opacity: 1; } 85% { opacity: 0; } }
    .chispa { animation: subir 4.5s ease-in infinite; opacity: 0; }
    @keyframes subir { 0% { opacity: 0; transform: translateY(0); } 20% { opacity: 1; } 100% { opacity: 0; transform: translateY(-260px); } }

    .igris { animation: igris 7s ease-in-out infinite alternate; transform-origin: 200px 300px; }
    @keyframes igris { from { transform: scale(1); } to { transform: scale(1.04) translateY(-4px); } }
    .runas { animation: runas 2.6s ease-in-out infinite; }
    @keyframes runas { 0%, 100% { opacity: 0.2; } 50% { opacity: 1; } }
    .filo { animation: filo 3.4s ease-in-out infinite; }
    @keyframes filo { 0%, 100% { opacity: 0.15; } 40% { opacity: 0.9; } 45% { opacity: 0.4; } 50% { opacity: 1; } }
    .penacho { animation: penacho 1.3s ease-in-out infinite alternate; }
    @keyframes penacho { from { opacity: 0.35; } to { opacity: 0.95; } }
    .ojo-igris { animation: ojoIgris 2s ease-in-out infinite; }
    @keyframes ojoIgris { 0%, 100% { opacity: 0.5; } 50% { opacity: 1; } }
    .brasa { animation: brasa 3.5s ease-out infinite; opacity: 0; }
    @keyframes brasa { 0% { opacity: 0; transform: translate(0, 0); } 15% { opacity: 1; } 100% { opacity: 0; transform: translate(70px, -90px); } }
    .nombre-entra { animation: nombreEntra 12s ease-out infinite both; }
    @keyframes nombreEntra { 0%, 3% { opacity: 0; transform: translateX(-12px); } 8%, 86% { opacity: 1; transform: none; } 94%, 100% { opacity: 0; } }
    """ + MOVIMIENTO_REDUCIDO

    cx = 640  # Jin-Woo
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="t">
  <title id="t">ARISE: Igris y el ejército de sombras de Sung Jin-Woo</title>
  <defs>
    <clipPath id="marco"><rect width="{W}" height="{H}" rx="18"/></clipPath>
    <linearGradient id="cielo" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#05030A"/>
      <stop offset="1" stop-color="#0A0A1F"/>
    </linearGradient>
    <linearGradient id="letras" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#FFFFFF"/>
      <stop offset="0.6" stop-color="#E0E7FF"/>
      <stop offset="1" stop-color="#818CF8"/>
    </linearGradient>
    <linearGradient id="fundidoIgris" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="420" y2="0">
      <stop offset="0.62" stop-color="#FFFFFF"/>
      <stop offset="1" stop-color="#000000"/>
    </linearGradient>
    <linearGradient id="fundidoEjercito" gradientUnits="userSpaceOnUse" x1="{EX}" y1="0" x2="{EX + 150}" y2="0">
      <stop offset="0" stop-color="#000000"/>
      <stop offset="1" stop-color="#FFFFFF"/>
    </linearGradient>
    <linearGradient id="sombraArriba" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#000" stop-opacity="0.6"/>
      <stop offset="1" stop-color="#000" stop-opacity="0"/>
    </linearGradient>
    <mask id="mIgris" maskUnits="userSpaceOnUse" x="0" y="0" width="420" height="{H}"><rect width="420" height="{H}" fill="url(#fundidoIgris)"/></mask>
    <mask id="mEjercito" maskUnits="userSpaceOnUse" x="0" y="0" width="{W}" height="{H}"><rect width="{W}" height="{H}" fill="url(#fundidoEjercito)"/></mask>
    <mask id="mRunas" maskUnits="userSpaceOnUse" x="0" y="0" width="400" height="440"><image width="400" height="440" href="data:image/jpeg;base64,{m_runas}"/></mask>
    <mask id="mFilo" maskUnits="userSpaceOnUse" x="0" y="0" width="400" height="440"><image width="400" height="440" href="data:image/jpeg;base64,{m_filo}"/></mask>
    <mask id="mPenacho" maskUnits="userSpaceOnUse" x="0" y="0" width="400" height="440"><image width="400" height="440" href="data:image/jpeg;base64,{m_penacho}"/></mask>
    <mask id="mLlamas" maskUnits="userSpaceOnUse" x="{EX}" y="0" width="{EW}" height="{H}"><image x="{EX}" width="{EW}" height="{H}" href="data:image/jpeg;base64,{m_llamas}"/></mask>
    <mask id="mOjos" maskUnits="userSpaceOnUse" x="{EX}" y="0" width="{EW}" height="{H}"><image x="{EX}" width="{EW}" height="{H}" href="data:image/jpeg;base64,{m_ojos}"/></mask>
    <filter id="neonV" x="-20%" y="-50%" width="140%" height="200%">
      <feGaussianBlur stdDeviation="7" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <filter id="resplandor" x="-5%" y="-5%" width="110%" height="110%">
      <feGaussianBlur stdDeviation="4" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <filter id="resplandorFuerte" x="-5%" y="-5%" width="110%" height="110%">
      <feGaussianBlur stdDeviation="9" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="b"/><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <filter id="brilloOjoIgris" x="-300%" y="-300%" width="700%" height="700%"><feGaussianBlur stdDeviation="6"/></filter>
    <filter id="borroso" x="-50%" y="-100%" width="200%" height="300%"><feGaussianBlur stdDeviation="16"/></filter>
  </defs>
  <style>{css}</style>

  <g clip-path="url(#marco)">
    <rect width="{W}" height="{H}" fill="url(#cielo)"/>

    <!-- El ejército de sombras con Jin-Woo al centro -->
    <g mask="url(#mEjercito)">
      <g class="camara">
        <image x="{EX}" width="{EW}" height="{H}" href="data:image/jpeg;base64,{base_ejercito}"/>
        <g filter="url(#resplandor)" class="llamas"><rect x="{EX}" width="{EW}" height="{H}" fill="#6366F1" mask="url(#mLlamas)"/></g>
        <g filter="url(#resplandorFuerte)" class="estallido solo-animado"><rect x="{EX}" width="{EW}" height="{H}" fill="#A5B4FC" mask="url(#mLlamas)"/></g>
        <g filter="url(#resplandor)" class="ojos-ejercito"><rect x="{EX}" width="{EW}" height="{H}" fill="#E0E7FF" mask="url(#mOjos)"/></g>
      </g>
    </g>
    {"".join(rayos)}
    <rect x="{EX}" width="{W - EX}" height="150" fill="url(#sombraArriba)"/>

    <!-- Círculo mágico a los pies de Jin-Woo -->
    <g transform="translate({cx} 408) scale(0.85 0.16)">
      <g class="pulso" filter="url(#neonV)">
        <g class="circulo">
          <circle r="250" fill="none" stroke="#818CF8" stroke-width="3"/>
          <circle r="214" fill="none" stroke="#6366F1" stroke-width="2" stroke-dasharray="14 10"/>
          {runas}
        </g>
        <g class="circulo-inverso">
          <circle r="170" fill="none" stroke="#C7D2FE" stroke-width="2"/>
          <polygon points="0,-170 147,85 -147,85" fill="none" stroke="#818CF8" stroke-width="2"/>
          <polygon points="0,170 147,-85 -147,-85" fill="none" stroke="#818CF8" stroke-width="2"/>
        </g>
      </g>
      <circle r="250" fill="none" stroke="#E0E7FF" stroke-width="10" class="onda solo-animado"/>
    </g>
    <g filter="url(#borroso)" class="niebla solo-animado">
      <ellipse cx="520" cy="430" rx="200" ry="26" fill="#3730A3"/>
      <ellipse cx="830" cy="428" rx="210" ry="26" fill="#4338CA"/>
    </g>
    <g>{chispas(rng, 18, 420, 980, 430, ["#818CF8", "#A5B4FC", "#6366F1", "#C7D2FE"], r=(1.2, 3))}</g>

    <!-- Igris, el comandante -->
    <g mask="url(#mIgris)">
      <rect width="420" height="{H}" fill="#05030A"/>
      <g class="igris">
        <image width="400" height="440" href="data:image/jpeg;base64,{base_igris}"/>
        <g filter="url(#resplandor)" class="runas"><rect width="400" height="440" fill="#60A5FA" mask="url(#mRunas)"/></g>
        <g filter="url(#resplandor)" class="filo"><rect width="400" height="440" fill="#E0F2FE" mask="url(#mFilo)"/></g>
        <g filter="url(#resplandor)" class="penacho"><rect width="400" height="440" fill="#FB923C" mask="url(#mPenacho)"/></g>
        <g filter="url(#brilloOjoIgris)">
          {"".join(f'<ellipse cx="{x}" cy="{y}" rx="11" ry="6" fill="#93C5FD" class="ojo-igris"/>' for x, y in ojos_igris)}
        </g>
        {brasas_penacho}
      </g>
    </g>
    <g class="nombre-entra">
      <rect x="24" y="392" width="282" height="30" fill="#030712" fill-opacity="0.75" stroke="#60A5FA" stroke-width="1.2"/>
      <text x="36" y="412" class="nombre" fill="#DBEAFE">IGRIS <tspan fill="#60A5FA" font-weight="400">· COMANDANTE</tspan></text>
    </g>

    <!-- ARISE -->
    <g class="grito">
      <text x="{cx + 10}" y="100" text-anchor="middle" class="arise" fill="#6366F1" filter="url(#neonV)" opacity="0.85">ARISE</text>
      <text x="{cx + 10}" y="100" text-anchor="middle" class="arise" fill="url(#letras)">ARISE</text>
    </g>
    <rect x="{cx - 230}" y="412" width="460" height="22" rx="4" fill="#030712" fill-opacity="0.6"/>
    <text x="{cx}" y="428" text-anchor="middle" class="sub" fill="#BFDBFE">[SISTEMA] EXTRACCIÓN DE SOMBRAS COMPLETADA</text>
  </g>
  <rect x="1.5" y="1.5" width="{W - 3}" height="{H - 3}" rx="17" fill="none" stroke="#6366F1" stroke-opacity="0.5" stroke-width="2"/>
</svg>
"""


# ----------------------------------------------------------------- caminos

def decor_ayanokoji() -> str:
    rey = (
        "M -26 0 L 26 0 L 22 -12 L -22 -12 Z M -16 -14 L 16 -14 L 10 -70 L -10 -70 Z "
        "M -18 -72 L 18 -72 L 14 -82 L -14 -82 Z M 0 -84 m -13 0 a 13 13 0 1 0 26 0 a 13 13 0 1 0 -26 0 "
        "M -3 -96 L 3 -96 L 3 -104 L 10 -104 L 10 -110 L 3 -110 L 3 -118 L -3 -118 L -3 -110 L -10 -110 L -10 -104 L -3 -104 Z"
    )
    casillas = []
    for fila in range(4):
        for col in range(6):
            if (fila + col) % 2 == 0:
                casillas.append(f'<rect x="{730 + col * 40}" y="{40 + fila * 40}" width="40" height="40"/>')
    return f"""
  <g fill="#F59E0B" fill-opacity="0.06" class="solo-animado">{"".join(casillas)}</g>
  <g transform="translate(900 196)">
    <g class="rey">
      <path d="{rey}" fill="#0D0B14" stroke="#F59E0B" stroke-width="2" filter="url(#brillo)" opacity="0.6"/>
      <path d="{rey}" fill="#0D0B14" stroke="#FCD34D" stroke-width="1.6"/>
    </g>
  </g>"""


def decor_jinwoo() -> str:
    # Recorte del ejército real a la derecha de la tarjeta, fundido hacia la izquierda
    recorte = Image.open(EJERCITO).convert("RGB").crop((650, 0, 1672, 940)).resize((240, 221), Image.LANCZOS)
    llamas_m = mascara(recorte, lambda r, g, b: b > 160 and b - r > 60, 1)
    return f"""
  <mask id="mEjercitoCamino" maskUnits="userSpaceOnUse" x="600" y="0" width="400" height="220">
    <rect x="600" width="400" height="220" fill="url(#fundidoCamino)"/>
  </mask>
  <mask id="mLlamasCamino" maskUnits="userSpaceOnUse" x="760" y="0" width="240" height="221">
    <image x="760" width="240" height="221" href="data:image/jpeg;base64,{llamas_m}"/>
  </mask>
  <g clip-path="url(#sueloCamino)" mask="url(#mEjercitoCamino)">
    <image x="760" width="240" height="221" href="data:image/jpeg;base64,{jpeg_base64(recorte, 80)}"/>
    <g filter="url(#brillo)" class="llama-azul"><rect x="760" width="240" height="221" fill="#818CF8" mask="url(#mLlamasCamino)"/></g>
  </g>"""


def decor_asta() -> str:
    rng = random.Random(5)
    return f"""
  <g transform="translate(885 100)" opacity="0.5">
    <g class="gira">{trebol(70, "#000000", "#EF4444", 2.5)}</g>
  </g>
  <g filter="url(#fuegoCamino)">
    <path d="{llamas(rng, 640, 1000, 222, 18, 60, ancho=26)}" fill="#000000" stroke="#DC2626" stroke-width="1.5" class="llama"/>
  </g>"""


CAMINOS = [
    {
        "archivo": "camino-ayanokoji.svg",
        "recorte": (40, 200, 400, 558),
        "acento": "#F59E0B",
        "acento2": "#DC2626",
        "etiqueta": "CAMINO I · LA MENTE",
        "titulo": "Análisis y estrategia",
        "frase": "“Mientras gane al final, eso es todo lo que importa.” — Ayanokoji",
        "decor": decor_ayanokoji,
    },
    {
        "archivo": "camino-jinwoo.svg",
        "recorte": (470, 0, 830, 358),
        "acento": "#A855F7",
        "acento2": "#6366F1",
        "etiqueta": "CAMINO II · LAS SOMBRAS",
        "titulo": "Sistemas en las sombras",
        "frase": "“¡Levántate!” · ARISE — Sung Jin-Woo",
        "decor": decor_jinwoo,
    },
    {
        "archivo": "camino-asta.svg",
        "fuente": ASTA,
        "recorte": (206, 549, 726, 1069),
        "acento": "#DC2626",
        "acento2": "#EF4444",
        "etiqueta": "CAMINO III · NUNCA RENDIRSE",
        "titulo": "Construir sin rendirse",
        "frase": "“No rendirme... ¡esa es mi magia!” — Asta",
        "decor": decor_asta,
    },
]


def camino(banner: Image.Image, c: dict) -> str:
    fuente = Image.open(c["fuente"]).convert("RGB") if "fuente" in c else banner
    retrato = jpeg_base64(fuente.crop(c["recorte"]).resize((240, 240), Image.LANCZOS))
    acento, acento2 = c["acento"], c["acento2"]
    css = """
    .etiqueta { font: 700 13px """ + FUENTE_MONO + """; letter-spacing: 5px; }
    .titulo   { font: 900 38px """ + FUENTE_TITULO + """; }
    .frase    { font: italic 400 17px """ + FUENTE_TEXTO + """; }

    .entra   { animation: entrar 0.8s cubic-bezier(.2,.9,.3,1.2) both; }
    .entra-2 { animation: entrar 0.8s cubic-bezier(.2,.9,.3,1.2) 0.25s both; }
    @keyframes entrar { from { opacity: 0; transform: translateX(-24px); } to { opacity: 1; transform: none; } }
    .respira { animation: respirar 6s ease-in-out infinite; transform-box: fill-box; transform-origin: center; }
    @keyframes respirar { 0%, 100% { transform: scale(1); } 50% { transform: scale(1.05); } }
    .pulso { animation: pulso 2.2s ease-in-out infinite; }
    @keyframes pulso { 0%, 100% { opacity: 0.35; } 50% { opacity: 1; } }
    .escaner { animation: escanear 3.2s linear infinite; }
    @keyframes escanear { from { transform: translateY(-60px); } to { transform: translateY(200px); } }
    .dibuja { stroke-dasharray: 730; stroke-dashoffset: 730; animation: dibujar 1.6s ease-out 0.5s forwards; }
    @keyframes dibujar { to { stroke-dashoffset: 0; } }
    .chispa { animation: subir 3.8s ease-in infinite; opacity: 0; }
    @keyframes subir { 0% { opacity: 0; transform: translateY(0); } 20% { opacity: 1; } 100% { opacity: 0; transform: translateY(-180px); } }

    .rey { animation: flotar 4s ease-in-out infinite; }
    @keyframes flotar { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-8px); } }
    .gira { animation: girar 24s linear infinite; transform-box: fill-box; transform-origin: center; }
    @keyframes girar { to { transform: rotate(360deg); } }
    .llama { animation: oscilar 1.8s ease-in-out infinite alternate; }
    @keyframes oscilar { from { transform: translateY(0); } to { transform: translateY(-6px); } }
    .llama-azul { animation: llamaAzul 2.2s ease-in-out infinite; }
    @keyframes llamaAzul { 0%, 100% { opacity: 0.15; } 50% { opacity: 0.8; } }
    @media (prefers-reduced-motion: reduce) {
      * { animation: none !important; }
      .chispa, .escaner { display: none; }
      .dibuja { stroke-dashoffset: 0; }
    }"""
    rng = random.Random(c["archivo"])
    return f"""<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="1000" height="220" viewBox="0 0 1000 220" role="img" aria-labelledby="t">
  <title id="t">{c["etiqueta"]}: {c["titulo"]}</title>
  <defs>
    <linearGradient id="fondo" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#0D0B14"/>
      <stop offset="0.6" stop-color="#120E1C"/>
      <stop offset="1" stop-color="#0D0B14"/>
    </linearGradient>
    <radialGradient id="aura" cx="12%" cy="50%" r="45%">
      <stop offset="0" stop-color="{acento}" stop-opacity="0.35"/>
      <stop offset="1" stop-color="{acento}" stop-opacity="0"/>
    </radialGradient>
    <linearGradient id="linea" gradientUnits="userSpaceOnUse" x1="230" y1="0" x2="960" y2="0">
      <stop offset="0" stop-color="{acento}"/>
      <stop offset="1" stop-color="{acento2}" stop-opacity="0"/>
    </linearGradient>
    <linearGradient id="escaner" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="{acento}" stop-opacity="0"/>
      <stop offset="1" stop-color="{acento}" stop-opacity="0.55"/>
    </linearGradient>
    <clipPath id="marco"><rect x="20" y="20" width="180" height="180" rx="14"/></clipPath>
    <clipPath id="sueloCamino"><rect x="600" y="0" width="398" height="218" rx="17"/></clipPath>
    <linearGradient id="fundidoCamino" gradientUnits="userSpaceOnUse" x1="760" y1="0" x2="880" y2="0">
      <stop offset="0" stop-color="#000000"/>
      <stop offset="1" stop-color="#FFFFFF" stop-opacity="0.9"/>
    </linearGradient>
    <clipPath id="escritura">
      <rect x="230" y="128" width="0" height="34">
        <animate attributeName="width" from="0" to="750" dur="2.6s" begin="0.9s" fill="freeze"/>
      </rect>
    </clipPath>
    <filter id="brillo" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="6"/></filter>
    <filter id="fuegoCamino" x="-5%" y="-60%" width="110%" height="180%">
      <feTurbulence type="fractalNoise" baseFrequency="0.02 0.07" numOctaves="2" seed="2" result="r">
        <animate attributeName="baseFrequency" values="0.02 0.07;0.026 0.1;0.02 0.07" dur="2.6s" repeatCount="indefinite"/>
      </feTurbulence>
      <feDisplacementMap in="SourceGraphic" in2="r" scale="14" xChannelSelector="R" yChannelSelector="G"/>
    </filter>
  </defs>
  <style>{css}</style>

  <rect width="1000" height="220" rx="18" fill="url(#fondo)"/>
  <rect width="1000" height="220" rx="18" fill="url(#aura)" class="pulso"/>
  {c["decor"]()}
  <g fill="{acento}">
    {chispas(rng, 6, 280, 760, 220, [acento, acento2], r=(1.5, 3))}
  </g>

  <rect x="20" y="20" width="180" height="180" rx="14" fill="{acento}" filter="url(#brillo)" class="pulso"/>
  <g clip-path="url(#marco)">
    <image x="20" y="20" width="180" height="180" preserveAspectRatio="xMidYMid slice" class="respira" href="data:image/jpeg;base64,{retrato}"/>
    <rect x="20" y="20" width="180" height="60" fill="url(#escaner)" class="escaner"/>
  </g>
  <rect x="20" y="20" width="180" height="180" rx="14" fill="none" stroke="{acento}" stroke-width="2.5"/>

  <text x="230" y="58" class="etiqueta entra" fill="{acento}">{c["etiqueta"]}</text>
  <text x="230" y="108" class="titulo entra-2" fill="#F9FAFB">{c["titulo"]}</text>
  <g clip-path="url(#escritura)">
    <text x="230" y="152" class="frase" fill="#9CA3AF">{c["frase"]}</text>
  </g>
  <path d="M 230 180 L 960 180" stroke="url(#linea)" stroke-width="3" stroke-linecap="round" class="dibuja"/>
  <rect x="1.5" y="1.5" width="997" height="217" rx="17" fill="none" stroke="{acento}" stroke-opacity="0.3" stroke-width="2"/>
</svg>
"""


def main() -> None:
    banner = Image.open(BANNER).convert("RGB")
    salidas = {
        "banner-vivo.svg": banner_vivo(),
        "antimagia.svg": antimagia(),
        "sistema.svg": sistema(),
        "arise.svg": arise(),
    }
    for c in CAMINOS:
        salidas[c["archivo"]] = camino(banner, c)
    for nombre, svg in salidas.items():
        (ASSETS / nombre).write_text(svg, encoding="utf-8")
        print(f"{nombre}: {len(svg.encode('utf-8')) // 1024} KB")


if __name__ == "__main__":
    main()
