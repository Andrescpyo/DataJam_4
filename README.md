# DataJam_4 — Vulnerabilidad, calor, contaminación y arbolado urbano en Bogotá D.C.

## Objetivo del análisis
Este proyecto construye un análisis reproducible para estudiar la relación espacial entre vulnerabilidad socioeconómica, exposición al calor urbano, población, contaminación atmosférica y densidad de arbolado en Bogotá D.C., con la Unidad de Planeamiento Local (UPL) como unidad territorial de referencia. La lectura se mantiene descriptiva y territorial: se prioriza la identificación de patrones y asociaciones, sin afirmar causalidad.

La hipótesis de trabajo es: **las UPL con mayor vulnerabilidad socioeconómica y/o mayor exposición a la contaminación tienen una menor cobertura de arbolado urbano**. La temperatura y la densidad poblacional se incorporan como condiciones ambientales y de presión urbana complementarias.

## Fuentes de datos integradas
Se usaron fuentes públicas oficiales y documentadas, alineadas con la lógica de análisis espacial:

1. UPL — geometría base
   - Entidad: Secretaría Distrital de Planeación
   - Fuente: Datos Abiertos Bogotá
   - Formato: GeoJSON
   - CRS: EPSG:4686 / transformación interna a EPSG:3116 para agregación espacial
   - Identificador clave: CODIGO_UPL

2. Población por UPL
   - Entidad: Secretaría Distrital de Salud
   - Fuente: Datos Abiertos Bogotá
   - Formato: CSV
   - Temporalidad: anual
   - Variable principal: población total por UPL y año

3. PM2.5 promedio anual
   - Entidad: Secretaría Distrital de Ambiente
   - Fuente: Portal de Datos Abiertos y servicios ArcGIS
   - Formato: GeoJSON / REST
   - Variable: conc_pm25

4. Temperatura media superficial
   - Entidad: Secretaría Distrital de Ambiente
   - Fuente: Portal de Datos Abiertos y servicios ArcGIS
   - Formato: GeoJSON / REST
   - Variable: temperatura media anual por zona

5. Densidad de arbolado urbano
   - Entidad: Jardín Botánico de Bogotá
   - Fuente: servicio institucional ArcGIS del Jardín Botánico de Bogotá
   - Formato: servicio de identificación por punto (`identify`) sobre la capa raster institucional
   - Observación: se consultaron valores oficiales del servicio para puntos representativos por UPL y se promediaron para cada unidad territorial; no se inventaron valores.

6. Estratificación socioeconómica por manzanas
   - Entidad: Catastro Distrital
   - Fuente: servicio ArcGIS de estratificación
   - Formato: polígonos de manzana descargados como GeoJSON en data/raw/manzanas_estrato.geojson
   - Variables: ESTRATO, código de manzana

## Metodología
- Se definió la UPL como unidad base del análisis.
- Se estandarizaron identificadores territoriales para coincidir entre geometría y tablas tabulares.
- La población se agrego por UPL y año.
- PM2.5 y temperatura se agregaron a UPL mediante promedios ponderados por área de intersección, evitando aproximaciones por centroides.
- La estratificación se cruzó espacialmente con las UPL. Para cada estrato se sumó el área de intersección de sus manzanas; el estrato medio es la media ponderada por esas áreas y también se calcula la proporción de área en estratos 1–2.
- La vulnerabilidad socioeconómica se usa como proxy descriptivo: `-estrato_medio`, de modo que valores mayores representan menor estrato medio. No equivale a una medición integral de vulnerabilidad.
- La densidad poblacional es población / área de la UPL en km².
- Se validaron los años 2023 y 2024.
- Se construyó la tabla final por UPL y año en data/processed/df_final.csv.
- Se ajustó un modelo OLS estandarizado con densidad de arbolado como respuesta y vulnerabilidad, PM2.5, temperatura y densidad poblacional como predictores. Sus resultados quedan en data/processed/modelo_arbolado.csv.
- La densidad de arbolado se incorporó como variable territorial derivada de consultas reales al servicio oficial del Jardín Botánico, con una validación explícita de la capa y sus limitaciones.

## Reproducibilidad
### 1. Crear entorno
```bash
python -m venv .venv
```

### 2. Activar entorno
PowerShell:
```powershell
.\.venv\Scripts\Activate.ps1
```
Bash/Git Bash:
```bash
source .venv/bin/activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Procesar la base final (opcional)
```bash
python src/analisis_bogota.py
```
Este paso es opcional cuando usas `python main.py`, porque `main.py` verifica si `data/processed/df_final.csv` y `data/processed/modelo_arbolado.csv` ya existen y tienen estructura válida. Si faltan o están incompletos, ejecuta automáticamente el procesamiento antes de abrir la app.

### 5. Lanzar la aplicación principal
Este repositorio tiene como entrada principal el archivo [main.py](main.py), que inicia el dashboard interactivo de Bogotá por UPL:
```bash
python main.py
```

## Outputs principales
- Tabla analítica final: data/processed/df_final.csv
- Resultado del modelo descriptivo: data/processed/modelo_arbolado.csv
- Notebook de análisis: notebooks/analisis_bogota.ipynb
- Documento técnico de integración: docs/nota_tecnica_integracion_datos_publicos.md
- Dashboard final: dashboard_interactivo.py
- Punto de entrada principal: main.py

## Estructura del repositorio
```text
DataJam_4/
├── data/
│   ├── raw/
│   └── processed/
├── docs/
│   ├── formulario_caracterizacion.md
│   └── nota_tecnica_integracion_datos_publicos.md
├── notebooks/
│   └── analisis_bogota.ipynb
├── qgis/
│   ├── Densidad arbolado urbano.qgz
│   └── ...
├── src/
│   ├── analisis_bogota.py
│   ├── fetch_metadata.py
│   ├── funciones.py
│   └── __init__.py
├── dashboard_interactivo.py
├── README.md
├── requirements.txt
├── LICENSE
└── .gitignore
```

## Producto final
El proyecto entrega una base reproducible y una visualización interactiva final basada en UPL con:
- selector por año,
- mapa territorial por UPL,
- hover con valores por bloque territorial,
- tabla comparativa de variables,
- correlación entre temperatura, PM2.5 y población,
- estrato medio, proporción de estratos 1–2 y vulnerabilidad socioeconómica proxy,
- tabla completa con código y nombre de cada UPL,
- interpretación metodológica explícita.

## Cumplimiento de lineamientos analíticos
- Enfoque de ciudad: el problema se formula a escala distrital (Bogotá D.C.) y la UPL se usa como desagregación territorial para diagnóstico comparativo, no como intervención aislada.
- Indicadores medibles y comparables en el tiempo: se emplean variables objetivas para 2023 y 2024 (temperatura media, PM2.5, población, densidad poblacional, estrato medio y proporción de estratos 1–2), manteniendo definiciones consistentes entre periodos.
- Comparabilidad temporal: la estructura final de la tabla analítica preserva el mismo esquema de variables por año para facilitar seguimiento, monitoreo y análisis de tendencias.

## Nota metodológica
La densidad de arbolado se estimó a partir de valores oficiales recuperados por `identify` sobre la capa institucional del Jardín Botánico de Bogotá, usando seis puntos candidatos dentro de cada UPL (centroide, punto representativo y vértices contenidos) y promediando únicamente los valores válidos devueltos por el servicio. La estratificación se resume mediante una media ponderada por el área de intersección entre manzanas y UPL. El modelo obtenido con los datos actuales tiene n=64 y R²=0.131: los coeficientes estandarizados son -0.246 para vulnerabilidad socioeconómica, -0.239 para PM2.5, 0.167 para temperatura y 0.383 para densidad poblacional. Estos resultados apoyan una lectura de asociación débil y exploratoria, no una conclusión causal.
