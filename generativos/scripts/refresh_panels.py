"""Re-render fixed selected examples using existing trained checkpoints."""

import json

import numpy as np
from tensorflow import keras
from train_ae_vae import grid, infer

from inf8239_lab10.data import ROOT, load_data, normalize

_, _, raw_test, labels = load_data()
x = normalize(raw_test)
ids = np.array(
    json.loads((ROOT / "reports/panel_indices.json").read_text())["test_indices"]
)
ae = keras.models.load_model(ROOT / "models/autoencoder.keras", compile=False)
enc = keras.models.load_model(ROOT / "models/vae_encoder.keras", compile=False)
dec = keras.models.load_model(ROOT / "models/decoder.keras", compile=False)
sources = {
    "Original": x[ids],
    "AE": infer(ae, x[ids]),
    "VAE": infer(dec, enc(x[ids])[0].numpy()),
}
images = []
titles = []
for start in [0, 8]:
    for name, source in sources.items():
        images.extend(source[start : start + 8])
        titles.extend([f"{name} #{i} c{labels[i]}" for i in ids[start : start + 8]])
grid(
    np.asarray(images),
    ROOT / "reports/reconstructions.png",
    "16 ejemplos de prueba: originales, AE y VAE (media)",
    titles,
    8,
)
