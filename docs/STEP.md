# Fase 1 – Preprocesado (`src/preprocessing.py`)

## Qué hace el pipeline

1. **Genera** [`data/external/countries_mapping.json`](../data/external/countries_mapping.json) a partir de [`data/raw/worldcup_data/teams.csv`](../data/raw/worldcup_data/teams.csv) y aliases manuales en código.
2. **Carga** tres fuentes: `international_results.csv` (martj42), `worldcup_data/matches.csv` (jfjelstul), `fifa-world-cup/WorldCupMatches.csv` (Kaggle, opcional).
3. **Resuelve entidades** a códigos FIFA de 3 letras; registra equipos no mapeados en logs y en `reports/preprocessing_summary.txt`.
4. **Fusiona** por `match_key` (fecha + equipos ordenados) con prioridad **jfjelstul > kaggle > martj42**.
5. **Filtra** partidos con fecha **año >= 2000** (histórico anterior queda fuera del CSV de entrenamiento; en Fase 2 el ELO y los ratios leen `international_results.csv` completo).
6. **Asigna** `team_A` / `team_B` y `result` (0/1/2); en partidos neutrales ordena equipos alfabéticamente para quitar sesgo de “home” en el fixture.
7. **Añade** columnas de features como **`NaN`** (rellenadas en Fase 2): `elo_*`, `fifa_rank_*`, `squad_value_*`, `top5_ratio_*`, `win_ratio_50_*`, `xg_computed_*`. Las columnas `gdp_capita_*` **no** forman parte del esquema (no derivables solo de `data/raw/`).
8. **Espeja** cada fila (intercambia A/B y voltea 0↔2) y escribe [`data/processed/match_dataset.csv`](../data/processed/match_dataset.csv).

## Imputación por confederación (Paso 4 de la guía)

No aplica en Fase 1 porque esas columnas aún no tienen valores. En **Fase 2**, [`src/feature_engineering.py`](../src/feature_engineering.py) usa `load_team_confederation()` de [`src/utils.py`](../src/utils.py) para imputar faltantes con la **mediana por confederación y año**; si no hay datos en el grupo, mediana por confederación y, en último término, valores por defecto documentados en el código.

---

# Fase 2 – Ingeniería de variables (`src/feature_engineering.py`)

Ejecutar **después** de Fase 1. Lee `data/processed/match_dataset.csv` y `data/raw/` (principalmente `international_results.csv` y `worldcup_data/*`), y **sobrescribe** el mismo CSV con columnas numéricas completas.

## Regla transversal (*as-of-date*)

- Para cada fila: `team_A`, `team_B`, `date`.
- Los históricos se unen con `merge_asof` hacia atrás usando **`date` del partido menos 1 día** como clave izquierda, de modo que solo entra información **estrictamente anterior** al día del partido.
- Tras el mirroring, `_A` / `_B` están alineados con `team_A` / `team_B`.

## Columnas: reales vs proxies

| Columna | Tipo | Definición implementada |
|---------|------|-------------------------|
| `elo_A`, `elo_B` | **Real** | ELO estilo World Football sobre `international_results.csv` completo: K según `tournament_type` (Mundial 60, continental 50, clasificatoria 40, amistoso 20, otro 30), ventaja local +100 si no neutral, multiplicador por margen de goles (eloratings.net). Valor guardado: **ELO antes** del partido. |
| `win_ratio_50_A`, `win_ratio_50_B` | **Real** | Victorias / partidos entre los **últimos 50** partidos con fecha **&lt; `date`**. |
| `xg_computed_A`, `xg_computed_B` | **Proxy** | Media de **goles a favor** del equipo en partidos con fecha en **[`date` − 365 días, `date`)**. No es xG de proveedor. |
| `fifa_rank_A`, `fifa_rank_B` | **Proxy** | Posición (1 = mejor) en un ranking **mensual** por `elo_after` acumulado al cierre de mes; no es ranking FIFA oficial. |
| `top5_ratio_A`, `top5_ratio_B` | **Proxy** | En convocatorias de Mundial (`squads.csv` + `players.csv`): fracción de jugadores con **≥2** apariciones en mundiales según `count_tournaments` **o** al menos un año en `list_tournaments` anterior al torneo. Sustituto de “Top 5 ligas” (dato inexistente en raw). |
| `squad_value_A`, `squad_value_B` | **Proxy** | Media de **número de Mundiales previos** por jugador (años en `list_tournaments` &lt; año del torneo), **normalizada al máximo por torneo** en `[0, 1]`. No es valor de mercado Transfermarkt. |

## PIB per cápita

**Fuera del esquema.** Integración futura con WDI u otra fuente económica si el trabajo lo requiere.

## Ejecución

Desde la raíz del repo, con el venv activado:

```powershell
python -m src.preprocessing
python -m src.feature_engineering
```

Requisitos: datos en `data/raw/` y `data/external/countries_mapping.json` (generado en Fase 1).

Salidas adicionales Fase 2: [`reports/feature_engineering_summary.txt`](../reports/feature_engineering_summary.txt) (conteo de NaN antes/después, MD5 del CSV, muestra de equipos sin historia previa, resumen de ELO por confederación).

---

# Fase 3 – Modelado y calibración (`src/model/`)

Ejecutar **después** de Fase 2. Lee [`data/processed/features_dataset.csv`](../data/processed/features_dataset.csv) (columna objetivo `result`: 0=gana A, 1=empate, 2=gana B).

## Split temporal (sin KFold aleatorio)

- **Train:** `year <= 2018` (derivado de `date`), con filas espejadas (`match_id` terminado en `_m`) y `sample_weight` (time decay).
- **Validación:** `2019 <= year <= 2022`, **sin** filas `_m` — calibración isotónica OvR sobre probabilidades del XGB ya entrenado.
- **Test:** `year > 2022`, **sin** filas `_m` — métricas finales **Log-Loss** y **Brier multiclase**.

## Modelo y salidas

- Base: `XGBClassifier` multiclase (`multi:softprob`, `num_class=3`) con los hiperparámetros definidos en [`src/model/train.py`](../src/model/train.py).
- Calibración: `IsotonicCalibratedClassifier` en [`src/model/calibration.py`](../src/model/calibration.py) (isotónica one-vs-rest + renorm; equivalente a calibración isotónica sklearn sobre un conjunto fijo; compatible con scikit-learn 1.8, que ya no admite `cv='prefit'` en `CalibratedClassifierCV`).
- Artefactos: [`models/final_xgboost.pkl`](../models/final_xgboost.pkl), [`reports/training_summary.txt`](../reports/training_summary.txt).

## Ejecución

```powershell
python -m src.model.train
```

Opcional (CSV de features alternativo, p. ej. smoke test):

```powershell
python -m src.model.train --features-path tests/fixtures/features_calib_smoke.csv
```

Regenerar el fixture de ejemplo: `python tests/fixtures/generate_smoke_features.py`.

Requisitos: `xgboost` en el entorno (ver [`requirements.txt`](../requirements.txt)).

---

# Fase 4 – Simulación Monte Carlo (`src/simulation/`)

Ejecutar **después** de Fase 3 (modelo `models/final_xgboost.pkl` y datos en `data/raw/` + `data/processed/`).

## Qué hace

1. **Snapshot as-of** ([`src/simulation/feature_provider.py`](../src/simulation/feature_provider.py)): recalcula ELO, rank proxy, ratios y proxies con la misma lógica que Fase 2 (`merge_asof` con `fecha_partido − 1 día`). Equipos sin historia previa a `sim_date` reciben defaults alineados con la imputación Fase 2 (ELO 1500, rank 100, etc.).
2. **Grupos**: [`data/external/world_cup_2026.json`](../data/external/world_cup_2026.json) — 12 grupos × 4 equipos (códigos FIFA-3), `hosts`, `sim_date`. Slots `TBD_*` se rellenan con el siguiente mejor ELO disponible no asignado. Si el archivo no existe, se usa **mock snake** con los 48 equipos de mayor ELO del snapshot (requiere ≥48 equipos en el histórico).
3. **Anexo C** ([`data/external/annex_c_wc2026.json`](../data/external/annex_c_wc2026.json)): las 495 combinaciones oficiales de los 8 mejores terceros y el mapeo a los cruces 1A–1L vs terceros (tabla Wikipedia / Reglamento FIFA).
4. **Fase de grupos**: 6 partidos por grupo; puntos 3/1/0; desempate puntos → ELO snapshot → `fifa_rank` (menor valor = mejor) → desempate aleatorio reproducible.
5. **Eliminatoria**: sin empates; renormalización \(P'(A)=P(A)/(P(A)+P(B))\) sobre clases gana A / gana B. Bracket R32→R16→CF→SF→Final y **tercer lugar** entre perdedores de semifinales, con emparejamientos fijos FIFA 2026 (R16: 89=W74×W77, …).
6. **Rendimiento**: tensor de probabilidades `48×48×3` precalculado con una sola llamada batch a `predict_proba` antes del bucle Monte Carlo.

## Salidas

- [`reports/monte_carlo_top5.csv`](../reports/monte_carlo_top5.csv) — tabla completa por selección (prob. campeón, final, semifinal + intervalos **Wilson 95%**).
- [`reports/monte_carlo_summary.txt`](../reports/monte_carlo_summary.txt) — parámetros, MD5 del modelo, grupos resueltos, top 10.

## Ejecución

```powershell
python -m src.simulation.monte_carlo --iterations 10000 --groups data/external/world_cup_2026.json
```

Fixture de smoke (48 equipos tomados de `features_dataset.csv`):

```powershell
python tests/fixtures/generate_smoke_groups.py
python -m src.simulation.monte_carlo --iterations 1000 --groups tests/fixtures/world_cup_2026_smoke.json
```

Regenerar Anexo C desde volcado de tabla Wikipedia (solo si falta el JSON):

```powershell
python scripts/parse_annex_c_wiki.py ruta/al/wiki_knockout_stage.txt
```
