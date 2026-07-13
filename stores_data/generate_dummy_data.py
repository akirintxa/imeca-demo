"""
Generador de datos dummy de ventas — con perfiles distintos por sucursal.

Cada sucursal tiene su propio "carácter": rango de márgenes, categorías que
más vende, tamaño de ticket promedio, y qué tan irregulares son sus ventas
mes a mes. Todo lo ajustable está en la sección de PARÁMETROS al inicio.
"""

import pandas as pd
import random
import os
from datetime import datetime, timedelta

# --- Ruta de salida: este script vive en stores_data/, los CSV van en stores_data/raw/ ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_DIR = os.path.join(SCRIPT_DIR, 'raw')

# ============================================================
# PARÁMETROS AJUSTABLES — cambia estos valores para experimentar
# ============================================================

SEMILLA = 42  # fija la semilla para resultados reproducibles. Pon None para que cambie cada vez que corras el script.

FECHA_INICIO = datetime(2025, 1, 1)
NUM_MESES = 18  # Ene 2025 a Jun 2026 (aprox.)

# Pesos base de cada categoría en el catálogo (antes de aplicar la preferencia de cada sucursal)
CATEGORIAS_BASE = {
    'Plywood': 0.30, 'Cemento': 0.25, 'Tuberías': 0.15, 'Pinturas': 0.10,
    'Acero': 0.05, 'Eléctrico': 0.05, 'Ferretería': 0.03, 'Acabados': 0.03,
    'Herramientas': 0.02, 'Seguridad': 0.02
}

# Qué tan distinto es el margen de una categoría a otra DENTRO de la misma
# sucursal (0 = todas las categorías tienen el mismo margen; 0.3 = pueden
# variar hasta +/-30% respecto al rango base de esa sucursal)
VARIABILIDAD_MARGEN_CATEGORIA = 0.25

# --- Perfil de cada sucursal: aquí es donde defines las diferencias importantes ---
PERFILES_SUCURSAL = {
    'DEL': {
        'cantidad_facturas': 200,

        # Rango de margen general (multiplicador costo -> precio neto).
        # DEL vende con margen más alto en promedio.
        'margen_min': 1.45, 'margen_max': 2.00,

        # Tamaño del ticket: cuántos ítems por factura y cuántas unidades por ítem.
        # Rangos más altos = tickets promedio más grandes.
        'items_min': 2, 'items_max': 5,
        'cantidad_min': 2, 'cantidad_max': 6,

        # Qué tanto varían las ventas de un mes a otro (0 = parejo todo el año, 1 = muy irregular)
        'variabilidad_mensual': 0.65,

        # Multiplicador de peso por categoría: >1 vende más de esa categoría, <1 menos.
        # Las categorías que no se listan usan el peso base sin cambios.
        'preferencia_categorias': {
            'Plywood': 1.4, 'Acero': 1.6, 'Herramientas': 1.5, 'Cemento': 0.7, 'Seguridad': 0.5
        }
    },
    'PAL': {
        'cantidad_facturas': 300,

        # PAL vende con margen más ajustado (más descuento / menor markup)
        'margen_min': 1.15, 'margen_max': 1.60,

        # Tickets más chicos: menos ítems y menos unidades por factura
        'items_min': 1, 'items_max': 3,
        'cantidad_min': 1, 'cantidad_max': 4,

        # Más irregular mes a mes que DEL (para que a veces PAL venda mucho más
        # o mucho menos que DEL en un mismo mes)
        'variabilidad_mensual': 0.85,

        'preferencia_categorias': {
            'Cemento': 1.6, 'Tuberías': 1.5, 'Pinturas': 1.4, 'Acero': 0.4, 'Plywood': 0.7
        }
    }
}


def generar_pesos_mensuales(num_meses, variabilidad, rng):
    """Genera un peso relativo de ventas para cada mes. Con variabilidad alta,
    algunos meses tendrán muchas más facturas que otros (picos y valles)."""
    pesos = [max(0.05, rng.uniform(1 - variabilidad, 1 + variabilidad)) for _ in range(num_meses)]
    total = sum(pesos)
    return [p / total for p in pesos]


def generar_margenes_por_categoria(categorias, margen_min, margen_max, variabilidad, rng):
    """Asigna a cada categoría su propio rango de margen dentro del rango general
    de la sucursal, para que no todas las categorías rindan igual."""
    margenes = {}
    for cat in categorias:
        shift = rng.uniform(-variabilidad, variabilidad)
        centro_min = margen_min * (1 + shift)
        centro_max = margen_max * (1 + shift)
        # aseguramos que min < max y que no baje de un piso razonable
        centro_min = max(1.05, min(centro_min, centro_max - 0.05))
        margenes[cat] = (centro_min, centro_max)
    return margenes


def generar_datos_sucursal(nombre_sucursal, perfil, rng):
    categorias = list(CATEGORIAS_BASE.keys())

    # Pesos de categoría ajustados por la preferencia de esta sucursal
    preferencia = perfil.get('preferencia_categorias', {})
    pesos_categoria = [CATEGORIAS_BASE[c] * preferencia.get(c, 1.0) for c in categorias]

    # Margen propio por categoría (para que el mapa de calor de margen no salga plano)
    margenes_categoria = generar_margenes_por_categoria(
        categorias, perfil['margen_min'], perfil['margen_max'],
        VARIABILIDAD_MARGEN_CATEGORIA, rng
    )

    # Distribución de facturas por mes (con picos/valles según variabilidad_mensual)
    pesos_mes = generar_pesos_mensuales(NUM_MESES, perfil['variabilidad_mensual'], rng)
    meses = list(range(NUM_MESES))

    cantidad_facturas = perfil['cantidad_facturas']
    facturas_por_mes = rng.choices(meses, weights=pesos_mes, k=cantidad_facturas)

    datos = []
    for i in range(cantidad_facturas):
        invoice_no = f'{nombre_sucursal}{1000 + i}'
        mes_offset = facturas_por_mes[i]
        dia_aleatorio = rng.randint(0, 27)  # evita problemas con meses cortos
        fecha = fecha_sumar_meses(FECHA_INICIO, mes_offset, dia_aleatorio)

        num_items = rng.randint(perfil['items_min'], perfil['items_max'])

        for linea in range(1, num_items + 1):
            categoria = rng.choices(categorias, weights=pesos_categoria)[0]
            costo = round(rng.uniform(5, 40), 2)

            margen_min_cat, margen_max_cat = margenes_categoria[categoria]
            net_unit_price = round(costo * rng.uniform(margen_min_cat, margen_max_cat), 2)
            price_list = round(net_unit_price * 1.1, 2)
            price_limit = round(net_unit_price * 0.95, 2)
            price_std = net_unit_price

            cantidad = rng.randint(perfil['cantidad_min'], perfil['cantidad_max'])

            datos.append({
                'Invoice No': invoice_no,
                'Date': fecha.strftime('%d/%m/%Y'),
                'Line': linea * 10,
                'Product Code': f"{categoria[:3].upper()}-{rng.randint(100, 999)}",
                'Invoice Quantity': cantidad,
                'Unit Cost': costo,
                'Net Unit Price': net_unit_price,
                'Price List': price_list,
                'Price Limit': price_limit,
                'Price Std': price_std,
                'Category Name': categoria,
                'Total': round(cantidad * net_unit_price, 2)
            })

    df = pd.DataFrame(datos)
    os.makedirs(RAW_DIR, exist_ok=True)
    df.to_csv(os.path.join(RAW_DIR, f'ventas_{nombre_sucursal}.csv'), index=False)
    return df


def fecha_sumar_meses(fecha_inicio, meses_offset, dia):
    """Devuelve una fecha dentro del mes fecha_inicio + meses_offset, en el día indicado."""
    mes_total = fecha_inicio.month - 1 + meses_offset
    anio = fecha_inicio.year + mes_total // 12
    mes = mes_total % 12 + 1
    return datetime(anio, mes, 1) + timedelta(days=dia)


# ============================================================
# Generar datos
# ============================================================
rng = random.Random(SEMILLA)

df_del = generar_datos_sucursal('DEL', PERFILES_SUCURSAL['DEL'], rng)
df_pal = generar_datos_sucursal('PAL', PERFILES_SUCURSAL['PAL'], rng)

print("Datos generados exitosamente para DEL y PAL.")
print(f"DEL: {len(df_del)} líneas en {df_del['Invoice No'].nunique()} facturas")
print(f"PAL: {len(df_pal)} líneas en {df_pal['Invoice No'].nunique()} facturas")
