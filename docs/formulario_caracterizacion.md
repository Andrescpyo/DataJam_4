# Formulario de caracterización y formulación del problema

## 1. Pregunta analítica
¿Cómo se relacionan la exposición al calor urbano, la contaminación atmosférica, la población y la cobertura vegetal en las Unidades de Planeamiento Local (UPL) de Bogotá D.C. durante 2023 y 2024?

## 2. Hipótesis
Las UPL con mayor temperatura y mayor concentración de PM2.5 tienden a concentrar condiciones de mayor exposición urbana, con cambios espaciales y temporales que pueden asociarse a diferencias de población y a la disponibilidad de vegetación urbana.

## 3. Datasets utilizados
- UPL oficial de Bogotá D.C. (geometría base)
- Población por UPL
- PM2.5 promedio anual
- Temperatura media superficial anual
- Densidad de arbolado urbano (cuando fue posible abrir el raster oficial)

## 4. Herramientas empleadas
- Python
- GeoPandas
- Pandas
- NumPy
- Rasterio
- Rasterstats
- Matplotlib
- Seaborn
- QGIS

## 5. Metodología general
1. Carga y validación de la geometría base de UPL.
2. Limpieza de registros y homogeneización de identificadores.
3. Agregación de población por UPL y año.
4. Cálculo de promedios ponderados por área para PM2.5 y temperatura.
5. Integración espacial a la UPL como unidad base.
6. Diagnóstico de calidad y análisis descriptivo.
7. Generación de productos reproducibles y visualizaciones.

## 6. Resultados esperados
- Identificar UPL con mayor exposición térmica y ambiental.
- Comparar 2023 y 2024.
- Evaluar asociaciones espaciales entre variables clave.
- Generar insumos para interpretación técnica institucional.

## 7. Observaciones metodológicas
- La investigación se sostiene en asociación y patrones espaciales, no causalidad.
- La densidad de arbolado se trató como una variable limitada por la disponibilidad del raster oficial.
- La comparación se mantiene en el período 2023-2024 por la regla del proyecto.
