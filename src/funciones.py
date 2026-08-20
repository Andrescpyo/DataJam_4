"""
Funciones auxiliares para el proyecto DataJam_4
Incluye utilidades para: descarga de recursos, chequeo/reproyección de CRS,
estadísticas zonales raster→polígono y agregación de puntos a polígonos.
"""

from pathlib import Path

import geopandas as gpd
import pandas as pd
import requests
from rasterstats import zonal_stats


def download_file(url, dest_path, timeout=60):
    """Descarga un archivo desde `url` a `dest_path`.
    Nota: requiere conexión a Internet.
    """
    dest = Path(dest_path)
    dest.parent.mkdir(parents=True, exist_ok=True)
    with requests.get(url, stream=True, timeout=timeout) as r:
        r.raise_for_status()
        with open(dest, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
    return dest


def ensure_crs(gdf, target_crs):
    """Reproyecta `gdf` a `target_crs` si es necesario."""
    if gdf.crs is None:
        raise ValueError("GeoDataFrame sin CRS definido")
    return gdf.to_crs(target_crs)


def zonal_mean_raster(gdf_zonas, raster_path, nodata=None, stats=['mean','median','std']):
    """Calcula estadísticas zonales de un raster sobre `gdf_zonas`.
    Devuelve GeoDataFrame con columnas prefijadas como raster_...
    """
    zs = zonal_stats(gdf_zonas.geometry, raster_path, stats=stats, nodata=nodata, geojson_out=False)
    stat_df = pd.DataFrame(zs)
    stat_df = stat_df.rename(columns={k: f"raster_{k}" for k in stat_df.columns})
    gdf_out = gdf_zonas.reset_index(drop=True).join(stat_df)
    return gdf_out


def aggregate_points_to_polygons(points_gdf, polygons_gdf, value_field, agg_func='mean'):
    """Agrega valores desde `points_gdf` a `polygons_gdf` por unión espacial.
    `agg_func` puede ser 'mean', 'sum', 'median', etc.
    Requiere que ambos GDFs compartan CRS.
    """
    joined = gpd.sjoin(points_gdf[[value_field,'geometry']], polygons_gdf[['geometry']], how='inner', predicate='within')
    agg = joined.groupby('index_right')[value_field].agg(agg_func)
    polygons_gdf = polygons_gdf.reset_index()
    polygons_gdf[value_field + '_' + agg_func] = polygons_gdf.index.map(agg)
    return polygons_gdf
