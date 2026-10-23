"""Create an executable notebook; execute with nbclient (see README)."""

from pathlib import Path

import nbformat as nbf

root = Path(__file__).resolve().parents[1]
notebook = nbf.v4.new_notebook()
notebook.metadata.kernelspec = {
    "display_name": "Python 3 (proyecto)",
    "language": "python",
    "name": "python3",
}
md, code = nbf.v4.new_markdown_cell, nbf.v4.new_code_cell
notebook.cells = [
    md(
        "# LAB08 + LAB09 · Sistemas recomendadores\nVictor Perez · INF-8239 · UASD\n\nEjecución real sobre MovieLens. No se incorporan filas del dataset al notebook. Los rankings son productos del análisis. Consulte las tarjetas y el informe para interpretar los límites."
    ),
    code(
        "from pathlib import Path\nimport os, sys, subprocess, json\nROOT = Path.cwd()\nif ROOT.name == 'notebooks': ROOT = ROOT.parent\nos.chdir(ROOT)\nprint('Python:', sys.version.split()[0])\nif not (ROOT/'data/raw/ml-latest-small/ratings.csv').exists():\n    subprocess.run([sys.executable,'scripts/download_data.py'],check=True)"
    ),
    md(
        "## Procedencia y auditoría\nSe validan claves, nulos, columnas, rango, incrementos de ratings y timestamps. Las tarjetas describen la licencia y el sesgo de selección."
    ),
    code(
        "from inf8239_u03.data import load_movielens\nfrom inf8239_u03.config import MOVIELENS_DIR\nratings,movies = load_movielens(MOVIELENS_DIR)\nprint(json.dumps(json.loads((ROOT/'reports/download_manifest.json').read_text()),indent=2))\nprint({'usuarios':int(ratings.userId.nunique()),'peliculas':len(movies),'ratings':len(ratings)})"
    ),
    md(
        "## Experimento completo\nMismo corte por usuario; modelos 8 factores/4 épocas y 20/12; semillas 17, 42 y 83; alpha 0.25 y 0.75. Se puntúa todo el catálogo sin películas vistas. El corte por usuario no impide fuga temporal entre usuarios; hay empates de timestamp resueltos por movieId. La selección es exploratoria sobre esta prueba, sin test independiente posterior."
    ),
    code(
        "run = subprocess.run([sys.executable,'scripts/run_experiments.py'],capture_output=True,text=True,encoding='utf-8')\n(ROOT/'reports/experiment_log.txt').write_text(run.stdout+run.stderr,encoding='utf-8')\nassert run.returncode == 0, run.stderr\nprint('Experimentos completos. Registro en reports/experiment_log.txt')\nimport pandas as pd\nsummary = pd.read_csv(ROOT/'reports/pareto.csv')\ndisplay(summary.round(6))"
    ),
    code(
        "from IPython.display import Image, display\ndisplay(Image(filename=str(ROOT/'reports/pareto.png')))\nprint(json.dumps(json.loads((ROOT/'reports/audit.json').read_text()),indent=2))"
    ),
    md(
        "## Popularidad y tres consultas por contenido\nEl Top-10 de LAB08 es descriptivo sobre todos los ratings; la evaluación utiliza exclusivamente entrenamiento. Los empates aparecen al compartir el mismo vector TF-IDF de géneros. Las dimensiones latentes de MF no tienen nombres semánticos garantizados."
    ),
    code(
        "display(pd.read_csv(ROOT/'reports/popular_top10.csv'))\ncontent = pd.read_csv(ROOT/'reports/content_recommendations.csv')\nfor query, table in content.groupby('query',sort=False):\n    print(query)\n    assert query not in set(table.title)\n    display(table.drop(columns='query'))"
    ),
    md(
        "## Tres perfiles\nEl historial pequeño es el menor dentro de MovieLens, no un usuario verdaderamente nuevo. El perfil nuevo (-1) es sintético y usa popularidad no personalizada. Las listas con varias semillas permiten inspeccionar estabilidad."
    ),
    code(
        "profiles = pd.read_csv(ROOT/'reports/profile_recommendations.csv')\nexample = profiles[(profiles.method=='hybrid') & (profiles.factors==20) & (profiles.seed==42) & (profiles.alpha==0.75)]\nfor profile,table in example.groupby('profile',sort=False):\n    print(profile, 'historial:',table.history_size.iloc[0])\n    display(table[['rank','title']])"
    ),
    md(
        "## Verificación\nLas pruebas incluyen exclusión de vistos, fallback, extremos del híbrido, corte temporal, errores de datos y dominancia de Pareto."
    ),
    code(
        "check = subprocess.run([sys.executable,'-m','pytest','-q','-p','no:cacheprovider'],capture_output=True,text=True)\nprint(check.stdout)\nassert check.returncode == 0, check.stderr\n(ROOT/'reports/tests.txt').write_text(check.stdout,encoding='utf-8')"
    ),
    md(
        "## Conclusión y declaración de IA\nLa decisión se obtiene de las métricas ejecutadas y se documenta en `docs/CONCLUSION.md` y el PDF. Una mejora offline no prueba satisfacción; se necesita validación independiente, un corte global estricto y evaluación de diversidad. Codex ayudó a completar código, experimentos, pruebas y redacción; los prompts, correcciones y verificaciones figuran en `docs/AI_USAGE.md`. El estudiante debe revisar y poder explicar esta entrega."
    ),
]
(root / "notebooks").mkdir(exist_ok=True)
nbf.write(notebook, root / "notebooks/LAB08_LAB09.ipynb")

if __name__ == "__main__":
    from nbclient import NotebookClient

    NotebookClient(
        notebook, timeout=600, resources={"metadata": {"path": str(root)}}
    ).execute()
    nbf.write(notebook, root / "notebooks/LAB08_LAB09.ipynb")
    print("Notebook ejecutado sin errores.")
