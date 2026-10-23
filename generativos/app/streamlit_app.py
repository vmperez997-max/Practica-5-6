"""Inference only: never train or download data during a visit."""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
from tensorflow import keras

ROOT = Path(__file__).resolve().parents[1]
st.title("LAB10 · Muestreo del VAE")
st.caption(
    "Fashion-MNIST · Zalando Research · licencia MIT. Modelo académico, no condicionado por clase."
)
st.info(
    "Imágenes sintéticas de 28×28. No garantizan originalidad, privacidad, diversidad ni utilidad comercial. Los ejes latentes no tienen significado semántico garantizado."
)
path = ROOT / "models/decoder.keras"
if not path.exists():
    st.error(
        "Falta models/decoder.keras. Ejecute scripts/train_ae_vae.py antes de iniciar la app."
    )
    st.stop()


@st.cache_resource
def load_decoder(path):
    return keras.models.load_model(path, compile=False)


decoder = load_decoder(str(path))
seed = st.number_input(
    "Semilla de muestreo", min_value=0, max_value=100000, value=2026, step=1
)
z = (
    np.random.default_rng(seed)
    .standard_normal((16, decoder.input_shape[-1]))
    .astype(np.float32)
)
images = decoder(z, training=False).numpy()
fig, axes = plt.subplots(4, 4, figsize=(6, 6))
for ax, image in zip(axes.ravel(), images):
    ax.imshow(image.squeeze(), cmap="gray", vmin=0, vmax=1)
    ax.axis("off")
fig.tight_layout()
st.pyplot(fig)
plt.close(fig)
st.subheader("Explorar un punto latente")
z1 = st.slider("z1", -3.0, 3.0, 0.0, 0.1)
z2 = st.slider("z2", -3.0, 3.0, 0.0, 0.1)
single = decoder(np.array([[z1, z2]], dtype=np.float32), training=False).numpy()[0]
st.image(
    single, clamp=True, width=196, caption=f"Decodificación en ({z1:.1f}, {z2:.1f})"
)
st.caption(
    "Solo inferencia: no se descarga Fashion-MNIST ni se entrena al visitar esta aplicación."
)
