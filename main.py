import csv
import subprocess
import sys
from pathlib import Path

from streamlit.runtime import exists as streamlit_runtime_exists


def _has_required_columns(csv_path: Path, required_columns: set[str]) -> bool:
    if not csv_path.exists() or csv_path.stat().st_size == 0:
        return False
    with csv_path.open("r", encoding="utf-8", newline="") as fh:
        reader = csv.reader(fh)
        header = next(reader, None)
    if not header:
        return False
    return required_columns.issubset(set(header))


def processed_outputs_ready(root: Path) -> bool:
    processed = root / "data" / "processed"
    df_final_path = processed / "df_final.csv"
    model_path = processed / "modelo_arbolado.csv"

    expected_df_columns = {
        "upl",
        "anio",
        "temperatura_media_c",
        "densidad_arbolado_media",
        "poblacion",
        "densidad_poblacional",
        "pm25_media",
        "estrato_medio",
        "proporcion_estrato_1_2",
        "vulnerabilidad_socioeconomica",
    }
    expected_model_columns = {"termino", "coeficiente_estandarizado", "r2", "n"}

    return _has_required_columns(df_final_path, expected_df_columns) and _has_required_columns(
        model_path, expected_model_columns
    )


def ensure_processed_data(root: Path) -> None:
    if processed_outputs_ready(root):
        return

    analysis_script = root / "src" / "analisis_bogota.py"
    subprocess.run([sys.executable, str(analysis_script)], cwd=root, check=True)


def main() -> None:
    root = Path(__file__).resolve().parent
    ensure_processed_data(root)

    if not streamlit_runtime_exists():
        subprocess.run(
            [sys.executable, "-m", "streamlit", "run", str(root / "dashboard_interactivo.py")],
            cwd=root,
            check=True,
        )
        return

    from dashboard_interactivo import main as dashboard_main

    dashboard_main()


if __name__ == "__main__":
    main()
