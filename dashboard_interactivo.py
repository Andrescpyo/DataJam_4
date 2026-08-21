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
    "densidad_poblacional": "Densidad poblacional (hab/km²)",
    "densidad_arbolado_media": "Densidad de arbolado",
    "estrato_medio": "Estrato socioeconómico medio",
    "proporcion_estrato_1_2": "Proporción de estratos 1–2",
}
DISPLAY_LABELS = {
    "upl": "UPL",
    "nombre_upl": "Nombre UPL",
    "anio": "Año",
    "temperatura_media_c": "Temperatura media (°C)",
    "pm25_media": "PM2.5 (µg/m³)",
    "poblacion": "Población",
    "densidad_poblacional": "Densidad poblacional (hab/km²)",
    "densidad_arbolado_media": "Densidad de arbolado",
    "estrato_medio": "Estrato socioeconómico medio",
    "proporcion_estrato_1_2": "Proporción de estratos 1–2",
    "vulnerabilidad_socioeconomica": "Vulnerabilidad socioeconómica",
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

    geo = upl[["CODIGO_UPL", "NOMBRE", "geometry"]].rename(
        columns={"CODIGO_UPL": "upl", "NOMBRE": "nombre_upl"}
    )
    geo["upl"] = geo["upl"].map(normalize_upl_code)
    geo["nombre_upl"] = geo["nombre_upl"].fillna(geo["upl"])
    map_df = geo.merge(df, on="upl", how="left")
    return map_df


def build_corr_table(df: pd.DataFrame) -> pd.DataFrame:
    cols = [
        "densidad_arbolado_media",
        "vulnerabilidad_socioeconomica",
        "estrato_medio",
        "temperatura_media_c",
        "pm25_media",
        "densidad_poblacional",
    ]
    corr = df[cols].corr(method="pearson").round(3)
    return corr


def main() -> None:
    st.set_page_config(page_title="Dashboard interactivo Bogotá UPL", page_icon="🗺️", layout="wide")
    st.title("Dashboard interactivo — Bogotá D.C. por UPL")
    st.caption("Comparación territorial por año, con UPL delimitadas y hover con datos para cada variable.")

    map_df = load_dashboard_data()
    model_path = ROOT / "data" / "processed" / "modelo_arbolado.csv"
    model_results = pd.read_csv(model_path) if model_path.exists() else pd.DataFrame()

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
        hover_name="nombre_upl",
        hover_data={
            "upl": True,
            "nombre_upl": True,
            "anio": True,
            "temperatura_media_c": True,
            "pm25_media": True,
            "poblacion": True,
            "densidad_poblacional": True,
            "densidad_arbolado_media": True,
            "estrato_medio": True,
            "proporcion_estrato_1_2": True,
            selected_var: True,
        },
        labels=DISPLAY_LABELS,
        zoom=10,
        center={"lat": 4.711, "lon": -74.0721},
        mapbox_style="carto-positron",
        title=f"{VARIABLES[selected_var]} por UPL — {selected_year}",
        opacity=0.9,
    )

    label_points = filtered.copy()
    label_points["label_point"] = label_points.geometry.representative_point()
    fig.add_scattermapbox(
        lat=label_points["label_point"].y,
        lon=label_points["label_point"].x,
        text=label_points["nombre_upl"],
        mode="text",
        textfont={"size": 10, "color": "#17324D"},
        hoverinfo="skip",
        showlegend=False,
    )

    fig.update_layout(margin={"r": 0, "t": 40, "l": 0, "b": 0}, height=700)
    fig.update_geos(fitbounds="locations", visible=False)
    st.plotly_chart(fig, use_container_width=True)

    left_col, right_col = st.columns(2)

    with left_col:
        st.subheader("Top UPL por variable")
        top = (
            filtered[["upl", "nombre_upl", selected_var, "anio"]]
            .sort_values(selected_var, ascending=False)
            .head(10)
            .rename(columns={selected_var: VARIABLES[selected_var], "upl": "UPL", "nombre_upl": "Nombre UPL", "anio": "Año"})
        )
        st.dataframe(top, use_container_width=True)

    with right_col:
        st.subheader("Correlación de variables")
        corr = build_corr_table(filtered)
        corr = corr.rename(index=DISPLAY_LABELS, columns=DISPLAY_LABELS)
        st.dataframe(corr, use_container_width=True)

    st.subheader("Datos completos por UPL")
    show_df = filtered[["upl", "nombre_upl", "anio", "temperatura_media_c", "pm25_media", "poblacion", "densidad_poblacional", "densidad_arbolado_media", "estrato_medio", "proporcion_estrato_1_2"]].sort_values("upl").reset_index(drop=True)
    show_df = show_df.rename(columns=DISPLAY_LABELS)
    st.dataframe(show_df, use_container_width=True)

    st.subheader("Modelo descriptivo de densidad de arbolado")
    if not model_results.empty:
        st.dataframe(model_results.rename(columns={"termino": "Término", "coeficiente_estandarizado": "Coeficiente estandarizado", "r2": "R²", "n": "n"}), use_container_width=True)
        st.caption("Modelo OLS estandarizado: densidad de arbolado ~ vulnerabilidad socioeconómica + PM2.5 + temperatura + densidad poblacional. Los coeficientes describen asociación territorial, no causalidad.")

    st.markdown(
        """
        ### Cómo interpretarlo
        - Los colores siguen la misma lógica en todas las variables: rojo = valor alto, azul = valor bajo.
        - Si una UPL aparece roja en temperatura y también roja en PM2.5, es una zona con mayor exposición combinada.
        - Un estrato medio menor y una proporción mayor de estratos 1–2 representan mayor vulnerabilidad socioeconómica en este análisis descriptivo.
        - La densidad poblacional se calcula como población dividida por el área de la UPL en km².
        - La visualización permite comparar territorialmente los patrones sin afirmar causalidad.
        """
    )

    st.markdown(
        """
        ### Conclusión
        El modelo descriptivo estandarizado (n=64; R²=0.131) presenta asociaciones negativas entre densidad de arbolado y vulnerabilidad socioeconómica (coeficiente=-0.246) y PM2.5 (coeficiente=-0.239), mientras que temperatura (0.167) y densidad poblacional (0.383) presentan asociaciones positivas en esta base. Estos resultados son débiles en capacidad explicativa y no prueban causalidad: sirven para priorizar la revisión espacial de UPL donde coinciden exposición ambiental, presión demográfica y menor cobertura arbórea observada.
        """
    )


if __name__ == "__main__":
    main()
