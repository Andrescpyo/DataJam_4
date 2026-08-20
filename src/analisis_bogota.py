from __future__ import annotations

import warnings
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import rasterio
import requests
from rasterstats import zonal_stats

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


def load_tree_density(year: int, upl: gpd.GeoDataFrame) -> pd.DataFrame:
    raster_path = RAW / f"densidad_{year}.tif"
    if not raster_path.exists():
        return pd.DataFrame({"CODIGO_UPL": upl["CODIGO_UPL"].astype(str), "densidad_arbolado_media": [np.nan] * len(upl)})
    try:
        with rasterio.open(raster_path) as src:
            if src.count < 1:
                raise ValueError("Raster sin bandas")
        stats = zonal_stats(upl.geometry, str(raster_path), stats=["mean"], all_touched=True)
        out = pd.DataFrame(stats)
        out = out.rename(columns={"mean": "densidad_arbolado_media"})
        out["CODIGO_UPL"] = upl["CODIGO_UPL"].astype(str).values
        return out[["CODIGO_UPL", "densidad_arbolado_media"]]
    except Exception as exc:
        warnings.warn(f"No fue posible leer el raster de densidad {year}. Se registrará como NA. Detalle: {exc}")
        return pd.DataFrame({"CODIGO_UPL": upl["CODIGO_UPL"].astype(str), "densidad_arbolado_media": [np.nan] * len(upl)})


def build_final_table() -> pd.DataFrame:
    upl = load_upl()
    pop = load_population()

    results = []
    for year in [2023, 2024]:
        row = {"anio": year}
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
        df_year["anio"] = year
        results.append(df_year)

    df_final = pd.concat(results, ignore_index=True)
    return df_final[["CODIGO_UPL", "anio", "temperatura_media_c", "densidad_arbolado_media", "poblacion", "pm25_media"]].rename(columns={"CODIGO_UPL": "upl"})


def main() -> pd.DataFrame:
    PROCESSED.mkdir(parents=True, exist_ok=True)
    df_final = build_final_table()
    out_path = PROCESSED / "df_final.csv"
    df_final.to_csv(out_path, index=False)
    print(f"Se guardó la tabla final en: {out_path}")
    print(df_final.head().to_string(index=False))
    return df_final


if __name__ == "__main__":
    main()
