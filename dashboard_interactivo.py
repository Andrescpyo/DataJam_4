import json
from pathlib import Path

import geopandas as gpd
import pandas as pd
import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parent

VARIABLES = {
    "temperatura_media_c": "Temperatura media (°C)",
    "pm25_media": "PM2.5 (µg/m³)",
    "poblacion": "Población",
    "densidad_arbolado_media": "Densidad de arbolado",
}
COMMON_COLOR_SCALE = "RdYlBu_r"


def normalize_upl_code(value):
    text = str(value).strip().upper()
    if text.startswith("UPL"):
        if len(text) == 3:
            return f"UPL{int(text[3:]):02d}"
        return text
    return f"UPL{int(text):02d}"


@st.cache_data
def load_dashboard_data():
    upl = gpd.read_file(ROOT / "data" / "raw" / "upl_geojson.geojson").to_crs("EPSG:4326")
    df = pd.read_csv(ROOT / "data" / "processed" / "df_final.csv")
    df["upl"] = df["upl"].map(normalize_upl_code)
    df["anio"] = df["anio"].astype(int)

    geo = upl[["CODIGO_UPL", "geometry"]].rename(columns={"CODIGO_UPL": "upl"})
    geo["upl"] = geo["upl"].map(normalize_upl_code)
    map_df = geo.merge(df, on="upl", how="left")
    return map_df


def build_corr_table(df: pd.DataFrame) -> pd.DataFrame:
    cols = [
        "temperatura_media_c",
        "pm25_media",
        "poblacion",
    ]
    corr = df[cols].corr(method="pearson").round(3)
    return corr


st.set_page_config(page_title="Dashboard interactivo Bogotá UPL", page_icon="🗺️", layout="wide")
st.title("Dashboard interactivo — Bogotá D.C. por UPL")
st.caption("Comparación territorial por año, con UPL delimitadas y hover con datos para cada variable.")

map_df = load_dashboard_data()

with st.sidebar:
    st.header("Filtros")
    years = sorted(map_df["anio"].dropna().unique().tolist())
    selected_year = st.radio("Año", years, index=len(years) - 1, horizontal=True)
    selected_var = st.selectbox("Variable a visualizar", list(VARIABLES.keys()), format_func=lambda x: VARIABLES[x])

filtered = map_df[map_df["anio"] == selected_year].copy()
variable_has_values = filtered[selected_var].notna().any()

if not variable_has_values:
    st.info(f"La variable {VARIABLES[selected_var]} no está disponible para este año en la base analítica, por lo que no se puede mapear con la misma lógica. Se mantiene la advertencia metodológica.")
    filtered = filtered.copy()
else:
    filtered = filtered[filtered[selected_var].notna()].copy()

# KPI summary
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
with kpi1:
    st.metric("UPL con valores", int(filtered["upl"].nunique()))
with kpi2:
    st.metric("Promedio variable", f"{filtered[selected_var].mean():.2f}")
with kpi3:
    st.metric("Máximo", f"{filtered[selected_var].max():.2f}")
with kpi4:
    st.metric("Mínimo", f"{filtered[selected_var].min():.2f}")

if not variable_has_values:
    st.stop()

geojson = json.loads(filtered.to_json())
fig = px.choropleth_mapbox(
    filtered,
    geojson=geojson,
    locations="upl",
    featureidkey="properties.upl",
    color=selected_var,
    color_continuous_scale=COMMON_COLOR_SCALE,
    range_color=(filtered[selected_var].min(), filtered[selected_var].max()),
    hover_name="upl",
    hover_data={
        "upl": True,
        "anio": True,
        "temperatura_media_c": True,
        "pm25_media": True,
        "poblacion": True,
        "densidad_arbolado_media": True,
        selected_var: True,
    },
    zoom=10,
    center={"lat": 4.711, "lon": -74.0721},
    mapbox_style="carto-positron",
    title=f"{VARIABLES[selected_var]} por UPL — {selected_year}",
    opacity=0.9,
)

fig.update_layout(margin={"r": 0, "t": 40, "l": 0, "b": 0}, height=700)
fig.update_geos(fitbounds="locations", visible=False)
st.plotly_chart(fig, use_container_width=True)

left_col, right_col = st.columns(2)

with left_col:
    st.subheader("Top UPL por variable")
    top = (
        filtered[["upl", selected_var, "anio"]]
        .sort_values(selected_var, ascending=False)
        .head(10)
        .rename(columns={selected_var: VARIABLES[selected_var], "upl": "UPL", "anio": "Año"})
    )
    st.dataframe(top, use_container_width=True)

with right_col:
    st.subheader("Correlación de variables")
    corr = build_corr_table(filtered)
    st.dataframe(corr, use_container_width=True)

st.subheader("Datos completos por UPL")
show_df = filtered[["upl", "anio", "temperatura_media_c", "pm25_media", "poblacion", "densidad_arbolado_media"]].sort_values("upl").reset_index(drop=True)
st.dataframe(show_df, use_container_width=True)

st.markdown(
    """
    ### Cómo interpretarlo
    - Los colores siguen la misma lógica en todas las variables: rojo = valor alto, azul = valor bajo.
    - Si una UPL aparece roja en temperatura y también roja en PM2.5, es una zona con mayor exposición combinada.
    - Si una UPL es roja en temperatura pero no en población, la cifra sugiere un patrón territorial más que una relación mecánica por densidad poblacional.
    - La visualización permite comparar territorialmente los patrones sin afirmar causalidad.
    """
)

st.markdown(
    """
    ### Conclusión
    El mapa interactivo muestra que las UPL con mayor exposición térmica y ambiental no necesariamente coinciden con las de mayor población, pero sí permiten identificar zonas donde convergen calor, contaminación y presión territorial. La comparación por UPL y año confirma la presencia de hotspots urbanos y permite priorizar áreas para diagnóstico y gestión institucional con una lectura espacial y descriptiva, no causal.
    """
)
