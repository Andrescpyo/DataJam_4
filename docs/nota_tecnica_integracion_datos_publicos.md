# Nota técnica sobre integración de datos públicos

## 1. Objetivo y alcance
La integración de fuentes públicas tuvo como objetivo construir una base analítica homogénea para la comparación territorial entre 2023 y 2024 en Bogotá D.C., usando la Unidad de Planeamiento Local (UPL) como unidad mínima de análisis. La hipótesis es que las UPL con mayor vulnerabilidad socioeconómica y/o mayor exposición a la contaminación presentan menor cobertura de arbolado urbano; temperatura y densidad poblacional se usan como covariables descriptivas. No se asume causalidad.

## 2. Principales fuentes y nivel de disponibilidad
Las capas empleadas provienen de portales institucionales y servicios ArcGIS de entidades distritales. La disponibilidad fue suficiente para construir el análisis, pero la estructura, la temporalidad y el formato de cada recurso no fueron homogéneos. Fueron especialmente relevantes los ajustes de identificador territorial y la normalización del CRS antes de cualquier agregación espacial.

## 3. Desafíos técnicos de integración
La parte más compleja no fue la descarga sino la armonización de unidades y geometrías. La población llegó en formato tabular anual; las capas ambientales llegaron como geometrías vectoriales; la estratificación llegó como polígonos de manzana; y el arbolado se consultó desde un servicio raster. Todas las fuentes se llevaron a EPSG:3116 antes de las operaciones de área y se agregaron a UPL.

## 4. Punto de entrada de la aplicación
La entrega final del proyecto se ejecuta a través de [main.py](../main.py), que lanza el dashboard interactivo y centraliza la ejecución de la visualización. Este archivo funciona como punto de arranque de la presentación analítica, mientras que [dashboard_interactivo.py](../dashboard_interactivo.py) contiene la lógica del mapa y los paneles de análisis.

## 5. Observaciones sobre interoperabilidad
Se observó una diferencia clara entre capas listas para uso directo y capas que requieren procesos especializados de extracción. Algunos recursos estaban disponibles como GeoJSON, otros como endpoints ArcGIS REST, y varios requerían transformaciones de columnas, nombres y CRS. Esto exige una etapa de limpieza y validación previa al análisis que no puede omitirse si se quiere mantener rigor y reproduccionabilidad.

## 6. Tratamiento del caso de densidad de arbolado
La capa de densidad de arbolado se incorporó al flujo analítico mediante consultas oficiales al servicio ArcGIS del Jardín Botánico de Bogotá. Dado que la capa se presenta como servicio institucional y no como una descarga directa legible en este entorno, el proyecto extrae valores reales a partir de puntos representativos dentro de cada UPL y luego promedia los resultados por unidad territorial. Esta estrategia conserva la lógica de análisis espacial y evita inventar valores que no provengan de la fuente oficial.

## 7. Estratificación por UPL
Se descargó la capa oficial `Manzanas de estrato` del servicio de Catastro Distrital mediante consultas paginadas, conservando `CODIGO_MANZANA` y `ESTRATO` en `data/raw/manzanas_estrato.geojson`. Se excluyeron registros sin estrato válido o fuera del rango 1–6. Cada manzana se intersectó con la geometría de UPL; para cada UPL y estrato se sumó el área resultante. El estrato medio se calculó como:

$$
\bar{E}_{UPL} = \frac{\sum_s s \cdot A_{UPL,s}}{\sum_s A_{UPL,s}}
$$

donde $A_{UPL,s}$ es el área de manzanas del estrato $s$ dentro de la UPL. También se calculó la proporción de área correspondiente a estratos 1–2. La vulnerabilidad socioeconómica usada en el modelo es el proxy $-\bar{E}_{UPL}$; no representa por sí sola la vulnerabilidad multidimensional.

## 8. Modelo matemático descriptivo
La respuesta fue la densidad media de arbolado y los predictores fueron vulnerabilidad socioeconómica proxy, PM2.5, temperatura media y densidad poblacional. Todas las variables se estandarizaron y se estimó por mínimos cuadrados ordinarios:

$$
z(\text{arbolado}) = \beta_0 + \beta_1z(\text{vulnerabilidad}) + \beta_2z(\text{PM2.5}) + \beta_3z(\text{temperatura}) + \beta_4z(\text{densidad poblacional}) + \varepsilon
$$

Con los datos actuales: $n=64$, $R^2=0.131$, $\beta_1=-0.246$, $\beta_2=-0.239$, $\beta_3=0.167$ y $\beta_4=0.383$. La asociación negativa observada para vulnerabilidad y PM2.5 es compatible con la hipótesis exploratoria, pero el bajo $R^2$, la escala agregada a UPL y la ausencia de inferencia causal obligan a interpretarla como señal territorial para revisión, no como evidencia de efecto.

## 9. Recomendaciones para fortalecer la integración institucional
- Estandarizar los identificadores espaciales entre entidades.
- Publicar capas en formatos interoperables y fáciles de consumir (GeoJSON, GeoPackage, CSV con metadatos claros).
- Documentar mejor CRS, temporalidad y unidades de medida.
- Facilitar exportaciones raster y vectoriales legibles para análisis geoespaciales abiertos.
- Mantener un protocolo de integración territorial para UPL, barrio o localización geográfica.

## 10. Conclusión
La integración de datos públicos de Bogotá permitió construir un análisis territorial útil y reproducible, siempre que se realicen validaciones explícitas, limpieza de identificadores y manejo transparente de faltantes. El resultado final es un diagnóstico descriptivo por UPL con una visualización interactiva que prioriza la calidad del dato y la claridad metodológica sobre la presentación superficial.
