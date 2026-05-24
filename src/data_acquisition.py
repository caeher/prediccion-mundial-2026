from __future__ import annotations

import os
from pathlib import Path

import pandas as pd
import requests
from git import Repo

DATA_DIR = Path("data/raw")
DATA_DIR.mkdir(parents=True, exist_ok=True)

INTERNATIONAL_RESULTS_URL = "https://raw.githubusercontent.com/martj42/international_results/master/results.csv"

WORLDCUP_REPO_URL = "https://github.com/jfjelstul/worldcup"
WORLDCUP_BRANCH = "master"
WORLDCUP_DATA_DIR = "data-csv"


def download_international_results():
    print("Descargando partidos internacionales...")

    df = pd.read_csv(INTERNATIONAL_RESULTS_URL)
    output_path = DATA_DIR / "international_results.csv"
    df.to_csv(output_path, index=False)

    print(f"Dataset guardado en: {output_path}")
    print(f"Total partidos: {len(df)}")

def force_rmtree(path):
    import stat
    import shutil
    path = Path(path)
    if not path.exists():
        return
    for root, dirs, files in os.walk(path, topdown=False):
        for name in files:
            os.chmod(os.path.join(root, name), stat.S_IWRITE)
        for name in dirs:
            os.chmod(os.path.join(root, name), stat.S_IWRITE)
    shutil.rmtree(path)

def download_worldcup_data_csv():
    print("Descargando archivos de data-csv desde el repositorio worldcup...")

    temp_repo_dir = DATA_DIR / "tmp_worldcup_repo"
    data_csv_target = DATA_DIR / "worldcup_data"

    if data_csv_target.exists():
        print(f"La carpeta {data_csv_target} ya existe. Se omitirá la descarga.")
        return

    # Clona solo la carpeta data-csv usando git sparse-checkout
    try:
        # Clonado superficial con sparse checkout para solo data-csv
        if temp_repo_dir.exists():
            force_rmtree(temp_repo_dir)
        Repo.clone_from(WORLDCUP_REPO_URL, temp_repo_dir, branch=WORLDCUP_BRANCH, depth=1, multi_options=["--filter=blob:none"])
        repo = Repo(temp_repo_dir)
        repo.git.sparse_checkout('init', '--cone')
        repo.git.sparse_checkout('set', WORLDCUP_DATA_DIR)
        # Mueve los archivos descargados a la ubicación final
        if (temp_repo_dir / WORLDCUP_DATA_DIR).exists():
            os.rename(temp_repo_dir / WORLDCUP_DATA_DIR, data_csv_target)
        print(f"Archivos .csv guardados en: {data_csv_target}")
    except Exception as e:
        print(f"Error al descargar o procesar worldcup data-csv: {e}")
    finally:
        # Limpieza del repo temporal si existe
        if temp_repo_dir.exists():
            force_rmtree(temp_repo_dir)

def download_kaggle_fifa_world_cup():
    print("Descargando dataset de la FIFA desde Kaggle...")
    target_dir = DATA_DIR / "fifa-world-cup"
    target_dir.mkdir(exist_ok=True)

    # Verificamos si ya existen archivos en la carpeta para evitar descargas redundantes
    if any(target_dir.iterdir()):
        print(f"Los datos de Kaggle ya existen en {target_dir}. Omitiendo descarga.")
        return

    try:
        from kaggle.api.kaggle_api_extended import KaggleApi
        api = KaggleApi()
        api.authenticate()
        api.dataset_download_files('abecklas/fifa-world-cup', path=str(target_dir), unzip=True)
        print(f"Dataset de Kaggle guardado en: {target_dir}")
    except Exception as e:
        print(f"Error al descargar desde Kaggle: Asegúrate de tener configurado kaggle.json o las variables de entorno.")
        print(f"Detalle del error: {e}")

def main() -> None:
    download_international_results()
    download_worldcup_data_csv()
    download_kaggle_fifa_world_cup()

if __name__ == "__main__":
    main()
