# Predicción Mundial de Fútbol FIFA 2026 mediante Machine Learning

Proyecto base para análisis exploratorio, prototipado en notebooks y scripts modulares de ML.

## Estructura

```text
├── data/               # Datos pequeños o solo .gitkeep (datasets grandes fuera de git)
├── notebooks/          # EDA (01_*), entrenamiento (02_training), simulación (03_simulation)
├── src/                # Scripts modulares
│   ├── data_acquisition.py
│   ├── preprocessing.py
│   ├── feature_engineering.py
│   ├── model/
│   │   ├── __init__.py
│   │   ├── calibration.py
│   │   └── train.py
│   ├── simulation/
│   │   ├── feature_provider.py
│   │   ├── monte_carlo.py
│   │   └── tournament_rules.py
│   └── utils.py
├── tests/
│   └── fixtures/       # CSV mínimo para smoke test de entrenamiento
├── requirements.txt
├── environment.yml
└── README.md
```

## Requisitos

- Python 3.10 o superior (recomendado 3.11+).
- En Windows, PowerShell.

## Configuración con entorno virtual (venv)

Desde la raíz del repositorio:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Si la ejecución de scripts está restringida, puede ser necesario (solo en tu sesión):

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## Jupyter

Con el entorno activado:

```powershell
python -m ipykernel install --user --name lab01 --display-name "Python (lab01)"
jupyter lab
```

Elige el kernel **Python (lab01)** en tus notebooks.

| Notebook | Contenido |
|----------|-----------|
| `01_eda_initial.ipynb` / `01_eda_visuals.ipynb` | EDA sobre `data/raw` y `features_dataset.csv` |
| `02_training.ipynb` | Paso a paso (XGBoost + isotónica) |
| `03_simulation.ipynb` | Monte Carlo (grupos JSON + modelo) |

Al ejecutar las celdas con gráficos en `01_eda_visuals.ipynb`, `02_training.ipynb` y `03_simulation.ipynb`, las PNG se guardan en `reports/figures/` (subcarpetas `01_eda/`, `02_training/`, `03_simulation/`). Catálogo ordenado: [reports/figures/README.md](reports/figures/README.md).

## Obtención de datos

El módulo `src/data_acquisition.py` descarga y guarda los datasets en `data/raw/`. Con el entorno virtual activado, ejecútalo desde la raíz del proyecto:

```powershell
python -m src.data_acquisition
```

### Qué descarga

| Origen | Destino | Descripción |
|--------|---------|-------------|
| [martj42/international_results](https://github.com/martj42/international_results) | `data/raw/international_results.csv` | Resultados de partidos internacionales (CSV vía URL pública). |
| [jfjelstul/worldcup](https://github.com/jfjelstul/worldcup) (`data-csv/`) | `data/raw/worldcup_data/` | Clon parcial del repositorio (sparse checkout). Si la carpeta ya existe, se omite. |
| Kaggle: [abecklas/fifa-world-cup](https://www.kaggle.com/datasets/abecklas/fifa-world-cup) | `data/raw/fifa-world-cup/` | Copas del Mundo FIFA (requiere cuenta y API de Kaggle). Si la carpeta ya tiene archivos, se omite. |

Las carpetas bajo `data/raw/` se crean automáticamente. Los dos primeros orígenes no requieren credenciales; Kaggle sí.

### Configuración de Kaggle

1. Crea una cuenta en [Kaggle](https://www.kaggle.com/) y, en **Account → API**, genera un token (`kaggle.json`).
2. Coloca el archivo en:
   - **Windows:** `%USERPROFILE%\.kaggle\kaggle.json`
   - **Linux/macOS:** `~/.kaggle/kaggle.json`
3. En Windows, restringe permisos del archivo si la API lo exige (solo tu usuario debe poder leerlo).

Alternativa: variables de entorno `KAGGLE_USERNAME` y `KAGGLE_KEY` (ver [documentación de la API de Kaggle](https://github.com/Kaggle/kaggle-api)).

Si la autenticación falla, el script imprimirá un aviso y continuará; los otros datasets igualmente se descargarán si sus fuentes responden.

## Preprocesado

Con datos ya presentes en `data/raw/`, genera el dataset maestro espejado y el mapeo de países:

```powershell
python -m src.preprocessing
```

Salidas principales: `data/external/countries_mapping.json`, `data/processed/match_dataset.csv` (una fila por partido), `reports/preprocessing_summary.txt`. El dataset espejado para entrenamiento se genera en (Feature engineering): `python -m src.feature_engineering` → `data/processed/features_dataset.csv`.

## Feature engineering

Con `match_dataset.csv` ya generado:

```powershell
python -m src.feature_engineering
```

Actualiza `match_dataset.csv` con métricas A/B (ELO, rank, etc., una fila por partido) y escribe `data/processed/features_dataset.csv` con variables diferenciales, `sample_weight` (time decay), `tournament_weight` y mirroring. Ver `reports/feature_engineering_summary.txt`.

## Modelado y calibración

Con `features_dataset.csv` ya generado (cobertura temporal suficiente para validación 2019–2022):

```powershell
python -m src.model.train
```

Salidas: `models/final_xgboost.pkl`, `reports/training_summary.txt` (Log-Loss y Brier multiclase en test; split temporal estricto; validación/test sin filas espejadas `_m`). Con `02_training.ipynb`, también `reports/figures/02_training/`.

Para comprobar el pipeline sin dataset completo:

```powershell
python tests/fixtures/generate_smoke_features.py
python -m src.model.train --features-path tests/fixtures/features_calib_smoke.csv
```

Para datos procesados (se debe asegurar que los scripts anteriores se completarán satisfactoriamente)

```powershell
python -m src.model.train --features-path data/processed/features_dataset.csv
```

## Simulación Monte Carlo

Con el modelo entrenado y datos en `data/raw/` (idealmente `international_results` completo):

```powershell
python -m src.simulation.monte_carlo --iterations 10000 --groups data/external/world_cup_2026.json
```

Salidas: `reports/monte_carlo_top5.csv`, `reports/monte_carlo_summary.txt`. Los intervalos de confianza al 95% para probabilidades de título/final/semifinal usan la **aproximación binomial de Wilson**. Con `03_simulation.ipynb`, también `reports/figures/03_simulation/`.

- **Grupos editables:** [`data/external/world_cup_2026.json`](data/external/world_cup_2026.json) (`sim_date`, `hosts`, 12 grupos). Slots `TBD_*` se sustituyen por equipos con mejor ELO as-of no repetidos. Si el archivo no existe, se usa un **mock snake** con los 48 equipos de mayor ELO (requiere ≥48 equipos en el histórico previo a `sim_date`).
- **Anexo C:** [`data/external/annex_c_wc2026.json`](data/external/annex_c_wc2026.json) (495 combinaciones oficiales). Opcional: `python scripts/parse_annex_c_wiki.py <tabla_wikipedia.txt>`.
- **Smoke:** `python tests/fixtures/generate_smoke_groups.py` → `tests/fixtures/world_cup_2026_smoke.json`; luego `--groups tests/fixtures/world_cup_2026_smoke.json`.


### Error SSL al conectar con Kaggle

Al descargar desde Kaggle puede aparecer un error similar a:

```text
HTTPSConnectionPool(host='api.kaggle.com', port=443): Max retries exceeded with url: /v1/datasets.DatasetApiService/ListDatasets
(Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1032)')))
```

**Causa habitual:** el antivirus o un proxy corporativo intercepta el tráfico HTTPS hacia `api.kaggle.com` y presenta un certificado propio. Python no confía en esa cadena porque no coincide con los certificados raíz del sistema, y la verificación SSL falla.

**Qué probar:**

1. **Antivirus / firewall:** desactiva temporalmente la inspección HTTPS o SSL scanning para comprobar si el error desaparece; si es así, añade una excepción para `api.kaggle.com` o para el intérprete de Python del venv (`.venv\Scripts\python.exe`).
2. **Proxy corporativo:** configura las variables `HTTP_PROXY` / `HTTPS_PROXY` si tu red lo exige, o instala el certificado raíz de la empresa en el almacén de confianza de Windows.
3. **Certificados del sistema:** en Windows, ejecuta Windows Update y asegúrate de que las raíces de confianza estén actualizadas.
4. **Descarga manual (alternativa):** descarga el dataset [fifa-world-cup](https://www.kaggle.com/datasets/abecklas/fifa-world-cup) desde el navegador, descomprime el ZIP en `data/raw/fifa-world-cup/` y vuelve a ejecutar el script (detectará los archivos y omitirá Kaggle).

No se recomienda desactivar la verificación SSL en código de producción; es preferible corregir certificados o excepciones en el antivirus/proxy.

## Datos en `data/`

Por defecto, todo el contenido de `data/` está ignorado por Git salvo `.gitkeep`. Sube solo archivos pequeños o de ejemplo; datasets grandes deben vivir fuera del repositorio o descargarse con `python -m src.data_acquisition` (ver sección anterior).

## Alternativa: Conda

Si usas Miniconda o Anaconda:

```bash
conda env create -f environment.yml
conda activate lab01
```

## Licencia

Ver [LICENSE](LICENSE).
