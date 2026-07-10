# Demo — Dashboard de Ventas Multi-Sucursal

Herramienta para analizar y visualizar ventas de tiendas de construcción,
con soporte para múltiples sucursales.

## 📁 Estructura del proyecto

| Archivo | Función |
|---|---|
| `df_generation.py` | Genera datos de ventas simulados para cada sucursal (`ventas_DEL.csv`, `ventas_PAL.csv`) |
| `analisis.ipynb` | Une los CSV de cada sucursal, crea la columna `Sede`, calcula márgenes y exporta `ventas_procesadas.csv` |
| `dashboard_ventas.ipynb` | Dashboard interactivo (filtros por sucursal/categoría/periodo) que consume el CSV procesado |
| `requirements.txt` | Dependencias del entorno |

## ⚙️ Requisitos

- Python 3.11+ (probado con 3.13)
- Un entorno virtual (recomendado)

## 🚀 Pasos para ejecutar el demo

### 1. Crear y activar el entorno virtual

```bash
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 3. (Opcional) Generar datos de ejemplo

Si no tienes ya un CSV de ventas, genera datos simulados:

```bash
python df_generation.py
```

Esto crea `ventas_DEL.csv` y `ventas_PAL.csv` en la carpeta actual.

> Si ya tienes tu propio archivo procesado (por ejemplo `ventas_procesadas_copy.csv`),
> puedes saltarte este paso y el siguiente — solo renómbralo a `ventas.csv` y ve directo al paso 5.

### 4. Procesar y unir los datos por sucursal

Abre `analisis.ipynb` en VS Code o Jupyter y ejecuta todas las celdas
(`Run All`). Esto:
- Une los CSV de cada sucursal en un solo DataFrame
- Crea la columna `Sede` a partir del prefijo de la factura
- Calcula márgenes y ventas mensuales
- Exporta el resultado final como `ventas_procesadas.csv`

### 5. Ejecutar el dashboard interactivo

1. Renombra o copia el archivo procesado como `ventas.csv` en la misma
   carpeta que `dashboard_ventas.ipynb` (o edita la variable `CSV_PATH`
   dentro del notebook si prefieres usar otro nombre).
2. Abre `dashboard_ventas.ipynb` en VS Code.
3. Selecciona el kernel de tu entorno virtual (ícono arriba a la derecha).
4. Ejecuta todas las celdas (`Run All`).
5. Al final aparecen los controles interactivos — cambia sucursal,
   categoría o rango de meses y los KPI y gráficas se actualizan solos.

## ➕ Agregar una nueva sucursal

No hace falta tocar código. Solo agrega las filas de la nueva tienda al
CSV con su propio valor en la columna `Sede` (por ejemplo `GYE`), y
vuelve a correr `dashboard_ventas.ipynb` — el filtro de sucursal se llena
automáticamente a partir de los datos.

## 🛠️ Problemas comunes

- **`ValueError: Mime type rendering requires nbformat>=4.2.0`**
  → Falta `nbformat` en el entorno activo. Corre `pip install nbformat`
  y reinicia el kernel del notebook.
- **`python`/`pip` no usan el entorno virtual aunque esté activado**
  → Revisa si tienes un alias en tu shell (`alias | grep python`) que
  esté pisando el PATH del venv. Bórralo del `.zshrc`/`.bashrc` y abre
  una terminal nueva.
