# DataJam_4 — Diagnóstico espacial de calor, población y calidad del aire en Bogotá D.C.

## Objetivo del análisis
Este proyecto construye un análisis reproducible para estudiar la relación espacial entre exposición al calor urbano, población y contaminación atmosférica en Bogotá D.C., con la Unidad de Planeamiento Local (UPL) como unidad territorial de referencia. La lectura se mantiene descriptiva y territorial: se prioriza la identificación de patrones, asociaciones y hotspots, sin afirmar causalidad.

La pregunta guía es: ¿qué UPL exhiben mayor exposición combinada a calor y contaminación y cómo se relacionan con la presión demográfica y la estructura urbana?

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
   - Fuente: servicio geoespacial institucional
   - Formato: raster
   - Observación: la capa disponible en este entorno no fue legible ni georreferenciable de forma confiable, por lo que se registró como dato faltante y no se inventó información.

## Metodología
- Se definió la UPL como unidad base del análisis.
- Se estandarizaron identificadores territoriales para coincidir entre geometría y tablas tabulares.
- La población se agrego por UPL y año.
- PM2.5 y temperatura se agregaron a UPL mediante promedios ponderados por área de intersección, evitando aproximaciones por centroides.
- Se validaron los años 2023 y 2024.
- Se construyó la tabla final por UPL y año en data/processed/df_final.csv.
- La densidad de arbolado se documentó como variable no disponible en la fuente efectiva utilizada, sin ocultar la limitación.

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

### 4. Procesar la base final
```bash
python src/analisis_bogota.py
```

### 5. Lanzar la aplicación principal
Este repositorio tiene como entrada principal el archivo [main.py](main.py), que inicia el dashboard interactivo de Bogotá por UPL:
```bash
python main.py
```

### 6. Ejecutar el dashboard directamente (alternativa)
```bash
streamlit run dashboard_interactivo.py
```

## Outputs principales
- Tabla analítica final: data/processed/df_final.csv
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
- interpretación metodológica explícita.

## Nota metodológica
La medición de densidad de arbolado se mantiene como variable no validada en esta entrega porque la capa raster oficial disponible en el entorno no podía ser leída correctamente. Por ello, la visualización no fabrica valores para esa dimensión; se documenta la ausencia y se asume el límite metodológico de manera transparente.
