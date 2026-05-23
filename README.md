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

## Ejecutar módulos

Desde la raíz del proyecto, con el entorno activado:

```powershell
python -m src.data_acquisition
```

Sustituye `data_acquisition` por el nombre del módulo que quieras ejecutar.

## Datos en `data/`

Por defecto, todo el contenido de `data/` está ignorado por Git salvo `.gitkeep`. Sube solo archivos pequeños o de ejemplo; datasets grandes deben vivir fuera del repositorio o descargarse con scripts en `src/data_acquisition.py`.

## Alternativa: Conda

Si usas Miniconda o Anaconda:

```bash
conda env create -f environment.yml
conda activate lab01
```

## Licencia

Ver [LICENSE](LICENSE).
