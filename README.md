# Demo — Dashboard de Ventas Multi-Sucursal

Herramienta para analizar y visualizar ventas de tiendas de construcción,
con soporte para múltiples sucursales.

## 📁 Estructura del proyecto

```
IMECA-DEMO/
├── data_analysis/
│   ├── 0_process_data.ipynb     ← une los CSV crudos por sucursal y calcula columnas derivadas
│   ├── 1_analyse_data.ipynb     ← dashboard interactivo (Jupyter/VS Code)
│   └── 2_create_dashboard.py    ← exporta el dashboard como un .html autocontenido
├── stores_data/
│   ├── data_generation.py       ← genera datos de ventas simulados (opcional)
│   ├── raw/                     ← CSV crudos por sucursal (ventas_DEL.csv, ventas_PAL.csv)
│   └── processed/                ← ventas.csv ya unido y listo para analizar
├── reports/                      ← dashboard_ventas.html generado (para compartir)
├── tests/                        ← pruebas del proyecto (ver sugerencia abajo)
├── requirements.txt
└── README.md
```

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

Si no tienes ya CSV de ventas por sucursal, genera datos simulados:

```bash
python stores_data/data_generation.py
```

Esto crea `stores_data/raw/ventas_DEL.csv` y `stores_data/raw/ventas_PAL.csv`.

> Si ya tienes tus propios CSV crudos, colócalos en `stores_data/raw/` con el
> mismo formato de columnas y sáltate este paso.

### 4. Procesar y unir los datos por sucursal

Abre `data_analysis/0_process_data.ipynb` en VS Code o Jupyter y ejecuta
todas las celdas (`Run All`). Esto:
- Une los CSV de `stores_data/raw/` en un solo DataFrame
- Crea la columna `Sede` a partir del prefijo de la factura
- Exporta el resultado como `stores_data/processed/ventas.csv`

### 5. Explorar el dashboard interactivo (Jupyter/VS Code)

1. Abre `data_analysis/1_analyse_data.ipynb`.
2. Selecciona el kernel de tu entorno virtual (ícono arriba a la derecha).
3. Ejecuta todas las celdas (`Run All`).
4. Al final aparecen los controles interactivos — cambia sucursal,
   categoría o periodo y los KPI y gráficas se actualizan solos.

### 6. Generar el dashboard como archivo para compartir

```bash
cd data_analysis
python 2_create_dashboard.py
```

Esto crea `reports/dashboard_ventas.html` — un solo archivo que cualquiera
puede abrir con doble clic en su navegador, sin instalar Python.

## ➕ Agregar una nueva sucursal

No hace falta tocar código. Agrega el CSV crudo de la tienda nueva en
`stores_data/raw/`, vuelve a correr `0_process_data.ipynb` y luego
`1_analyse_data.ipynb` o `2_create_dashboard.py` — el filtro de sucursal
se llena automáticamente a partir de los datos.

## 🧪 Sobre la carpeta `tests/`

Aún vacía — si el proyecto va a crecer, vale la pena agregar pruebas
simples para lo que más se rompe al cambiar cosas:
- Que `stores_data/processed/ventas.csv` tenga las columnas esperadas
  después de correr `0_process_data.ipynb`.
- Que `data_generation.py` con una `SEMILLA` fija produzca siempre el
  mismo número de filas (prueba de regresión simple).
- Que `2_create_dashboard.py` genere un `.html` no vacío a partir de un
  CSV de prueba pequeño incluido en `tests/fixtures/`.

## 🛠️ Problemas comunes

- **`ValueError: Mime type rendering requires nbformat>=4.2.0`**
  → Falta `nbformat` en el entorno activo. Corre `pip install nbformat`
  y reinicia el kernel del notebook.
- **`python`/`pip` no usan el entorno virtual aunque esté activado**
  → Revisa si tienes un alias en tu shell (`alias | grep python`) que
  esté pisando el PATH del venv. Bórralo del `.zshrc`/`.bashrc` y abre
  una terminal nueva.
- **Las gráficas de Plotly aparecen duplicadas en VS Code**
  → Usa `1_analyse_data.ipynb` tal cual está: las gráficas son
  `FigureWidget` que se actualizan en el mismo lugar, en vez de volver a
  dibujarse cada vez (esa combinación es la que causaba duplicados).

