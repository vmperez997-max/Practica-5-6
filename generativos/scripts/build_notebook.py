"""Execute a notebook that verifies checkpoints and recomputes test inference."""

from pathlib import Path

import nbformat as nbf
from nbclient import NotebookClient

root = Path(__file__).resolve().parents[1]
md, code = nbf.v4.new_markdown_cell, nbf.v4.new_code_cell
notebook = nbf.v4.new_notebook()
notebook.metadata.kernelspec = {
    "display_name": "Python 3 LAB10",
    "language": "python",
    "name": "python3",
}
notebook.cells = [
    md(
        "# U03 · LAB10 · Autoencoder y VAE con Fashion-MNIST\nVictor Manuel Perez Padilla · 100801946\n\nEntorno TensorFlow aislado. El notebook carga los modelos entrenados, verifica hashes y vuelve a calcular reconstrucción sobre toda la prueba. El entrenamiento completo está en `scripts/train_ae_vae.py`; active `RETRAIN` para repetirlo, con costo registrado de nuevo. No se fabrican salidas."
    ),
    code(
        "from pathlib import Path\nimport os, sys, json, subprocess, hashlib\nROOT=Path.cwd()\nif ROOT.name=='notebooks':ROOT=ROOT.parent\nos.chdir(ROOT)\nos.environ['TF_ENABLE_ONEDNN_OPTS']='0'\nos.environ['TF_CPP_MIN_LOG_LEVEL']='2'\nRETRAIN=False\nif RETRAIN or not (ROOT/'models/decoder.keras').exists():\n    result=subprocess.run([sys.executable,'scripts/train_ae_vae.py','--epochs-ae','6','--epochs-vae','8'],capture_output=True,text=True,encoding='utf-8')\n    (ROOT/'reports/training_log.txt').write_text(result.stdout+result.stderr,encoding='utf-8')\n    assert result.returncode==0,result.stderr\nprint('Python',sys.version.split()[0])\nprint(json.dumps(json.loads((ROOT/'reports/runtime.json').read_text()),indent=2))"
    ),
    md(
        "## Datos, licencia y partición\nFashion-MNIST oficial: 60,000 entrenamiento y 10,000 prueba. Se separan 50,000 fit y 10,000 validación estratificada, semilla 42. Prueba no decide épocas ni hiperparámetros. Píxeles uint8 se normalizan a [0,1]. Los 16 ejemplos visuales se eligen uniformemente con semilla 2026, sin seleccionar por calidad. Hashes y URLs apuntan a un commit fijo de Zalando Research."
    ),
    code(
        "from inf8239_lab10.data import load_data, normalize, split_training\nraw,labels,raw_test,test_labels=load_data()\nconfig=json.loads((ROOT/'reports/runtime.json').read_text())\nfit_idx,val_idx=split_training(raw,labels,seed=config['seed'],limit=config['arguments']['limit'])\nassert not set(fit_idx)&set(val_idx)\nassert len(fit_idx)==config['fit_n'] and len(val_idx)==10000 and len(raw_test)==10000\nprint(json.dumps(json.loads((ROOT/'reports/download_manifest.json').read_text()),indent=2))\nprint({'fit':len(fit_idx),'val':len(val_idx),'test':len(raw_test)})"
    ),
    md(
        "## Modelos y costos\nAE y VAE densos comparten anchos 256/128, latente de dos dimensiones y decodificador 128/256/784 con sigmoid. AE minimiza BCE sumada; VAE añade KL con beta=1. Adam .001, batch 256, CPU. Se restaura el menor loss de validación dentro de 6 épocas AE y 8 VAE. No se ha entrenado GAN ni un modelo de transferencia; se comparan conceptualmente en la Model Card."
    ),
    code(
        "import pandas as pd\nimport numpy as np\nfrom tensorflow import keras\nfrom inf8239_lab10.models import Sampling\nmanifest=json.loads((ROOT/'models/manifest.json').read_text())\nfor filename,meta in manifest.items():\n    assert hashlib.sha256((ROOT/'models'/filename).read_bytes()).hexdigest()==meta['sha256']\nautoencoder=keras.models.load_model(ROOT/'models/autoencoder.keras',compile=False)\nencoder=keras.models.load_model(ROOT/'models/vae_encoder.keras',compile=False)\ndecoder=keras.models.load_model(ROOT/'models/decoder.keras',compile=False)\ndisplay(pd.read_csv(ROOT/'reports/metrics.csv'))\nprint('Todos los modelos coinciden con sus hashes.')"
    ),
    code(
        "from inf8239_lab10.metrics import reconstruction_metrics\nx_test=normalize(raw_test)\nrecomputed=[]\nfor name in ['AE','VAE']:\n    output=[]\n    for offset in range(0,len(x_test),256):\n        batch=x_test[offset:offset+256]\n        prediction=autoencoder(batch,training=False) if name=='AE' else decoder(encoder(batch,training=False)[0],training=False)\n        output.append(prediction.numpy())\n    scores=reconstruction_metrics(x_test,np.concatenate(output))\n    reference=pd.read_csv(ROOT/'reports/metrics.csv').query('model==@name').iloc[0]\n    assert abs(scores['mse']-reference.mse)<1e-6\n    recomputed.append({'model':name,**scores})\ndisplay(pd.DataFrame(recomputed))"
    ),
    md(
        "## Paneles completos y no seleccionados\nReconstrucción VAE usa la media posterior para evitar ruido de evaluación. También se registra una estimación Monte Carlo posterior en diagnostics.json. Muestras nuevas: primeras 16 de 256 puntos N(0,I), semilla 2026. En AE el mismo prior es arbitrario y no está calibrado."
    ),
    code(
        "from IPython.display import Image,display\nfor filename in ['curves.png','reconstructions.png','samples_vae.png','samples_ae.png','interpolation.png','latent_space.png','latent_grid.png','nearest_neighbors.png']:\n    print(filename)\n    display(Image(filename=str(ROOT/'reports'/filename)))"
    ),
    md(
        "## Fidelidad, diversidad y posible memorización\nSe comparan las 256 muestras con todos los 50,000 ejemplos de fit, mediante vecino más cercano en MSE de píxeles. Un vecino parecido no demuestra copia, y no hallar igualdad no demuestra privacidad. Diversidad numérica y clases de vecinos no son métricas de realismo ni prueban cobertura semántica. Ver errores por clase y conclusión crítica."
    ),
    code(
        "print(json.dumps(json.loads((ROOT/'reports/diagnostics.json').read_text()),indent=2))\ndisplay(pd.read_csv(ROOT/'reports/class_errors.csv'))\ndisplay(pd.read_csv(ROOT/'reports/nearest_neighbors.csv').head(16))"
    ),
    md(
        "## Pruebas y responsabilidad\nCodex apoyó código, depuración, entrenamiento, pruebas e informe. El ZIP docente no estaba accesible: esta es una implementación propia declarada. El estudiante debe revisar y explicar lo entregado. Referencias y prompts: MODEL_CARD.md y AI_USE_DECLARATION.md."
    ),
    code(
        "result=subprocess.run([sys.executable,'-m','pytest','-q','-p','no:cacheprovider'],capture_output=True,text=True)\nprint(result.stdout)\nassert result.returncode==0,result.stderr\n(ROOT/'reports/tests.txt').write_text(result.stdout,encoding='utf-8')"
    ),
]
(root / "notebooks").mkdir(exist_ok=True)
path = root / "notebooks/LAB10_AE_VAE.ipynb"
nbf.write(notebook, path)
NotebookClient(
    notebook, timeout=1200, resources={"metadata": {"path": str(root)}}
).execute()
nbf.write(notebook, path)
print("Notebook ejecutado y verificado.")
