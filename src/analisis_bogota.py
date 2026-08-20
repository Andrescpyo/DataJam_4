from __future__ import annotations

import json
import warnings
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import requests
from shapely.geometry import Point

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"


def ensure_file(url: str, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        return
    response = requests.get(url, timeout=60)
    response.raise_for_status()
    target.write_bytes(response.content)


PROJECTED_CRS = "EPSG:3116"
STRATIFICATION_SERVICE = "https://serviciosgis.catastrobogota.gov.co/arcgis/rest/services/ordenamientoterritorial/estratificacion/MapServer/1/query"


def load_upl() -> gpd.GeoDataFrame:
    path = RAW / "upl_geojson.geojson"
    if not path.exists():
        raise FileNotFoundError(f"No existe la capa oficial de UPL: {path}")
    gdf = gpd.read_file(path)
    gdf = gdf.to_crs(PROJECTED_CRS)
    gdf["CODIGO_UPL"] = gdf["CODIGO_UPL"].astype(str)
    return gdf


def normalize_upl_code(value):
    text = str(value).strip().upper()
    if text.startswith("UPL"):
        if len(text) == 3:
            return f"UPL{int(text[3:]):02d}"
        return text
    return f"UPL{int(text):02d}"


def load_population() -> pd.DataFrame:
    path = RAW / "poblacion_upl_2023_2024.csv"
    if not path.exists():
        url = "https://datosabiertos.bogota.gov.co/dataset/85bf790d-84d1-4eda-bd6f-40af62e71d95/resource/d1743cda-9ff9-4103-87ab-9c038f2f09a3/download/osb_demografia-poblacion-upl.csv"
        ensure_file(url, path)
    df = pd.read_csv(path, sep=';')
    df = df.rename(columns={
        "ANO": "anio",
        "CODIGO_UPL": "CODIGO_UPL",
        "POBLACION": "poblacion",
    })
    df["CODIGO_UPL"] = df["CODIGO_UPL"].map(normalize_upl_code)
    df["anio"] = df["anio"].astype(int)
    pop = df[df["anio"].isin([2023, 2024])].groupby(["anio", "CODIGO_UPL"], as_index=False)["poblacion"].sum()
    return pop


def fetch_stratification_layer() -> gpd.GeoDataFrame:
    features = []
    offset = 0
    page_size = 2000
    while True:
        params = {
            "where": "1=1",
            "outFields": "CODIGO_MANZANA,ESTRATO",
            "returnGeometry": "true",
            "outSR": 3116,
            "resultOffset": offset,
            "resultRecordCount": page_size,
            "f": "json",
        }
        response = requests.get(STRATIFICATION_SERVICE, params=params, timeout=120)
        response.raise_for_status()
        payload = response.json()
        page = payload.get("features", [])
        for feature in page:
            geometry = feature.get("geometry")
            if geometry:
                features.append({
                    "type": "Feature",
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": geometry.get("rings", []),
                    },
                    "properties": feature.get("attributes", {}),
                })
        if len(page) < page_size and not payload.get("exceededTransferLimit"):
            break
        offset += len(page)
        if not page:
            break

    if not features:
        raise ValueError("El servicio oficial de estratificación no devolvió manzanas.")
    return gpd.GeoDataFrame.from_features(features, crs=PROJECTED_CRS)


def load_stratification() -> gpd.GeoDataFrame:
    path = RAW / "manzanas_estrato.geojson"
    if not path.exists():
        gdf = fetch_stratification_layer()
        path.parent.mkdir(parents=True, exist_ok=True)
        gdf.to_file(path, driver="GeoJSON")
    gdf = gpd.read_file(path).to_crs(PROJECTED_CRS)
    gdf["ESTRATO"] = pd.to_numeric(gdf["ESTRATO"], errors="coerce")
    return gdf[gdf["ESTRATO"].between(1, 6)].copy()


def aggregate_stratification(upl: gpd.GeoDataFrame, blocks: gpd.GeoDataFrame) -> pd.DataFrame:
    base = upl[["CODIGO_UPL", "geometry"]].copy().to_crs(PROJECTED_CRS)
    value = blocks[["ESTRATO", "geometry"]].copy().to_crs(PROJECTED_CRS)
    inter = gpd.overlay(base, value, how="intersection")
    if inter.empty:
        return pd.DataFrame({
            "CODIGO_UPL": upl["CODIGO_UPL"],
            "estrato_medio": np.nan,
            "proporcion_estrato_1_2": np.nan,
        })
    inter["area_m2"] = inter.geometry.area
    grouped = inter.groupby(["CODIGO_UPL", "ESTRATO"], as_index=False)["area_m2"].sum()
    totals = grouped.groupby("CODIGO_UPL", as_index=False)["area_m2"].sum().rename(columns={"area_m2": "area_estratificada_m2"})
    grouped = grouped.merge(totals, on="CODIGO_UPL", how="left")
    grouped["proporcion"] = grouped["area_m2"] / grouped["area_estratificada_m2"]
    mean = grouped.assign(weighted=grouped["ESTRATO"] * grouped["proporcion"]).groupby("CODIGO_UPL", as_index=False)["weighted"].sum()
    mean = mean.rename(columns={"weighted": "estrato_medio"})
    low_share = grouped[grouped["ESTRATO"].isin([1, 2])].groupby("CODIGO_UPL", as_index=False)["proporcion"].sum()
    low_share = low_share.rename(columns={"proporcion": "proporcion_estrato_1_2"})
    return base[["CODIGO_UPL"]].drop_duplicates().merge(mean, on="CODIGO_UPL", how="left").merge(low_share, on="CODIGO_UPL", how="left").fillna({"proporcion_estrato_1_2": 0})


def area_weighted_mean(gdf_upl: gpd.GeoDataFrame, gdf_value: gpd.GeoDataFrame, value_col: str) -> pd.DataFrame:
    if gdf_value.empty:
        raise ValueError(f"No hay geometrías para {value_col}")
    base = gdf_upl[["CODIGO_UPL", "geometry"]].copy().to_crs(PROJECTED_CRS)
    value = gdf_value[[value_col, "geometry"]].copy().to_crs(PROJECTED_CRS)
    inter = gpd.overlay(base, value, how="intersection")
    if inter.empty:
        return pd.DataFrame({"CODIGO_UPL": base["CODIGO_UPL"].unique(), value_col: [np.nan] * len(base)})
    inter["area_m2"] = inter.geometry.area
    weighted = inter.groupby("CODIGO_UPL").apply(lambda x: np.average(x[value_col], weights=x["area_m2"]))
    agg = weighted.reset_index(name=value_col)
    agg.columns = ["CODIGO_UPL", value_col]
    return agg


def load_air_quality(year: int, variable: str) -> gpd.GeoDataFrame:
    if variable == "pm25":
        file_name = "pm25_2023_arcgis.geojson" if year == 2023 else "pm25_2024_geojson.geojson"
        url = (
            "https://mapas.ambientebogota.gov.co/server/rest/services/Calidad_aire/PM25_Promedio_Anual_2023/MapServer/0/query?where=1%3D1&outFields=*&f=geojson"
            if year == 2023
            else "https://datosabiertos.bogota.gov.co/dataset/a32d342a-fe03-44a9-b006-b5997a816f70/resource/d6b61b68-9e28-4b9e-91dd-1b4dbdce9e94/download/pm25_promedio_anual_2024.geojson"
        )
    elif variable == "temperatura":
        file_name = "temperatura_2023_arcgis.geojson" if year == 2023 else "temperatura_2024_geojson.geojson"
        url = (
            "https://mapas.ambientebogota.gov.co/server/rest/services/Calidad_aire/Temperatura_Anual_Promedio_2023/MapServer/0/query?where=1%3D1&outFields=*&f=geojson"
            if year == 2023
            else "https://datosabiertos.bogota.gov.co/dataset/3d5a82a0-a9e5-4fc2-a912-5d7645e82302/resource/2a179c25-a32c-47c6-bd22-d819d274fd44/download/temperatura_promedio_2024.geojson"
        )
    else:
        raise ValueError(variable)
    path = RAW / file_name
    if not path.exists():
        ensure_file(url, path)
    gdf = gpd.read_file(path)
    gdf = gdf.to_crs(PROJECTED_CRS)
    return gdf


TREE_DENSITY_SERVICE = "https://geoportal.jbb.gov.co/agc/rest/services/IDECA/densidadarboladourbano/MapServer"
TREE_DENSITY_LAYERS = {2023: 0, 2024: 6}
BOGOTA_EXTENT_4686 = {
    "xmin": -74.37733905006982,
    "ymin": 4.414972488264942,
    "xmax": -73.84263597542511,
    "ymax": 4.864481781624532,
    "spatialReference": {"wkid": 4686},
}


def fetch_tree_density_value(year: int, lon: float, lat: float) -> float | np.nan:
    if year not in TREE_DENSITY_LAYERS:
        raise ValueError(f"Solo se soportan años 2023 y 2024; se recibió {year}.")

    layer_id = TREE_DENSITY_LAYERS[year]
    params = {
        "geometry": json.dumps({"x": float(lon), "y": float(lat), "spatialReference": {"wkid": 4686}}),
        "geometryType": "esriGeometryPoint",
        "sr": 4686,
        "tolerance": 1,
        "mapExtent": json.dumps(BOGOTA_EXTENT_4686),
        "imageDisplay": "600,600,96",
        "layers": "all",
        "returnGeometry": "false",
        "f": "json",
    }

    response = requests.get(f"{TREE_DENSITY_SERVICE}/identify", params=params, timeout=60)
    response.raise_for_status()
    payload = response.json()
    for result in payload.get("results", []):
        if str(result.get("layerId")) == str(layer_id):
            value = result.get("attributes", {}).get("Classify.Pixel Value")
            if value is not None:
                return float(value)
    return np.nan


def get_upl_representative_points(upl_gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    sample_points = []
    for _, row in upl_gdf.iterrows():
        geom = row.geometry
        centroid = geom.centroid
        bounds = geom.bounds
        min_x, min_y, max_x, max_y = bounds
        candidates = [
            centroid,
            Point(min_x, min_y),
            Point(max_x, min_y),
            Point(min_x, max_y),
            Point(max_x, max_y),
            geom.representative_point(),
        ]
        for point in candidates:
            if geom.contains(point) or geom.touches(point) or geom.distance(point) < 1e-6:
                sample_points.append({
                    "CODIGO_UPL": row["CODIGO_UPL"],
                    "geometry": point,
                })
    return gpd.GeoDataFrame(sample_points, geometry="geometry", crs=upl_gdf.crs)


def load_tree_density(year: int, upl: gpd.GeoDataFrame) -> pd.DataFrame:
    def _empty_result() -> pd.DataFrame:
        return pd.DataFrame({"CODIGO_UPL": upl["CODIGO_UPL"].astype(str), "densidad_arbolado_media": [np.nan] * len(upl)})

    if year not in TREE_DENSITY_LAYERS:
        raise ValueError(f"Solo se soportan 2023 y 2024 para densidad de arbolado; se recibió {year}.")

    upl_projected = upl.to_crs(PROJECTED_CRS)
    points_gdf = get_upl_representative_points(upl_projected)
    if points_gdf.empty:
        warnings.warn(f"No se pudieron construir puntos representativos para UPL del año {year}.")
        return _empty_result()

    points_gdf = points_gdf.to_crs("EPSG:4686")
    values = []
    for _, row in points_gdf.iterrows():
        lon, lat = row.geometry.x, row.geometry.y
        value = None
        try:
            value = fetch_tree_density_value(year=year, lon=lon, lat=lat)
        except Exception as exc:
            warnings.warn(f"No se pudo consultar el valor oficial de arbolado para UPL {row['CODIGO_UPL']} ({year}): {exc}")
        if pd.notna(value):
            values.append({
                "CODIGO_UPL": row["CODIGO_UPL"],
                "densidad_arbolado_ha": float(value),
            })

    if not values:
        warnings.warn(f"No se obtuvieron valores oficiales del servicio para densidad de arbolado en {year}.")
        return _empty_result()

    df_values = pd.DataFrame(values)
    agg = df_values.groupby("CODIGO_UPL", as_index=False)["densidad_arbolado_ha"].mean()
    agg = agg.rename(columns={"densidad_arbolado_ha": "densidad_arbolado_media"})
    return agg


def build_final_table() -> pd.DataFrame:
    upl = load_upl()
    pop = load_population()
    blocks = load_stratification()
    stratification = aggregate_stratification(upl, blocks)
    upl_area = upl[["CODIGO_UPL", "geometry"]].copy()
    upl_area["area_upl_km2"] = upl_area.geometry.area / 1_000_000
    upl_area = upl_area[["CODIGO_UPL", "area_upl_km2"]]

    results = []
    for year in [2023, 2024]:
        # PM2.5
        pm = load_air_quality(year=year, variable="pm25")
        if "conc_pm25" not in pm.columns:
            raise KeyError(f"La capa PM2.5 {year} no tiene la columna 'conc_pm25'.")
        pm_agg = area_weighted_mean(upl, pm, "conc_pm25")
        pm_agg = pm_agg.rename(columns={"conc_pm25": "pm25_media"})

        # Temperatura
        temp = load_air_quality(year=year, variable="temperatura")
        temp_col = "temperatur" if "temperatur" in temp.columns else "temperatura"
        temp_agg = area_weighted_mean(upl, temp, temp_col)
        temp_agg = temp_agg.rename(columns={temp_col: "temperatura_media_c"})

        # Población
        pop_year = pop[pop["anio"] == year][["CODIGO_UPL", "poblacion"]]

        # Densidad arbolado
        dens = load_tree_density(year=year, upl=upl)

        df_year = pd.merge(upl[["CODIGO_UPL"]], pm_agg, on="CODIGO_UPL", how="left")
        df_year = pd.merge(df_year, temp_agg, on="CODIGO_UPL", how="left")
        df_year = pd.merge(df_year, pop_year, on="CODIGO_UPL", how="left")
        df_year = pd.merge(df_year, dens, on="CODIGO_UPL", how="left")
        df_year = pd.merge(df_year, stratification, on="CODIGO_UPL", how="left")
        df_year = pd.merge(df_year, upl_area, on="CODIGO_UPL", how="left")
        df_year["densidad_poblacional"] = df_year["poblacion"] / df_year["area_upl_km2"]
        df_year["vulnerabilidad_socioeconomica"] = -df_year["estrato_medio"]
        df_year["anio"] = year
        results.append(df_year)

    df_final = pd.concat(results, ignore_index=True)
    return df_final[["CODIGO_UPL", "anio", "temperatura_media_c", "densidad_arbolado_media", "poblacion", "densidad_poblacional", "pm25_media", "estrato_medio", "proporcion_estrato_1_2", "vulnerabilidad_socioeconomica"]].rename(columns={"CODIGO_UPL": "upl"})


def fit_descriptive_model(df_final: pd.DataFrame) -> pd.DataFrame:
    columns = ["densidad_arbolado_media", "vulnerabilidad_socioeconomica", "pm25_media", "temperatura_media_c", "densidad_poblacional"]
    model_df = df_final[columns].dropna().copy()
    if len(model_df) <= len(columns):
        return pd.DataFrame(columns=["termino", "coeficiente_estandarizado", "r2", "n"])
    response = model_df["densidad_arbolado_media"].to_numpy(dtype=float)
    predictors = model_df[["vulnerabilidad_socioeconomica", "pm25_media", "temperatura_media_c", "densidad_poblacional"]].to_numpy(dtype=float)
    response_z = (response - response.mean()) / response.std(ddof=0)
    predictors_z = (predictors - predictors.mean(axis=0)) / predictors.std(axis=0, ddof=0)
    design = np.column_stack([np.ones(len(predictors_z)), predictors_z])
    coefficients = np.linalg.lstsq(design, response_z, rcond=None)[0]
    fitted = design @ coefficients
    r2 = 1 - np.sum((response_z - fitted) ** 2) / np.sum((response_z - response_z.mean()) ** 2)
    terms = ["intercepto", "vulnerabilidad_socioeconomica", "pm25_media", "temperatura_media_c", "densidad_poblacional"]
    return pd.DataFrame({"termino": terms, "coeficiente_estandarizado": coefficients.round(6), "r2": round(float(r2), 6), "n": len(model_df)})


def main() -> pd.DataFrame:
    PROCESSED.mkdir(parents=True, exist_ok=True)
    df_final = build_final_table()
    out_path = PROCESSED / "df_final.csv"
    df_final.to_csv(out_path, index=False)
    fit_descriptive_model(df_final).to_csv(PROCESSED / "modelo_arbolado.csv", index=False)
    return df_final


if __name__ == "__main__":
    main()
