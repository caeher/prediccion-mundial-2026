# Estructura de Datos Procesados

Este documento describe la estructura de cada archivo CSV ubicado en el directorio `data/processed`.

## 1. features_dataset.csv

- **Ruta Relativa**: `data/processed/features_dataset.csv`
- **Columnas Disponibles**:
  `match_id`, `date`, `team_A`, `team_B`, `is_neutral`, `tournament_type`, `tournament_weight`, `source`, `elo_A`, `fifa_rank_A`, `squad_value_A`, `top5_ratio_A`, `win_ratio_50_A`, `xg_computed_A`, `elo_B`, `fifa_rank_B`, `squad_value_B`, `top5_ratio_B`, `win_ratio_50_B`, `xg_computed_B`, `diff_elo`, `diff_fifa_rank`, `squad_value_ratio`, `diff_top5_ratio`, `diff_win_ratio`, `diff_xg`, `sample_weight`, `result`

### Registros de Ejemplo

**Ejemplo 1**:
```csv
2000-01-04_EGY_TGO,2000-01-04,EGY,TGO,0,friendly,1,martj42,1702.7232391961468,37.0,0.0,0.0,0.36,1.125,1434.3031467086294,151.0,0.0,0.3181818181818182,0.26,1.0,268.4200924875174,114.0,0.0,-0.3181818181818182,0.09999999999999998,0.125,0.002340445867383314,0
```

**Ejemplo 2**:
```csv
2000-01-07_TGO_TUN,2000-01-07,TUN,TGO,0,friendly,1,martj42,1672.7216955551464,51.0,0.0,0.5,0.54,1.0,1425.8756686621718,151.0,0.0,0.3181818181818182,0.26,0.9,246.84602689297458,100.0,0.0,0.18181818181818182,0.28,0.09999999999999998,0.0023450794366868966,0
```

---

## 2. match_dataset.csv

- **Ruta Relativa**: `data/processed/match_dataset.csv`
- **Columnas Disponibles**:
  `match_id`, `date`, `team_A`, `team_B`, `is_neutral`, `tournament_type`, `source`, `elo_A`, `fifa_rank_A`, `squad_value_A`, `top5_ratio_A`, `win_ratio_50_A`, `xg_computed_A`, `elo_B`, `fifa_rank_B`, `squad_value_B`, `top5_ratio_B`, `win_ratio_50_B`, `xg_computed_B`, `result`

### Registros de Ejemplo

**Ejemplo 1**:
```csv
2000-01-04_EGY_TGO,2000-01-04,EGY,TGO,0,friendly,martj42,1702.7232391961468,37.0,0.0,0.0,0.36,1.125,1434.3031467086294,151.0,0.0,0.3181818181818182,0.26,1.0,0
```

**Ejemplo 2**:
```csv
2000-01-07_TGO_TUN,2000-01-07,TUN,TGO,0,friendly,martj42,1672.7216955551464,51.0,0.0,0.5,0.54,1.0,1425.8756686621718,151.0,0.0,0.3181818181818182,0.26,0.9,0
```
