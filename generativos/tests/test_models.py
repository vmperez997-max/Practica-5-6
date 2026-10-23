import numpy as np
import tensorflow as tf
from tensorflow import keras

from inf8239_lab10.metrics import diversity, reconstruction_metrics
from inf8239_lab10.models import Sampling, build_models, loss_terms


def test_sampling_and_standard_normal_kl():
    mean = tf.zeros((5000, 2))
    logvar = tf.zeros_like(mean)
    z = Sampling()([mean, logvar]).numpy()
    assert z.shape == (5000, 2) and abs(z.mean()) < 0.05
    assert 0.9 < z.var() < 1.1
    _, kl = loss_terms(
        tf.ones((2, 28, 28, 1)) * 0.5, tf.ones((2, 28, 28, 1)) * 0.5, mean, logvar
    )
    assert float(kl) == 0


def test_reparameterization_keeps_encoder_gradients():
    _, _, _, vae, encoder, decoder = build_models()
    x = tf.random.uniform((4, 28, 28, 1))
    with tf.GradientTape() as tape:
        mean, logvar = encoder(x)
        pred = decoder(Sampling()([mean, logvar]))
        rec, kl = loss_terms(x, pred, mean, logvar)
        loss = rec + kl
    grads = tape.gradient(loss, vae.trainable_weights)
    assert all(g is not None and np.isfinite(g.numpy()).all() for g in grads)
    assert any(float(tf.norm(g)) > 0 for g in grads)


def test_model_shapes_ranges_and_saved_reload(tmp_path):
    ae, _, _, vae, _, decoder = build_models()
    x = tf.zeros((2, 28, 28, 1))
    assert ae(x).shape == vae(x).shape == x.shape
    z = np.zeros((2, 2), np.float32)
    predicted = decoder(z).numpy()
    assert 0 <= predicted.min() <= predicted.max() <= 1
    path = tmp_path / "decoder.keras"
    decoder.save(path)
    loaded = keras.models.load_model(path, compile=False)
    np.testing.assert_allclose(predicted, loaded(z).numpy(), atol=1e-6)
    vae_path = tmp_path / "vae.keras"
    vae.save(vae_path)
    assert keras.models.load_model(vae_path, compile=False)(x).shape == x.shape


def test_metrics_and_diversity_detect_identical_samples():
    x = np.zeros((3, 28, 28, 1), np.float32)
    assert diversity(x)["mean_pairwise_mse"] == 0
    assert reconstruction_metrics(x, x)["mse"] == 0
    y = x.copy()
    y[0] = 1
    assert diversity(y)["mean_pairwise_mse"] > 0
