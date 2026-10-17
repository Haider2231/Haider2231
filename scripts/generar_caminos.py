"""Genera las tarjetas animadas de los tres caminos a partir del banner.

Uso:  python scripts/generar_caminos.py
Lee assets/banner.jpg y escribe assets/camino-*.svg con el retrato incrustado.
"""

import base64
import io
from pathlib import Path

from PIL import Image

RAIZ = Path(__file__).resolve().parent.parent
BANNER = RAIZ / "assets" / "banner.jpg"

CAMINOS = [
    {
        "archivo": "camino-ayanokoji.svg",
        "recorte": (40, 200, 400, 558),
        "numero": "I",
        "acento": "#F59E0B",
        "acento2": "#DC2626",
        "etiqueta": "CAMINO I · LA MENTE",
        "titulo": "Análisis y estrategia",
        "frase": "“Mientras gane al final, eso es todo lo que importa.” — Ayanokoji",
    },
    {
        "archivo": "camino-jinwoo.svg",
        "recorte": (470, 0, 830, 358),
        "numero": "II",
        "acento": "#A855F7",
        "acento2": "#6366F1",
        "etiqueta": "CAMINO II · LAS SOMBRAS",
        "titulo": "Sistemas en las sombras",
        "frase": "“¡Levántate!” · ARISE — Sung Jin-Woo",
    },
    {
        "archivo": "camino-asta.svg",
        "recorte": (880, 200, 1240, 558),
        "numero": "III",
        "acento": "#DC2626",
        "acento2": "#EF4444",
        "etiqueta": "CAMINO III · NUNCA RENDIRSE",
        "titulo": "Construir sin rendirse",
        "frase": "“No rendirme... ¡esa es mi magia!” — Asta",
    },
]

PLANTILLA = """<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="1000" height="220" viewBox="0 0 1000 220" role="img" aria-labelledby="t">
  <title id="t">{etiqueta}: {titulo}</title>
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
    <clipPath id="escritura">
      <rect x="230" y="128" width="0" height="34">
        <animate attributeName="width" from="0" to="750" dur="2.6s" begin="0.9s" fill="freeze"/>
      </rect>
    </clipPath>
    <filter id="brillo" x="-30%" y="-30%" width="160%" height="160%">
      <feGaussianBlur stdDeviation="6"/>
    </filter>
  </defs>

  <style>
    .etiqueta {{ font: 700 13px 'Consolas', 'Courier New', monospace; letter-spacing: 5px; }}
    .titulo   {{ font: 900 38px 'Arial Black', 'Segoe UI Black', Impact, 'Helvetica Neue', Arial, sans-serif; }}
    .frase    {{ font: italic 400 17px 'Segoe UI', 'Helvetica Neue', Arial, sans-serif; }}
    .numero   {{ font: 900 190px 'Arial Black', 'Segoe UI Black', Impact, Arial, sans-serif; }}

    .entra   {{ animation: entrar 0.8s cubic-bezier(.2,.9,.3,1.2) both; }}
    .entra-2 {{ animation: entrar 0.8s cubic-bezier(.2,.9,.3,1.2) 0.25s both; }}
    @keyframes entrar {{ from {{ opacity: 0; transform: translateX(-24px); }} to {{ opacity: 1; transform: none; }} }}

    .respira {{ animation: respirar 6s ease-in-out infinite; transform-box: fill-box; transform-origin: center; }}
    @keyframes respirar {{ 0%, 100% {{ transform: scale(1); }} 50% {{ transform: scale(1.05); }} }}

    .pulso {{ animation: pulso 2.2s ease-in-out infinite; }}
    @keyframes pulso {{ 0%, 100% {{ opacity: 0.35; }} 50% {{ opacity: 1; }} }}

    .escaner {{ animation: escanear 3.2s linear infinite; }}
    @keyframes escanear {{ from {{ transform: translateY(-60px); }} to {{ transform: translateY(200px); }} }}

    .dibuja {{ stroke-dasharray: 730; stroke-dashoffset: 730; animation: dibujar 1.6s ease-out 0.5s forwards; }}
    @keyframes dibujar {{ to {{ stroke-dashoffset: 0; }} }}

    .chispa {{ animation: subir 3.8s ease-in infinite; opacity: 0; }}
    @keyframes subir {{
      0% {{ opacity: 0; transform: translateY(0); }}
      20% {{ opacity: 1; }}
      100% {{ opacity: 0; transform: translateY(-180px); }}
    }}

    @media (prefers-reduced-motion: reduce) {{
      * {{ animation: none !important; }}
      .chispa, .escaner {{ display: none; }}
      .dibuja {{ stroke-dashoffset: 0; }}
    }}
  </style>

  <rect width="1000" height="220" rx="18" fill="url(#fondo)"/>
  <rect width="1000" height="220" rx="18" fill="url(#aura)" class="pulso"/>
  <rect x="1.5" y="1.5" width="997" height="217" rx="17" fill="none" stroke="{acento}" stroke-opacity="0.3" stroke-width="2"/>

  <!-- Número del camino al fondo -->
  <text x="975" y="190" text-anchor="end" class="numero" fill="{acento}" fill-opacity="0.07">{numero}</text>

  <!-- Chispas -->
  <g fill="{acento}">
    <circle cx="300" cy="220" r="2"   class="chispa" style="animation-delay:0.2s"/>
    <circle cx="420" cy="220" r="3"   class="chispa" style="animation-delay:1.6s"/>
    <circle cx="560" cy="220" r="2"   class="chispa" style="animation-delay:2.8s"/>
    <circle cx="690" cy="220" r="2.5" class="chispa" style="animation-delay:0.9s"/>
    <circle cx="820" cy="220" r="2"   class="chispa" style="animation-delay:2.2s"/>
    <circle cx="930" cy="220" r="3"   class="chispa" style="animation-delay:3.3s"/>
  </g>

  <!-- Retrato -->
  <rect x="20" y="20" width="180" height="180" rx="14" fill="{acento}" filter="url(#brillo)" class="pulso"/>
  <g clip-path="url(#marco)">
    <image x="20" y="20" width="180" height="180" preserveAspectRatio="xMidYMid slice" class="respira" href="data:image/jpeg;base64,{retrato}" xlink:href="data:image/jpeg;base64,{retrato}"/>
    <rect x="20" y="20" width="180" height="60" fill="url(#escaner)" class="escaner"/>
  </g>
  <rect x="20" y="20" width="180" height="180" rx="14" fill="none" stroke="{acento}" stroke-width="2.5"/>

  <!-- Texto -->
  <text x="230" y="58" class="etiqueta entra" fill="{acento}">{etiqueta}</text>
  <text x="230" y="108" class="titulo entra-2" fill="#F9FAFB">{titulo}</text>
  <g clip-path="url(#escritura)">
    <text x="230" y="152" class="frase" fill="#9CA3AF">{frase}</text>
  </g>
  <path d="M 230 180 L 960 180" stroke="url(#linea)" stroke-width="3" stroke-linecap="round" class="dibuja"/>
</svg>
"""


def retrato_base64(banner: Image.Image, recorte: tuple[int, int, int, int]) -> str:
    img = banner.crop(recorte).resize((240, 240), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=82, optimize=True)
    return base64.b64encode(buf.getvalue()).decode("ascii")


def main() -> None:
    banner = Image.open(BANNER).convert("RGB")
    for camino in CAMINOS:
        svg = PLANTILLA.format(retrato=retrato_base64(banner, camino["recorte"]), **camino)
        destino = RAIZ / "assets" / camino["archivo"]
        destino.write_text(svg, encoding="utf-8")
        print(f"{destino.name}: {len(svg) // 1024} KB")


if __name__ == "__main__":
    main()
