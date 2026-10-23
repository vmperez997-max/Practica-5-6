"""Comparable dense AE / VAE; registered sampling for safe Keras reload."""

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers


@keras.utils.register_keras_serializable(package="inf8239_lab10")
class Sampling(layers.Layer):
    def call(self, inputs):
        mean, logvar = inputs
        return mean + tf.exp(0.5 * logvar) * tf.random.normal(tf.shape(mean))


def build_models(latent_dim=2):
    if latent_dim < 1:
        raise ValueError("latent_dim must be positive")

    def trunk():
        x = keras.Input(shape=(28, 28, 1))
        h = layers.Flatten()(x)
        h = layers.Dense(256, activation="relu")(h)
        h = layers.Dense(128, activation="relu")(h)
        return x, h

    def decoder(name):
        z = keras.Input(shape=(latent_dim,))
        h = layers.Dense(128, activation="relu")(z)
        h = layers.Dense(256, activation="relu")(h)
        h = layers.Dense(784, activation="sigmoid")(h)
        return keras.Model(z, layers.Reshape((28, 28, 1))(h), name=name)

    x, h = trunk()
    ae_encoder = keras.Model(
        x, layers.Dense(latent_dim, name="ae_latent")(h), name="ae_encoder"
    )
    ae_decoder = decoder("ae_decoder")
    ae = keras.Model(x, ae_decoder(ae_encoder(x)), name="autoencoder")
    x, h = trunk()
    mean = layers.Dense(latent_dim, name="z_mean")(h)
    logvar = layers.Dense(latent_dim, name="z_log_var")(h)
    vae_encoder = keras.Model(x, [mean, logvar], name="vae_encoder")
    vae_decoder = decoder("vae_decoder")
    vae = keras.Model(x, vae_decoder(Sampling()([mean, logvar])), name="vae")
    return ae, ae_encoder, ae_decoder, vae, vae_encoder, vae_decoder


def loss_terms(x, reconstructed, mean=None, logvar=None):
    reconstruction = tf.reduce_mean(
        tf.reduce_sum(
            keras.backend.binary_crossentropy(x, reconstructed), axis=(1, 2, 3)
        )
    )
    kl = (
        tf.constant(0.0, dtype=tf.float32)
        if mean is None
        else -0.5
        * tf.reduce_mean(
            tf.reduce_sum(1 + logvar - tf.square(mean) - tf.exp(logvar), axis=1)
        )
    )
    return reconstruction, kl
