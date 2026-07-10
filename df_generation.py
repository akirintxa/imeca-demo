import pandas as pd
import random
from datetime import datetime, timedelta

def generar_datos_sucursal(nombre_sucursal, cantidad_facturas):
    # 1. Catálogo con tendencias de materiales de construcción
    categorias = {
        'Plywood': 0.30, 'Cemento': 0.25, 'Tuberías': 0.15, 'Pinturas': 0.10, 
        'Acero': 0.05, 'Eléctrico': 0.05, 'Ferretería': 0.03, 'Acabados': 0.03, 
        'Herramientas': 0.02, 'Seguridad': 0.02
    }
    productos = list(categorias.keys())
    pesos = list(categorias.values())
    
    datos = []
    
    # Rango de fechas: Ene 2025 a Jun 2026 (aprox 545 días)
    fecha_inicio = datetime(2025, 1, 1)
    
    for i in range(cantidad_facturas):
        invoice_no = f'{nombre_sucursal}{1000 + i}'
        # Distribución de fechas uniforme en el periodo
        fecha = (fecha_inicio + timedelta(days=random.randint(0, 545))).strftime('%d/%m/%Y')
        
        # Objetivo de factura: entre 50 y 300 dólares
        meta_total_factura = random.uniform(50, 300)
        num_items = random.randint(1, 4)
        
        # Distribuimos la meta entre los ítems
        for linea in range(1, num_items + 1):
            categoria = random.choices(productos, weights=pesos)[0]
            costo = round(random.uniform(5, 40), 2)
            
            # Precios de referencia
            net_unit_price = round(costo * random.uniform(1.3, 1.9), 2)
            price_list = round(net_unit_price * 1.1, 2)
            price_limit = round(net_unit_price * 0.95, 2)
            price_std = net_unit_price
            
            # Cantidad y precio total por línea para ajustar al objetivo de factura
            cantidad = random.randint(1, 5)
            
            datos.append({
                'Invoice No': invoice_no,
                'Date': fecha,
                'Line': linea * 10,
                'Product Code': f"{categoria[:3].upper()}-{random.randint(100,999)}",
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
    # Guardar CSV
    df.to_csv(f'ventas_{nombre_sucursal}.csv', index=False)
    return df

# Generar datos
df_pal = generar_datos_sucursal('PAL', 200)
df_del = generar_datos_sucursal('DEL', 200)

print("Datos generados exitosamente para PAL y DEL.")