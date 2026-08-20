# Nota técnica sobre integración de datos públicos

## 1. Objetivo y alcance
La integración de fuentes públicas tuvo como objetivo construir una base analítica homogénea para la comparación territorial entre 2023 y 2024 en Bogotá D.C., usando la Unidad de Planeamiento Local (UPL) como unidad mínima de análisis. La lógica principal fue mantener un enfoque transparente, reproducible y descriptivo, con énfasis en variables ambientales y demográficas sin asumir causalidad.

## 2. Principales fuentes y nivel de disponibilidad
Las capas empleadas provienen de portales institucionales y servicios ArcGIS de entidades distritales. La disponibilidad fue suficiente para construir el análisis, pero la estructura, la temporalidad y el formato de cada recurso no fueron homogéneos. Fueron especialmente relevantes los ajustes de identificador territorial y la normalización del CRS antes de cualquier agregación espacial.

## 3. Desafíos técnicos de integración
La parte más compleja no fue la descarga sino la armonización de unidades y geometrías. La población llegó en formato tabular anual; las capas ambientales llegaron como geometrías vectoriales y los datos de arbolado se intentaron incorporar desde una capa raster. El desafío central fue cruzar esas fuentes bajo una misma lógica metodológica y validar que no se estaban combinando elementos que no compartían la misma unidad territorial ni la misma resolución.

## 4. Punto de entrada de la aplicación
La entrega final del proyecto se ejecuta a través de [main.py](../main.py), que lanza el dashboard interactivo y centraliza la ejecución de la visualización. Este archivo funciona como punto de arranque de la presentación analítica, mientras que [dashboard_interactivo.py](../dashboard_interactivo.py) contiene la lógica del mapa y los paneles de análisis.

## 5. Observaciones sobre interoperabilidad
Se observó una diferencia clara entre capas listas para uso directo y capas que requieren procesos especializados de extracción. Algunos recursos estaban disponibles como GeoJSON, otros como endpoints ArcGIS REST, y varios requerían transformaciones de columnas, nombres y CRS. Esto exige una etapa de limpieza y validación previa al análisis que no puede omitirse si se quiere mantener rigor y reproduccionabilidad.

## 6. Tratamiento del caso de densidad de arbolado
La capa de densidad de arbolado se incorporó como variable tentativa dentro del flujo analítico, pero la fuente efectiva disponible en este entorno no pudo leerse de forma confiable ni ser georreferenciada adecuadamente. Por esa razón, la variable se registró como faltante y no se sustituyó por valores inventados. Esto es una decisión metodológica adecuada para evitar resultados espurios en el dashboard y en la interpretación territorial.

## 7. Recomendaciones para fortalecer la integración institucional
- Estandarizar los identificadores espaciales entre entidades.
- Publicar capas en formatos interoperables y fáciles de consumir (GeoJSON, GeoPackage, CSV con metadatos claros).
- Documentar mejor CRS, temporalidad y unidades de medida.
- Facilitar exportaciones raster y vectoriales legibles para análisis geoespaciales abiertos.
- Mantener un protocolo de integración territorial para UPL, barrio o localización geográfica.

## 8. Conclusión
La integración de datos públicos de Bogotá permitió construir un análisis territorial útil y reproducible, siempre que se realicen validaciones explícitas, limpieza de identificadores y manejo transparente de faltantes. El resultado final es un diagnóstico descriptivo por UPL con una visualización interactiva que prioriza la calidad del dato y la claridad metodológica sobre la presentación superficial.
