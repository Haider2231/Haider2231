"""Genera assets/racha.svg con el total de contribuciones y las rachas, en hora de Colombia.

Reemplaza al widget externo de racha: ese se guarda hasta 24 h en la caché de GitHub y,
como calcula en UTC, cerca de las 7 p. m. de Colombia podía mostrar la racha en 0.

Uso: GH_TOKEN=... USUARIO=Haider2231 python scripts/generar_racha.py [salida.svg]
"""

import json
import os
import sys
import urllib.request
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

ZONA = ZoneInfo("America/Bogota")
API = "https://api.github.com/graphql"
MESES = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sept", "oct", "nov", "dic"]

COLORES = {
    "fondo": "#0D0B14",
    "borde": "#3B0A14",
    "anillo": "#DC2626",
    "fuego": "#EF4444",
    "numero_racha": "#FFFFFF",
    "titulo_racha": "#DC2626",
    "numeros": "#FFFFFF",
    "titulos": "#E5E7EB",
    "fechas": "#9CA3AF",
}


def graphql(token: str, query: str, variables: dict) -> dict:
    cuerpo = json.dumps({"query": query, "variables": variables}).encode()
    peticion = urllib.request.Request(
        API, data=cuerpo, headers={"Authorization": f"bearer {token}", "Content-Type": "application/json"}
    )
    with urllib.request.urlopen(peticion, timeout=30) as respuesta:
        datos = json.load(respuesta)
    if datos.get("errors"):
        raise RuntimeError(datos["errors"])
    return datos["data"]


def contribuciones_por_dia(token: str, usuario: str) -> dict[date, int]:
    """Todos los días con su conteo, desde el primer año con contribuciones."""
    anios = graphql(
        token,
        "query($u: String!) { user(login: $u) { contributionsCollection { contributionYears } } }",
        {"u": usuario},
    )["user"]["contributionsCollection"]["contributionYears"]

    consulta = """
    query($u: String!, $desde: DateTime!, $hasta: DateTime!) {
      user(login: $u) {
        contributionsCollection(from: $desde, to: $hasta) {
          contributionCalendar { weeks { contributionDays { date contributionCount } } }
        }
      }
    }"""
    dias: dict[date, int] = {}
    for anio in sorted(anios):
        semanas = graphql(
            token,
            consulta,
            {"u": usuario, "desde": f"{anio}-01-01T00:00:00Z", "hasta": f"{anio}-12-31T23:59:59Z"},
        )["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
        for semana in semanas:
            for dia in semana["contributionDays"]:
                dias[date.fromisoformat(dia["date"])] = dia["contributionCount"]
    return dias


def calcular(dias: dict[date, int], hoy: date) -> dict:
    dias = {d: n for d, n in dias.items() if d <= hoy}
    con_aporte = sorted(d for d, n in dias.items() if n > 0)
    total = sum(dias.values())
    primero = con_aporte[0] if con_aporte else hoy

    # Racha más larga
    larga = (0, hoy, hoy)
    inicio = previo = None
    for d in con_aporte:
        inicio = d if previo is None or d - previo > timedelta(days=1) else inicio
        largo = (d - inicio).days + 1
        if largo > larga[0]:
            larga = (largo, inicio, d)
        previo = d

    # Racha actual: si hoy aún no hay aportes, la racha sigue viva hasta ayer
    fin = hoy if dias.get(hoy, 0) > 0 else hoy - timedelta(days=1)
    d = fin
    while dias.get(d, 0) > 0:
        d -= timedelta(days=1)
    actual_largo = (fin - d).days
    actual = (actual_largo, d + timedelta(days=1), fin) if actual_largo else (0, hoy, hoy)

    return {"total": total, "primero": primero, "actual": actual, "larga": larga}


def fecha_corta(d: date, hoy: date) -> str:
    texto = f"{d.day} {MESES[d.month - 1]}"
    return texto if d.year == hoy.year else f"{texto} {d.year}"


def rango(inicio: date, fin: date, hoy: date) -> str:
    if inicio == fin:
        return fecha_corta(inicio, hoy)
    return f"{fecha_corta(inicio, hoy)} - {fecha_corta(fin, hoy)}"


def miles(n: int) -> str:
    return f"{n:,}".replace(",", ".")


def svg(datos: dict, hoy: date) -> str:
    c = COLORES
    actual_n, actual_ini, actual_fin = datos["actual"]
    larga_n, larga_ini, larga_fin = datos["larga"]
    primero = datos["primero"]
    desde = f"{primero.day} {MESES[primero.month - 1]} {primero.year} - Presente"
    actual_txt = rango(actual_ini, actual_fin, hoy)
    larga_txt = rango(larga_ini, larga_fin, hoy) if larga_n else "Sin racha"
    fuente = "font-family=\"'Segoe UI', Ubuntu, sans-serif\""

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 495 195" width="495" height="195" role="img" aria-label="Racha actual: {actual_n} días. Racha más larga: {larga_n} días. Total: {miles(datos['total'])} contribuciones.">
  <title>Racha de contribuciones</title>
  <rect x="0.5" y="0.5" width="494" height="194" rx="4.5" fill="{c['fondo']}" stroke="{c['borde']}"/>
  <line x1="165" y1="28" x2="165" y2="170" stroke="{c['borde']}"/>
  <line x1="330" y1="28" x2="330" y2="170" stroke="{c['borde']}"/>

  <g text-anchor="middle" {fuente}>
    <text x="82.5" y="79" fill="{c['numeros']}" font-size="28" font-weight="700">{miles(datos['total'])}</text>
    <text x="82.5" y="115" fill="{c['titulos']}" font-size="14">Contribuciones Totales</text>
    <text x="82.5" y="140" fill="{c['fechas']}" font-size="12">{desde}</text>

    <circle cx="247.5" cy="71" r="40" fill="none" stroke="{c['anillo']}" stroke-width="5"/>
    <rect x="234" y="20" width="27" height="16" fill="{c['fondo']}"/>
    <path transform="translate(235.5 19) scale(0.0234)" fill="{c['fuego']}" d="M512 0C512 0 128 304 128 640C128 852 300 1024 512 1024C724 1024 896 852 896 640C896 469 768 320 768 320C768 320 768 512 640 576C640 576 704 256 512 0ZM512 896C406 896 320 810 320 704C320 576 448 512 448 512C448 576 512 640 576 640C640 640 704 576 704 512C704 512 704 704 704 704C704 810 618 896 512 896Z"/>
    <text x="247.5" y="81" fill="{c['numero_racha']}" font-size="28" font-weight="700">{actual_n}</text>
    <text x="247.5" y="140" fill="{c['titulo_racha']}" font-size="14" font-weight="700">Racha Actual</text>
    <text x="247.5" y="160" fill="{c['fechas']}" font-size="12">{actual_txt}</text>

    <text x="412.5" y="79" fill="{c['numeros']}" font-size="28" font-weight="700">{larga_n}</text>
    <text x="412.5" y="115" fill="{c['titulos']}" font-size="14">Racha Más Larga</text>
    <text x="412.5" y="140" fill="{c['fechas']}" font-size="12">{larga_txt}</text>

  </g>
</svg>
"""


def main() -> None:
    token = os.environ["GH_TOKEN"]
    usuario = os.environ["USUARIO"]
    salida = Path(sys.argv[1] if len(sys.argv) > 1 else "assets/racha.svg")

    ahora = datetime.now(ZONA)
    hoy = ahora.date()
    datos = calcular(contribuciones_por_dia(token, usuario), hoy)

    salida.parent.mkdir(parents=True, exist_ok=True)
    salida.write_text(svg(datos, hoy), encoding="utf-8")
    print(
        f"Total {datos['total']}, racha actual {datos['actual'][0]} "
        f"({rango(datos['actual'][1], datos['actual'][2], hoy)}), "
        f"más larga {datos['larga'][0]} -> {salida}"
    )


if __name__ == "__main__":
    main()
