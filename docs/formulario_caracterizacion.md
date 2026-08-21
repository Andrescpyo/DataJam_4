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

## 6. Problema público a abordar
El problema que se desea analizar es la posible concentración de riesgo ambiental y socioeconómico en algunas Unidades de Planeamiento Local (UPL) de Bogotá D.C. En particular, se busca entender si las zonas con mayor vulnerabilidad socioeconómica y mayor exposición a la contaminación atmosférica y al calor urbano presentan menor cobertura de arbolado urbano. Este patrón es relevante porque la baja presencia de vegetación puede afectar la calidad del aire, la sensación térmica, la salud respiratoria y la resiliencia climática de la población, especialmente en sectores con mayor presión demográfica y menor capacidad adaptativa.

## 7. Justificación del problema
Este problema es relevante porque el bienestar urbano, la salud ambiental y la justicia climática no se distribuyen de manera homogénea en la ciudad. En Bogotá, ciertos territorios concentran condiciones de mayor exposición al calor y a contaminantes, al tiempo que pueden tener menor cobertura vegetal y mayores condiciones de vulnerabilidad social. Esto afecta de manera desproporcionada a residentes de estratos bajos, población infantil, adultos mayores y personas con condiciones de salud previas, además de influir en la calidad del espacio público y en la sostenibilidad del territorio. Analizar este problema permite orientar decisiones de planificación urbana, gestión ambiental y políticas de arborización y adaptación climática con mayor evidencia territorial.

## 8. Delimitación del análisis
El ejercicio se desarrolla a escala territorial en Bogotá D.C., con la Unidad de Planeamiento Local (UPL) como unidad de análisis. Se centra en el período 2023-2024 y aborda una dimensión ambiental, socioeconómica y urbana. Desde el punto de vista sectorial, se integra la relación entre planificación territorial, salud ambiental, clima urbano y gestión del arbolado. Desde la población, se considera la distribución de la población por UPL y la forma en que la vulnerabilidad socioeconómica se concentra espacialmente. Institucionalmente, el análisis se apoya en fuentes de la Secretaría Distrital de Planeación, la Secretaría Distrital de Salud, la Secretaría Distrital de Ambiente, el Catastro Distrital y el Jardín Botánico de Bogotá.

## 9. Pregunta de análisis
¿Cómo se relacionan la vulnerabilidad socioeconómica, la exposición al calor urbano, la contaminación atmosférica, la densidad poblacional y la cobertura de arbolado urbano en las UPL de Bogotá D.C. durante 2023 y 2024?

## 10. Hipótesis o expectativa analítica preliminar
Se espera encontrar que las UPL con mayor vulnerabilidad socioeconómica y/o mayor exposición a la contaminación presentan una menor densidad de arbolado urbano. Asimismo, se hipotetiza que la temperatura y la densidad poblacional pueden reforzar la presión ambiental y territorial sobre estas zonas, aunque no se pretende afirmar causalidad, sino identificar patrones de asociación espacial que orienten análisis posteriores. En términos analíticos, se espera una relación negativa entre vulnerabilidad y PM2.5 con la cobertura arbórea, y una asociación más débil o complementaria de la temperatura y la densidad poblacional.

## 11. Observaciones metodológicas
- La investigación se sostiene en asociación y patrones espaciales, no causalidad.
- La densidad de arbolado se trató como una variable integrada desde la fuente institucional oficial, usando consultas por punto y un promedio territorial por UPL sin inventar datos.
- La comparación se mantiene en el período 2023-2024 por la regla del proyecto.
- El modelo final usa 64 observaciones completas, obtiene R²=0.131 y presenta coeficientes estandarizados negativos para vulnerabilidad socioeconómica (-0.246) y PM2.5 (-0.239), y positivos para temperatura (0.167) y densidad poblacional (0.383). El resultado es exploratorio y no causal.
