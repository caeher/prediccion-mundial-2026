# Figuras generadas desde notebooks

Las imágenes PNG se crean al **ejecutar las celdas con gráficos** en los notebooks (kernel **Python (lab01)**). Convención: `reports/figures/<notebook>/NN_slug_descriptivo.png` (orden `NN` dentro de cada libreta).

| Orden | Ruta relativa | Notebook | Descripción |
|-------|---------------|----------|---------------|
| 1 | `01_eda/01_time_decay_sample_weight.png` | [01_eda_visuals.ipynb](../../notebooks/01_eda_visuals.ipynb) | `sample_weight` vs fecha y curva teórica de decaimiento |
| 2 | `01_eda/02_correlation_heatmap_result.png` | idem | Matriz de correlación (Pearson) variables diferenciales vs `result` |
| 3 | `01_eda/03_tournament_weight_diff_elo_by_result.png` | idem | Distribución `tournament_weight` y `diff_elo` por resultado |
| 4 | `02_training/01_feature_importance_xgb_top10.png` | [02_training.ipynb](../../notebooks/02_training.ipynb) | Importancia del modelo base XGB (top 10 features) |
| 5 | `02_training/02_reliability_diagrams_validation.png` | idem | Diagramas de fiabilidad (validación 2019–2022, calibrado), tres clases |
| 6 | `02_training/03_max_confidence_validation.png` | idem | Histograma de confianza máxima (correcta vs incorrecta) |
| 7 | `03_simulation/01_champion_probability_top15_wilson_ci.png` | [03_simulation.ipynb](../../notebooks/03_simulation.ipynb) | Top 15 probabilidad campeón con IC 95% Wilson |
| 8 | `03_simulation/02_final_probability_top10.png` | idem | Top 10 probabilidad de llegar a la final |

La función `save_notebook_figure` está en [`src/notebook_figures.py`](../../src/notebook_figures.py) y también se reexporta desde [`src/utils.py`](../../src/utils.py) (`dpi` por defecto 150; subir a 300 si necesitas impresión).
