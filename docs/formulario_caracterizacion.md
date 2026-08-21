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

## 11. Fuentes de datos identificadas
- Nombre del conjunto de datos: Unidades de Planeamiento Local (UPL) de Bogotá D.C.
  - Entidad fuente: Secretaría Distrital de Planeación
  - Enlace: https://datosabiertos.bogota.gov.co/

- Nombre del conjunto de datos: Población por UPL
  - Entidad fuente: Secretaría Distrital de Salud
  - Enlace: https://datosabiertos.bogota.gov.co/

- Nombre del conjunto de datos: PM2.5 promedio anual
  - Entidad fuente: Secretaría Distrital de Ambiente
  - Enlace: Portal de Datos Abiertos y servicios ArcGIS institucionales

- Nombre del conjunto de datos: Temperatura media superficial anual
  - Entidad fuente: Secretaría Distrital de Ambiente
  - Enlace: Portal de Datos Abiertos y servicios ArcGIS institucionales

- Nombre del conjunto de datos: Densidad de arbolado urbano
  - Entidad fuente: Jardín Botánico de Bogotá
  - Enlace: servicio institucional ArcGIS del Jardín Botánico de Bogotá

- Nombre del conjunto de datos: Estratificación socioeconómica por manzana
  - Entidad fuente: Catastro Distrital
  - Enlace: servicio ArcGIS institucional de estratificación

## 12. Variables clave identificadas
- Código y nombre de la UPL
- Año de observación (2023 y 2024)
- Población total por UPL
- Densidad poblacional (población / área de la UPL)
- Temperatura media superficial anual
- PM2.5 promedio anual
- Estrato medio por UPL
- Proporción de área en estratos 1-2
- Vulnerabilidad socioeconómica proxy (-estrato medio)
- Densidad de arbolado urbano por UPL

## 13. Posible estrategia de integración de datos
La estrategia de integración se basa principalmente en la relación territorial por Unidad de Planeamiento Local (UPL), que funciona como llave de unión entre las distintas fuentes. La geometría de las UPL sirve como base espacial y se integran las tablas de población, contaminación, temperatura y estratificación a través de intersecciones y agregaciones por área. Además, se compara el mismo contexto territorial en dos años (2023 y 2024), lo que permite identificar cambios temporales y diferencias entre ciclos anuales. La integración se realiza mediante una lógica geoespacial y anual, priorizando la consistencia territorial sobre el análisis individual por observación aislada.

## 14. ¿Los datos seleccionados contienen información geográfica, territorial o de segmentación institucional relevante para el análisis?
Parcialmente.

La base contiene información geográfica y territorial relevante porque las UPL, la estratificación por manzana y la capa ambiental se integran a nivel espacial. También incluye segmentación institucional a través de las unidades territoriales y los datos de la administración distrital. Sin embargo, no se trata de una segmentación poblacional detallada por sexo, edad o grupo diferencial; la segmentación principal del análisis es territorial y socioeconómica.

## 15. ¿Cuál es la principal entidad, sector o temática sobre la cual se enfoca el análisis?
El análisis se enfoca principalmente en la temática de ambiente, clima urbano y salud territorial, con un componente de planificación urbana y equidad socioespacial. En términos institucional, se relaciona con la gestión ambiental, la salud pública, la planeación territorial y la política de arborización urbana en Bogotá D.C.

## 16. ¿El análisis incorpora variables o enfoques relacionados con género, inclusión o poblaciones diferenciales?
En evaluación.

El análisis territorial incorpora una dimensión de vulnerabilidad socioeconómica como proxy de condiciones de desventaja, pero no se incluye una segmentación explícita por género, etnia, discapacidad o población diferencial en la modelación. No obstante, la lectura del problema reconoce que los impactos del calor y la contaminación pueden afectar desproporcionadamente a grupos con menor capacidad adaptativa o condiciones de riesgo mayores. En ese sentido, el enfoque se aproxima a la inclusión y la justicia climática, pero sin desarrollar un análisis específico por grupo poblacional.

## 17. Herramientas a utilizar
- Python
- QGIS
- Excel
- GeoPandas
- Pandas
- NumPy
- Plotly
- Streamlit

## 18. Tipo de análisis que esperan realizar
- Análisis exploratorio
- Construcción de indicadores
- Modelos estadísticos
- Visualización de datos
- Análisis geoespacial

## 19. Descripción de la herramienta desarrollada
La herramienta desarrollada consiste en un dashboard interactivo de Bogotá D.C. por UPL, orientado a visualizar y comparar indicadores ambientales, socioeconómicos y territoriales entre 2023 y 2024. La aplicación permite seleccionar el año, elegir la variable a visualizar, observar el mapa por UPL y consultar información de cada unidad territorial mediante hover. También presenta indicadores clave, correlación entre variables, tabla de datos por UPL y el modelo descriptivo de densidad de arbolado. La herramienta está diseñada para facilitar la lectura territorial del problema y permitir identificar zonas con mayor presión ambiental, mayor vulnerabilidad y menor cobertura arbórea.

## 20. Hallazgos y conclusiones
Los hallazgos preliminares sugieren que las UPL con mayor vulnerabilidad socioeconómica y mayor exposición a PM2.5 tienden a presentar menor densidad de arbolado urbano. La relación con la temperatura y la densidad poblacional también aporta información territorial relevante, aunque con fuerza explicativa menor en el modelo. La asociación observada es descriptiva y exploratoria, por lo que no se puede afirmar causalidad, pero sí permite priorizar zonas donde convergen condiciones de riesgo ambiental, presión demográfica y menor cobertura vegetal. La principal conclusión del ejercicio es que la relación entre vulnerabilidad, contaminación, calor y arbolado urbano no es homogénea en la ciudad y requiere una lectura territorial más detallada para orientar políticas públicas de adaptación climática y arborización.

## 21. Impacto y utilidad de la solución desarrollada para la toma de decisiones
1. La solución permite comprender mejor cómo se distribuyen espacialmente los riesgos ambientales y la vulnerabilidad socioeconómica en Bogotá, así como cómo estas condiciones pueden combinarse con la cobertura arbórea urbana. Esto facilita la identificación de zonas prioritarias para intervención.

2. La herramienta puede apoyar la toma de decisiones en temas de planificación urbana, gestión ambiental, políticas de arborización, diseño de intervenciones para reducir el calor urbano y priorización de acciones de adaptación climática. También puede servir como insumo para dialogar con entidades distritales y fortalecer la evidencia para la formulación de estrategias territoriales.

## 22. Descripción de la experiencia con el Portal de Datos Abiertos de Bogotá
La experiencia con el Portal de Datos Abiertos de Bogotá fue útil, aunque con algunas limitaciones. Se conocía parcialmente el portal antes del DataJam, pero no se había usado de manera intensiva. En general, se considera que la plataforma tiene una buena oferta de datos y potencial para análisis territorial, pero la búsqueda de algunos conjuntos requiere mayor claridad en la estructura de metadatos y en la identificación de capas y variables relevantes. Las principales dificultades estuvieron relacionadas con la localización de datasets geoespaciales, la homogeneización de nombres y la validación de la calidad de los archivos. Entre los aspectos que facilitaron el trabajo destacan la disponibilidad de datos públicos, la posibilidad de acceder a geometrías y variables clave y la existencia de información institucional útil para el análisis.

## 23. ¿Cuál ha sido el principal reto técnico o metodológico hasta el momento?
El principal reto ha sido la integración y validación de fuentes con distintos formatos, escalas y niveles de desagregación. En particular, combinar geometrías territoriales, capas ambientales, datos de población y variables de estratificación requiere una limpieza rigurosa, una estandarización de identificadores y una mirada crítica sobre la calidad de los datos. Además, el análisis descriptivo y el modelo estadístico requieren interpretar las asociaciones territoriales con cuidado, evitando extrapolar conclusiones causales sin evidencia adicional.

## 24. ¿Qué consideran que les hace falta para desarrollar mejor su análisis?
- Mayor disponibilidad de datos de salud, movilidad o calidad de vida por zonas más detalladas.
- Mejor documentación metodológica de algunas capas ambientales y de arbolado.
- Más tiempo para validación espacial y revisión de outliers.
- Acceso a indicadores socioeconómicos más específicos por población vulnerable.
- Mayor apoyo en herramientas de geoprocesamiento y visualización avanzada.

## 25. Comentarios adicionales sobre el DataJam o el uso de datos abiertos
El DataJam resultó una experiencia valiosa para integrar fuentes públicas y trabajar con datos abiertos de forma aplicada a un problema territorial relevante. La combinación de análisis espacial, modelación descriptiva y visualización permitió avanzar de manera concreta en la formulación de una pregunta analítica con potencial de uso para la toma de decisiones. La experiencia también evidenció la importancia de contar con documentación clara y metadatos más estructurados para facilitar la reutilización de datos abiertos en proyectos de análisis urbano y ambiental.
