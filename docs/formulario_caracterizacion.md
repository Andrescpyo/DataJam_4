# Formulario de caracterización y formulación del problema

## 1. Pregunta analítica
¿Cómo se relacionan la vulnerabilidad socioeconómica, la exposición al calor urbano, la contaminación atmosférica, la densidad poblacional y la cobertura vegetal en las Unidades de Planeamiento Local (UPL) de Bogotá D.C. durante 2023 y 2024?

## 2. Hipótesis
Las UPL con mayor vulnerabilidad socioeconómica y/o mayor exposición a la contaminación tienen una menor cobertura de arbolado urbano. La temperatura y la densidad poblacional pueden modificar el patrón territorial observado.

## 3. Datasets utilizados
- UPL oficial de Bogotá D.C. (geometría base)
- Población por UPL
- PM2.5 promedio anual
- Temperatura media superficial anual
- Densidad de arbolado urbano (valores oficiales del servicio institucional del Jardín Botánico de Bogotá, consultados por punto y agregados por UPL)
- Estratificación socioeconómica por manzanas (Catastro Distrital)

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
8. Modelo OLS estandarizado con densidad de arbolado como respuesta.

## 6. Resultados esperados
- Identificar UPL con mayor exposición térmica y ambiental.
- Comparar 2023 y 2024.
- Evaluar asociaciones espaciales entre variables clave.
- Generar insumos para interpretación técnica institucional.

## 7. Observaciones metodológicas
- La investigación se sostiene en asociación y patrones espaciales, no causalidad.
- La densidad de arbolado se trató como una variable integrada desde la fuente institucional oficial, usando consultas por punto y un promedio territorial por UPL sin inventar datos.
- La comparación se mantiene en el período 2023-2024 por la regla del proyecto.
- El modelo final usa 64 observaciones completas, obtiene R²=0.131 y presenta coeficientes estandarizados negativos para vulnerabilidad socioeconómica (-0.246) y PM2.5 (-0.239), y positivos para temperatura (0.167) y densidad poblacional (0.383). El resultado es exploratorio y no causal.
