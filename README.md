# lab01

Proyecto base para análisis exploratorio, prototipado en notebooks y scripts modulares de ML.

## Estructura

```text
├── data/               # Datos pequeños o solo .gitkeep (datasets grandes fuera de git)
├── notebooks/          # EDA y prototipado
├── src/                # Scripts modulares
│   ├── data_acquisition.py
│   ├── preprocessing.py
│   ├── feature_engineering.py
│   ├── train_model.py
│   ├── monte_carlo.py
│   └── utils.py
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

## Obtención de datos

El módulo `src/data_acquisition.py` descarga y guarda los datasets en `data/raw/`. Con el entorno virtual activado, ejecútalo desde la raíz del proyecto:

```powershell
python -m src.data_acquisition
```
ó
```powershell
python src/data_acquisition.py 
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
