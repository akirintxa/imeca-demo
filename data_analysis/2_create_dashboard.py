"""
Genera un dashboard de ventas como un ÚNICO archivo HTML autocontenido.

Uso:
    python 2_create_dashboard.py                          # ../stores_data/processed/ventas.csv -> ../reports/dashboard_ventas.html
    python 2_create_dashboard.py otro.csv                  # CSV distinto -> ../reports/dashboard_ventas.html
    python 2_create_dashboard.py otro.csv salida.html       # CSV y nombre de salida distintos

Por defecto asume esta estructura de proyecto:
    proyecto/
      data_analysis/2_create_dashboard.py       <- este script
      stores_data/processed/ventas.csv           <- entrada
      reports/dashboard_ventas.html               <- salida (se crea si no existe)

El archivo .html resultante:
  - Es un dashboard interactivo completo (filtros de sucursal, categoría y
    periodo; KPI por sucursal + total; gráficas de ventas, categoría, mapa
    de calor de margen y comparativo entre sucursales).
  - NO necesita Python, Jupyter, ni conexión a internet más que cargar
    Plotly desde su CDN la primera vez que se abre.
  - Es el mismo archivo que ves tú y el que le compartes a alguien más:
    solo hay que enviarle el .html (por correo, Drive, etc.) y lo abre con
    doble clic en cualquier navegador.
"""

import sys
import os
import json
import pandas as pd

# --- Rutas por defecto, relativas a la ubicación de este script ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH_DEFAULT = os.path.join(SCRIPT_DIR, '..', 'stores_data', 'processed', 'ventas.csv')
OUTPUT_PATH_DEFAULT = os.path.join(SCRIPT_DIR, '..', 'reports', 'dashboard_ventas.html')


def cargar_datos(csv_path: str) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce')
    df['Mes'] = df['Date'].dt.to_period('M').astype(str)
    df['Margen_pct'] = (df['Net Unit Price'] - df['Unit Cost']) / df['Net Unit Price'] * 100
    df['Descuento_pct'] = (df['Price List'] - df['Net Unit Price']) / df['Price List'] * 100
    return df


def registros_para_html(df: pd.DataFrame) -> str:
    columnas = ['Invoice No', 'Sede', 'Category Name', 'Mes', 'Total',
                'Invoice Quantity', 'Margen_pct', 'Descuento_pct']
    registros = df[columnas].to_dict(orient='records')
    return json.dumps(registros, ensure_ascii=False)


HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>Dashboard de Ventas</title>
<script src="https://cdn.plot.ly/plotly-2.32.0.min.js"></script>
<style>
  * { box-sizing: border-box; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif;
    margin: 0; padding: 24px; background: #f5f6f8; color: #1a1a1a;
  }
  .contenedor { max-width: 1100px; margin: 0 auto; }
  .header {
    background: linear-gradient(90deg,#1f3b57,#2c6e91); color: white;
    padding: 20px 28px; border-radius: 12px 12px 0 0;
  }
  .header h1 { margin: 0; font-size: 22px; font-weight: 600; }
  .header p { margin: 4px 0 0; opacity: 0.85; font-size: 13px; }
  .filtros {
    background: #fff; border: 1px solid #dfe3e6; border-top: none;
    padding: 18px 28px; display: flex; gap: 20px; flex-wrap: wrap; align-items: flex-end;
  }
  .campo { display: flex; flex-direction: column; gap: 4px; }
  .campo label { font-size: 12px; color: #555; font-weight: 600; }
  .campo select {
    padding: 7px 10px; border-radius: 6px; border: 1px solid #ccc; font-size: 14px; min-width: 160px;
  }
  .cuerpo { background: #fff; border: 1px solid #dfe3e6; border-top: none;
            border-radius: 0 0 12px 12px; padding: 20px 28px 32px; }
  .periodo-label { color: #666; font-size: 13px; margin-bottom: 12px; }
  .kpis { display: flex; gap: 16px; flex-wrap: wrap; margin-bottom: 20px; }
  .kpi-card { background: #f4f4f4; padding: 12px 20px; border-radius: 8px; min-width: 140px; }
  .kpi-card .label { font-size: 12px; color: #666; }
  .kpi-card .valor { font-size: 22px; font-weight: bold; }
  table.kpi-tabla { border-collapse: collapse; margin-bottom: 20px; font-size: 14px; width: 100%; }
  table.kpi-tabla th { background: #f4f4f4; text-align: left; padding: 8px 12px; }
  table.kpi-tabla td { padding: 8px 12px; border-bottom: 1px solid #eee; }
  table.kpi-tabla tr.total { font-weight: bold; background: #eaeaea; }
  .grafico { margin-bottom: 28px; }
  .footer-note { color: #999; font-size: 12px; margin-top: 8px; text-align: right; }
</style>
</head>
<body>
<div class="contenedor">
  <div class="header">
    <h1>📊 Panel de Ventas</h1>
    <p id="subtitulo">Cargando datos...</p>
  </div>
  <div class="filtros">
    <div class="campo">
      <label>Sucursal</label>
      <select id="f-sede"></select>
    </div>
    <div class="campo">
      <label>Categoría</label>
      <select id="f-categoria"></select>
    </div>
    <div class="campo">
      <label>Periodo rápido</label>
      <select id="f-preset"></select>
    </div>
    <div class="campo" id="campo-desde" style="display:none;">
      <label>Desde</label>
      <select id="f-desde"></select>
    </div>
    <div class="campo" id="campo-hasta" style="display:none;">
      <label>Hasta</label>
      <select id="f-hasta"></select>
    </div>
  </div>
  <div class="cuerpo">
    <div class="periodo-label" id="periodo-label"></div>
    <div id="kpi-area"></div>
    <div class="grafico" id="fig-mes"></div>
    <div class="grafico" id="fig-categoria"></div>
    <div class="grafico" id="fig-heatmap"></div>
    <div class="grafico" id="fig-comparativo"></div>
    <div class="footer-note">Generado automáticamente a partir de ventas.csv</div>
  </div>
</div>

<script>
const DATA = __DATA_JSON__;
const COLORES_SEDE = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b'];

function unico(arr) { return [...new Set(arr)].sort(); }

const sedes = unico(DATA.map(r => r.Sede));
const categorias = unico(DATA.map(r => r['Category Name']));
const meses = unico(DATA.map(r => r.Mes));
const anios = unico(meses.map(m => m.slice(0, 4)));

let presets = ['Todo el periodo'];
anios.forEach(a => presets.push('Año ' + a + ' completo'));
presets.push('Últimos 3 meses', 'Últimos 6 meses', 'Últimos 12 meses', 'Personalizado');

function llenarSelect(id, opciones, valorDefault) {
  const el = document.getElementById(id);
  el.innerHTML = '';
  opciones.forEach(op => {
    const o = document.createElement('option');
    o.value = op; o.textContent = op;
    if (op === valorDefault) o.selected = true;
    el.appendChild(o);
  });
}

llenarSelect('f-sede', ['Todas', ...sedes], 'Todas');
llenarSelect('f-categoria', ['Todas', ...categorias], 'Todas');
llenarSelect('f-preset', presets, 'Todo el periodo');
llenarSelect('f-desde', meses, meses[0]);
llenarSelect('f-hasta', meses, meses[meses.length - 1]);

document.getElementById('subtitulo').textContent =
  'Sucursales: ' + sedes.length + ' · ' + DATA.length + ' líneas · Vista unificada';

function aplicarPreset() {
  const val = document.getElementById('f-preset').value;
  const desdeSel = document.getElementById('f-desde');
  const hastaSel = document.getElementById('f-hasta');
  const camposCustom = [document.getElementById('campo-desde'), document.getElementById('campo-hasta')];

  if (val === 'Todo el periodo') {
    desdeSel.value = meses[0]; hastaSel.value = meses[meses.length - 1];
    camposCustom.forEach(c => c.style.display = 'none');
  } else if (val === 'Personalizado') {
    camposCustom.forEach(c => c.style.display = 'flex');
  } else if (val.startsWith('Año ')) {
    const anio = val.split(' ')[1];
    const mesesAnio = meses.filter(m => m.startsWith(anio));
    desdeSel.value = mesesAnio[0]; hastaSel.value = mesesAnio[mesesAnio.length - 1];
    camposCustom.forEach(c => c.style.display = 'none');
  } else {
    const n = parseInt(val.split(' ')[1]);
    desdeSel.value = meses[Math.max(0, meses.length - n)];
    hastaSel.value = meses[meses.length - 1];
    camposCustom.forEach(c => c.style.display = 'none');
  }
  render();
}

function filtrar(sede, categoria, desde, hasta) {
  return DATA.filter(r =>
    (sede === 'Todas' || r.Sede === sede) &&
    (categoria === 'Todas' || r['Category Name'] === categoria) &&
    r.Mes >= desde && r.Mes <= hasta
  );
}

function calcularKPIs(rows) {
  const ventas = rows.reduce((s, r) => s + r.Total, 0);
  const porFactura = {};
  rows.forEach(r => { porFactura[r['Invoice No']] = (porFactura[r['Invoice No']] || 0) + r.Total; });
  const nFacturas = Object.keys(porFactura).length;
  const ticketProm = nFacturas ? Object.values(porFactura).reduce((a, b) => a + b, 0) / nFacturas : 0;
  const margenProm = rows.length ? rows.reduce((s, r) => s + r.Margen_pct, 0) / rows.length : 0;
  const descuentoProm = rows.length ? rows.reduce((s, r) => s + r.Descuento_pct, 0) / rows.length : 0;
  const unidades = rows.reduce((s, r) => s + r['Invoice Quantity'], 0);
  return { ventas, facturas: nFacturas, ticketProm, margenProm, descuentoProm, unidades };
}

function fmtMoney(v) { return '$' + v.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }); }
function fmtPct(v) { return v.toLocaleString('en-US', { minimumFractionDigits: 1, maximumFractionDigits: 1 }) + '%'; }
function fmtInt(v) { return Math.round(v).toLocaleString('en-US'); }

function renderKPI(rows, sedeSeleccionada, sedesEnFiltro) {
  const area = document.getElementById('kpi-area');
  if (sedeSeleccionada === 'Todas' && sedesEnFiltro.length > 1) {
    let filas = sedesEnFiltro.map(s => {
      const k = calcularKPIs(rows.filter(r => r.Sede === s));
      return { sede: s, ...k };
    });
    const total = calcularKPIs(rows);
    filas.push({ sede: 'TOTAL', ...total });

    let html = '<table class="kpi-tabla"><thead><tr>' +
      '<th>Sucursal</th><th>Ventas</th><th>Facturas</th><th>Ticket prom.</th>' +
      '<th>Margen %</th><th>Descuento %</th><th>Unidades</th></tr></thead><tbody>';
    filas.forEach(f => {
      const claseTotal = f.sede === 'TOTAL' ? ' class="total"' : '';
      html += `<tr${claseTotal}><td>${f.sede}</td><td>${fmtMoney(f.ventas)}</td>` +
        `<td>${fmtInt(f.facturas)}</td><td>${fmtMoney(f.ticketProm)}</td>` +
        `<td>${fmtPct(f.margenProm)}</td><td>${fmtPct(f.descuentoProm)}</td>` +
        `<td>${fmtInt(f.unidades)}</td></tr>`;
    });
    html += '</tbody></table>';
    area.innerHTML = html;
  } else {
    const k = calcularKPIs(rows);
    area.innerHTML = `
      <div class="kpis">
        <div class="kpi-card"><div class="label">VENTAS TOTALES</div><div class="valor">${fmtMoney(k.ventas)}</div></div>
        <div class="kpi-card"><div class="label">FACTURAS</div><div class="valor">${fmtInt(k.facturas)}</div></div>
        <div class="kpi-card"><div class="label">TICKET PROMEDIO</div><div class="valor">${fmtMoney(k.ticketProm)}</div></div>
        <div class="kpi-card"><div class="label">MARGEN % PROMEDIO</div><div class="valor">${fmtPct(k.margenProm)}</div></div>
        <div class="kpi-card"><div class="label">DESCUENTO PROMEDIO</div><div class="valor">${fmtPct(k.descuentoProm)}</div></div>
        <div class="kpi-card"><div class="label">UNIDADES VENDIDAS</div><div class="valor">${fmtInt(k.unidades)}</div></div>
      </div>`;
  }
}

function agrupar(rows, keyFn, valFn) {
  const acc = {};
  rows.forEach(r => {
    const k = keyFn(r);
    if (!acc[k]) acc[k] = [];
    acc[k].push(r);
  });
  const out = {};
  Object.keys(acc).forEach(k => { out[k] = valFn(acc[k]); });
  return out;
}

function renderVentasPorMes(rows) {
  const sedesEnFiltro = unico(rows.map(r => r.Sede));
  const traces = sedesEnFiltro.map((sede, i) => {
    const rowsSede = rows.filter(r => r.Sede === sede);
    const porMes = agrupar(rowsSede, r => r.Mes, rs => rs.reduce((s, r) => s + r.Total, 0));
    const mesesOrdenados = Object.keys(porMes).sort();
    return {
      x: mesesOrdenados, y: mesesOrdenados.map(m => porMes[m]),
      type: 'scatter', mode: 'lines+markers', name: sede,
      line: { color: COLORES_SEDE[i % COLORES_SEDE.length] }
    };
  });
  Plotly.react('fig-mes', traces, {
    title: 'Ventas por mes', height: 350, margin: { t: 40, b: 40 },
    xaxis: { title: 'Mes' }, yaxis: { title: 'Ventas ($)' }
  }, { displaylogo: false, responsive: true });
}

function renderCategoria(rows, sedesEnFiltro) {
  // Orden de categorías: de mayor a menor venta total (combinando todas las sucursales del filtro)
  const porCatTotal = agrupar(rows, r => r['Category Name'], rs => rs.reduce((s, r) => s + r.Total, 0));
  const cats = Object.keys(porCatTotal).sort((a, b) => porCatTotal[b] - porCatTotal[a]);

  let traces = [];
  let titulo = 'Ventas por categoría (barras) vs. Margen % promedio (línea)';

  if (sedesEnFiltro.length > 1) {
    titulo = 'Ventas por categoría vs. Margen % — comparativo por sucursal';

    sedesEnFiltro.forEach((sede, i) => {
      const rowsSede = rows.filter(r => r.Sede === sede);
      const porCat = agrupar(rowsSede, r => r['Category Name'], rs => rs.reduce((s, r) => s + r.Total, 0));
      const color = COLORES_SEDE[i % COLORES_SEDE.length];
      traces.push({
        x: cats, y: cats.map(c => porCat[c] || 0), type: 'bar',
        name: 'Ventas — ' + sede, marker: { color }, legendgroup: sede
      });
    });

    sedesEnFiltro.forEach((sede, i) => {
      const rowsSede = rows.filter(r => r.Sede === sede);
      const porCat = agrupar(rowsSede, r => r['Category Name'], rs => rs.reduce((s, r) => s + r.Margen_pct, 0) / rs.length);
      const color = COLORES_SEDE[i % COLORES_SEDE.length];
      traces.push({
        x: cats, y: cats.map(c => porCat[c] !== undefined ? porCat[c] : null), name: 'Margen % — ' + sede,
        yaxis: 'y2', type: 'scatter', mode: 'lines+markers', legendgroup: sede,
        line: { color, dash: 'dot' }, marker: { symbol: 'diamond', size: 7 }
      });
    });
  } else {
    const porCat = agrupar(rows, r => r['Category Name'], rs => ({
      ventas: rs.reduce((s, r) => s + r.Total, 0),
      margen: rs.reduce((s, r) => s + r.Margen_pct, 0) / rs.length
    }));
    traces = [
      { x: cats, y: cats.map(c => porCat[c].ventas), type: 'bar', name: 'Ventas ($)' },
      { x: cats, y: cats.map(c => porCat[c].margen), name: 'Margen %', yaxis: 'y2',
        type: 'scatter', mode: 'lines+markers', line: { color: 'crimson' } }
    ];
  }

  Plotly.react('fig-categoria', traces, {
    title: titulo, height: 400, margin: { t: 40, b: 60 }, barmode: 'group',
    yaxis: { title: 'Ventas ($)' },
    yaxis2: { title: 'Margen %', overlaying: 'y', side: 'right' },
    legend: { orientation: 'h', yanchor: 'bottom', y: 1.02, xanchor: 'right', x: 1 }
  }, { displaylogo: false, responsive: true });
}

function renderHeatmap(rows, sedesEnFiltro) {
  const div = document.getElementById('fig-heatmap');
  div.style.display = 'block';

  const cats = unico(rows.map(r => r['Category Name']));
  const matrizPorCat = {};
  cats.forEach(cat => {
    matrizPorCat[cat] = sedesEnFiltro.map(sede => {
      const subset = rows.filter(r => r['Category Name'] === cat && r.Sede === sede);
      return subset.length ? subset.reduce((s, r) => s + r.Margen_pct, 0) / subset.length : null;
    });
  });
  const catsOrdenadas = cats.slice().sort((a, b) => {
    const promA = matrizPorCat[a].filter(v => v !== null).reduce((s, v) => s + v, 0) / matrizPorCat[a].length;
    const promB = matrizPorCat[b].filter(v => v !== null).reduce((s, v) => s + v, 0) / matrizPorCat[b].length;
    return promB - promA;
  });
  const z = catsOrdenadas.map(c => matrizPorCat[c]);
  const texto = z.map(fila => fila.map(v => v === null ? '' : v.toFixed(1)));
  const valoresValidos = z.flat().filter(v => v !== null);
  const zmax = Math.max(60, ...valoresValidos);

  Plotly.react('fig-heatmap', [{
    z, x: sedesEnFiltro, y: catsOrdenadas, type: 'heatmap', colorscale: 'RdYlGn',
    zmin: 0, zmax: zmax,
    text: texto, texttemplate: '%{text}', colorbar: { title: 'Margen %' }
  }], {
    title: 'Mapa de calor — Margen % por Categoría y Sucursal',
    height: Math.max(320, 40 * catsOrdenadas.length + 100), margin: { t: 40, b: 40 }
  }, { displaylogo: false, responsive: true });
}

function renderComparativo(rows, sedesEnFiltro) {
  const div = document.getElementById('fig-comparativo');
  if (sedesEnFiltro.length <= 1) { Plotly.purge(div); div.style.display = 'none'; return; }
  div.style.display = 'block';

  const porSede = agrupar(rows, r => r.Sede, rs => rs.reduce((s, r) => s + r.Total, 0));
  const sedesOrd = sedesEnFiltro;
  Plotly.react('fig-comparativo', [{
    x: sedesOrd, y: sedesOrd.map(s => porSede[s]), type: 'bar',
    marker: { color: sedesOrd.map((_, i) => COLORES_SEDE[i % COLORES_SEDE.length]) },
    text: sedesOrd.map(s => fmtMoney(porSede[s])), textposition: 'outside'
  }], {
    title: 'Comparativo de ventas por sucursal', height: 320, margin: { t: 40, b: 40 }, showlegend: false
  }, { displaylogo: false, responsive: true });
}

function render() {
  const sede = document.getElementById('f-sede').value;
  const categoria = document.getElementById('f-categoria').value;
  const desde = document.getElementById('f-desde').value;
  const hasta = document.getElementById('f-hasta').value;

  const rows = filtrar(sede, categoria, desde, hasta);
  document.getElementById('periodo-label').innerHTML =
    'Periodo: <b>' + (desde === hasta ? desde : desde + ' a ' + hasta) + '</b>';

  if (rows.length === 0) {
    document.getElementById('kpi-area').innerHTML = '<p>No hay datos para este filtro.</p>';
    ['fig-mes', 'fig-categoria', 'fig-heatmap', 'fig-comparativo'].forEach(id => Plotly.purge(document.getElementById(id)));
    return;
  }

  const sedesEnFiltro = unico(rows.map(r => r.Sede));
  renderKPI(rows, sede, sedesEnFiltro);
  renderVentasPorMes(rows);
  renderCategoria(rows, sedesEnFiltro);
  renderHeatmap(rows, sedesEnFiltro);
  renderComparativo(rows, sedesEnFiltro);
}

['f-sede', 'f-categoria', 'f-desde', 'f-hasta'].forEach(id =>
  document.getElementById(id).addEventListener('change', render)
);
document.getElementById('f-preset').addEventListener('change', aplicarPreset);

render();
</script>
</body>
</html>
"""


def main():
    csv_path = sys.argv[1] if len(sys.argv) > 1 else CSV_PATH_DEFAULT
    output_path = sys.argv[2] if len(sys.argv) > 2 else OUTPUT_PATH_DEFAULT

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    df = cargar_datos(csv_path)
    data_json = registros_para_html(df)

    html = HTML_TEMPLATE.replace('__DATA_JSON__', data_json)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"Dashboard exportado a '{output_path}'")
    print(f"  {len(df):,} líneas · {df['Invoice No'].nunique():,} facturas · "
          f"{df['Sede'].nunique()} sucursales: {list(df['Sede'].unique())}")


if __name__ == '__main__':
    main()
