"""Train on fit only, select checkpoints on validation, evaluate test once."""

import argparse
import hashlib
import json
import os
import platform
from datetime import UTC, datetime
from time import perf_counter

os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")
os.environ.setdefault("TF_ENABLE_ONEDNN_OPTS", "0")
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.metrics.pairwise import euclidean_distances
from tensorflow import keras

from inf8239_lab10.data import CLASSES, ROOT, load_data, normalize, split_training
from inf8239_lab10.metrics import diversity, reconstruction_metrics
from inf8239_lab10.models import build_models, loss_terms


def batches(x, batch_size=256):
    for i in range(0, len(x), batch_size):
        yield x[i : i + batch_size]


def infer(model, x):
    return np.concatenate([model(b, training=False).numpy() for b in batches(x)])


def fit_model(name, model, encoder, decoder, x_train, x_val, epochs, seed, beta=1.0):
    optimizer = keras.optimizers.Adam(1e-3)
    is_vae = name == "VAE"

    @tf.function
    def train_step(x):
        with tf.GradientTape() as tape:
            if is_vae:
                mean, logvar = encoder(x, training=True)
                z = mean + tf.exp(0.5 * logvar) * tf.random.normal(tf.shape(mean))
                pred = decoder(z, training=True)
                rec, kl = loss_terms(x, pred, mean, logvar)
            else:
                pred = model(x, training=True)
                rec, kl = loss_terms(x, pred)
            total = rec + beta * kl
        grads = tape.gradient(total, model.trainable_weights)
        optimizer.apply_gradients(zip(grads, model.trainable_weights))
        return total, rec, kl

    @tf.function
    def val_step(x, batch_number):
        if is_vae:
            mean, logvar = encoder(x, training=False)
            noise = tf.random.stateless_normal(
                tf.shape(mean),
                seed=tf.stack([tf.constant(seed, dtype=tf.int32), batch_number]),
            )
            pred = decoder(mean + tf.exp(0.5 * logvar) * noise, training=False)
            rec, kl = loss_terms(x, pred, mean, logvar)
        else:
            rec, kl = loss_terms(x, model(x, training=False))
        return rec + beta * kl, rec, kl

    rng = np.random.default_rng(seed)
    history = []
    best = float("inf")
    best_weights = None
    best_epoch = 0
    start = perf_counter()
    for epoch in range(1, epochs + 1):
        train_loss = np.zeros(3)
        for ids in batches(rng.permutation(len(x_train))):
            values = train_step(tf.convert_to_tensor(x_train[ids]))
            train_loss += np.array([float(v) for v in values]) * len(ids) / len(x_train)
        val_loss = np.zeros(3)
        for batch_number, b in enumerate(batches(x_val)):
            values = val_step(
                tf.convert_to_tensor(b), tf.constant(batch_number, dtype=tf.int32)
            )
            val_loss += np.array([float(v) for v in values]) * len(b) / len(x_val)
        row = {
            "model": name,
            "epoch": epoch,
            "loss": train_loss[0],
            "reconstruction_bce_sum": train_loss[1],
            "kl": train_loss[2],
            "val_loss": val_loss[0],
            "val_reconstruction_bce_sum": val_loss[1],
            "val_kl": val_loss[2],
        }
        history.append(row)
        if val_loss[0] < best:
            best = val_loss[0]
            best_weights = model.get_weights()
            best_epoch = epoch
        print(json.dumps(row), flush=True)
    model.set_weights(best_weights)
    return history, perf_counter() - start, best_epoch


def grid(images, path, title, labels=None, columns=4):
    rows = int(np.ceil(len(images) / columns))
    fig, axes = plt.subplots(
        rows, columns, figsize=(columns * 1.5, rows * 1.5), squeeze=False
    )
    for index, ax in enumerate(axes.ravel()):
        ax.axis("off")
        if index < len(images):
            ax.imshow(images[index].squeeze(), cmap="gray", vmin=0, vmax=1)
            if labels is not None:
                ax.set_title(str(labels[index]), fontsize=7)
    fig.suptitle(title, fontsize=12)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def nearest(samples, training):
    flat = training.reshape(len(training), -1)
    ids = []
    dist = []
    for b in batches(samples, 32):
        squared = euclidean_distances(b.reshape(len(b), -1), flat, squared=True) / 784
        where = np.argmin(squared, axis=1)
        ids.extend(where.tolist())
        dist.extend(squared[np.arange(len(b)), where].tolist())
    return np.asarray(ids), np.asarray(dist)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--epochs-ae", type=int, default=6)
    parser.add_argument("--epochs-vae", type=int, default=8)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--latent-dim", type=int, default=2)
    args = parser.parse_args()
    if min(args.epochs_ae, args.epochs_vae) < 1:
        parser.error("epochs must be positive")
    if args.latent_dim != 2:
        parser.error("This experiment fixes latent_dim=2 for direct visual inspection")
    tf.config.threading.set_intra_op_parallelism_threads(4)
    tf.config.threading.set_inter_op_parallelism_threads(2)
    keras.utils.set_random_seed(args.seed)
    tf.config.experimental.enable_op_determinism()
    (ROOT / "reports").mkdir(exist_ok=True)
    (ROOT / "models").mkdir(exist_ok=True)
    raw, labels, raw_test, test_labels = load_data()
    fit_idx, val_idx = split_training(raw, labels, args.seed, args.limit)
    all_x = normalize(raw)
    x_train = all_x[fit_idx]
    x_val = all_x[val_idx]
    x_test = normalize(raw_test)
    reports = ROOT / "reports"
    models_dir = ROOT / "models"
    np.savez(ROOT / "data/split_indices.npz", fit=fit_idx, validation=val_idx)
    split_hash = hashlib.sha256(fit_idx.tobytes() + val_idx.tobytes()).hexdigest()
    ae, ae_encoder, ae_decoder, vae, vae_encoder, vae_decoder = build_models(
        args.latent_dim
    )
    histories = []
    cost = {}
    for name, model, encoder, decoder, epochs in [
        ("AE", ae, ae_encoder, ae_decoder, args.epochs_ae),
        ("VAE", vae, vae_encoder, vae_decoder, args.epochs_vae),
    ]:
        history, seconds, best_epoch = fit_model(
            name, model, encoder, decoder, x_train, x_val, epochs, args.seed
        )
        histories.extend(history)
        cost[name] = {
            "fit_seconds": seconds,
            "best_epoch": best_epoch,
            "epochs": epochs,
            "parameters": model.count_params(),
        }
    pd.DataFrame(histories).to_csv(reports / "history.csv", index=False)
    # Freeze model selection before inspecting the official test split.
    for name, model in [
        ("autoencoder", ae),
        ("ae_encoder", ae_encoder),
        ("ae_decoder", ae_decoder),
        ("vae", vae),
        ("vae_encoder", vae_encoder),
        ("decoder", vae_decoder),
    ]:
        model.save(models_dir / f"{name}.keras")
    model_manifest = {
        p.name: {
            "sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
            "bytes": p.stat().st_size,
        }
        for p in models_dir.glob("*.keras")
    }
    (models_dir / "manifest.json").write_text(
        json.dumps(model_manifest, indent=2), encoding="utf-8"
    )
    predictions = {}
    inference_time = {}
    start = perf_counter()
    predictions["AE"] = infer(ae, x_test)
    inference_time["AE"] = perf_counter() - start
    start = perf_counter()
    means = []
    logvars = []
    for b in batches(x_test):
        m, v = vae_encoder(b, training=False)
        means.append(m.numpy())
        logvars.append(v.numpy())
    means = np.concatenate(means)
    logvars = np.concatenate(logvars)
    predictions["VAE"] = infer(vae_decoder, means)
    inference_time["VAE"] = perf_counter() - start
    # Deterministic mean reconstruction, plus a separate fixed posterior Monte Carlo estimate.
    rng = np.random.default_rng(args.seed + 1)
    posterior_z = means + np.exp(0.5 * logvars) * rng.standard_normal(
        means.shape
    ).astype(np.float32)
    posterior_pred = infer(vae_decoder, posterior_z)
    posterior_metrics = reconstruction_metrics(x_test, posterior_pred)
    kl = float(np.mean(-0.5 * np.sum(1 + logvars - means**2 - np.exp(logvars), axis=1)))
    rows = []
    baseline = np.broadcast_to(x_train.mean(axis=0), x_test.shape)
    rows.append(
        {
            "model": "Mean image",
            "test_n": len(x_test),
            **reconstruction_metrics(x_test, baseline),
            "fit_seconds": None,
            "epochs": 0,
            "parameters": 784,
            "model_bytes": 784 * 4,
        }
    )
    for name in ["AE", "VAE"]:
        filenames = ["autoencoder.keras"] if name == "AE" else ["vae.keras"]
        rows.append(
            {
                "model": name,
                "test_n": len(x_test),
                **reconstruction_metrics(x_test, predictions[name]),
                **cost[name],
                "inference_seconds": inference_time[name],
                "model_bytes": sum(model_manifest[f]["bytes"] for f in filenames),
                "kl_nats": kl if name == "VAE" else 0,
            }
        )
    pd.DataFrame(rows).to_csv(reports / "metrics.csv", index=False)
    panel_ids = np.random.default_rng(2026).choice(len(x_test), 16, replace=False)
    (reports / "panel_indices.json").write_text(
        json.dumps(
            {
                "seed": 2026,
                "test_indices": panel_ids.tolist(),
                "labels": test_labels[panel_ids].tolist(),
                "policy": "uniform without replacement, selected before inspecting output quality",
            },
            indent=2,
        )
    )
    panel = []
    titles = []
    for start in [0, 8]:
        for name, source in [
            ("Original", x_test),
            ("AE", predictions["AE"]),
            ("VAE", predictions["VAE"]),
        ]:
            panel.extend(source[panel_ids[start : start + 8]])
            titles.extend(
                [f"{name} #{i} c{test_labels[i]}" for i in panel_ids[start : start + 8]]
            )
    grid(
        np.asarray(panel),
        reports / "reconstructions.png",
        "16 ejemplos de prueba: originales y reconstrucciones",
        titles,
        8,
    )
    latent_rng = np.random.default_rng(2026)
    z = latent_rng.standard_normal((256, args.latent_dim)).astype(np.float32)
    generated = infer(vae_decoder, z)
    ae_prior = infer(ae_decoder, z)
    grid(
        generated[:16],
        reports / "samples_vae.png",
        "VAE: primeras 16 muestras N(0,I), semilla 2026",
    )
    grid(
        ae_prior[:16],
        reports / "samples_ae.png",
        "AE: mismo prior arbitrario, sin garantía de calibración",
    )
    nearest_idx, nearest_dist = nearest(generated, x_train)
    reference_idx, reference_dist = nearest(x_test[panel_ids], x_train)
    nn_panel = []
    nn_titles = []
    for i in range(16):
        nn_panel.extend([generated[i], x_train[nearest_idx[i]]])
        nn_titles.extend(
            [
                f"Sintética {i}",
                f"NN fit #{fit_idx[nearest_idx[i]]} / {nearest_dist[i]:.4f}",
            ]
        )
    grid(
        np.asarray(nn_panel),
        reports / "nearest_neighbors.png",
        f"Muestra VAE y vecino más cercano de los {len(x_train):,} ejemplos de fit",
        nn_titles,
        8,
    )
    pd.DataFrame(
        {
            "sample_id": np.arange(256),
            "fit_original_index": fit_idx[nearest_idx],
            "pixel_mse": nearest_dist,
            "nearest_class": labels[fit_idx[nearest_idx]],
        }
    ).to_csv(reports / "nearest_neighbors.csv", index=False)
    # Prior endpoints and encoded endpoints are fixed by seed, never chosen for aesthetics.
    t = np.linspace(0, 1, 10, dtype=np.float32)[:, None]
    prior_path = (1 - t) * z[0] + t * z[1]
    ae_end = infer(ae_encoder, x_test[panel_ids[:2]])
    ae_path = (1 - t) * ae_end[0] + t * ae_end[1]
    grid(
        np.concatenate([infer(ae_decoder, ae_path), infer(vae_decoder, prior_path)]),
        reports / "interpolation.png",
        "Arriba: AE entre entradas fijas. Abajo: VAE entre puntos del prior.",
        columns=10,
    )
    coordinates = np.linspace(-2, 2, 12, dtype=np.float32)
    latent_grid = np.array(
        [[a, b] for b in coordinates[::-1] for a in coordinates], dtype=np.float32
    )
    grid(
        infer(vae_decoder, latent_grid),
        reports / "latent_grid.png",
        "VAE: cuadrícula latente [-2,2] x [-2,2]",
        columns=12,
    )
    subset = np.random.default_rng(2026).choice(len(x_test), 2000, replace=False)
    ae_z = infer(ae_encoder, x_test[subset])
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    for ax, latent, name in [
        (axes[0], ae_z, "AE"),
        (axes[1], means[subset], "VAE (media)"),
    ]:
        scatter = ax.scatter(
            latent[:, 0],
            latent[:, 1],
            c=test_labels[subset],
            s=3,
            cmap="tab10",
            vmin=-0.5,
            vmax=9.5,
        )
        ax.set(title=name, xlabel="z1", ylabel="z2")
    fig.colorbar(
        scatter,
        ax=axes.ravel().tolist(),
        ticks=range(10),
        label="Etiqueta (solo visualización)",
    )
    fig.savefig(reports / "latent_space.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    fig, axes = plt.subplots(1, 3, figsize=(12, 3.5))
    history = pd.DataFrame(histories)
    for name, group in history.groupby("model"):
        axes[0].plot(group.epoch, group.reconstruction_bce_sum, label=f"{name} fit")
        axes[0].plot(
            group.epoch, group.val_reconstruction_bce_sum, "--", label=f"{name} val"
        )
    v = history[history.model.eq("VAE")]
    axes[1].plot(v.epoch, v.kl, label="fit")
    axes[1].plot(v.epoch, v.val_kl, label="val")
    axes[2].plot(v.epoch, v.loss, label="fit")
    axes[2].plot(v.epoch, v.val_loss, label="val")
    for ax, title in zip(
        axes,
        ["Reconstrucción BCE sumada", "KL del VAE (nats)", "Pérdida VAE = BCE + KL"],
    ):
        ax.set(title=title, xlabel="Época")
        ax.legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(reports / "curves.png", dpi=150)
    plt.close(fig)
    class_errors = []
    for name, pred in predictions.items():
        for label in range(10):
            mask = test_labels == label
            class_errors.append(
                {
                    "model": name,
                    "class_id": label,
                    "class_name": CLASSES[label],
                    **reconstruction_metrics(x_test[mask], pred[mask]),
                }
            )
    pd.DataFrame(class_errors).to_csv(reports / "class_errors.csv", index=False)
    diagnostics = {
        "vae_generated": diversity(generated),
        "ae_arbitrary_prior": diversity(ae_prior),
        "heldout_16": diversity(x_test[panel_ids]),
        "vae_nn_mse_min": float(nearest_dist.min()),
        "vae_nn_mse_mean": float(nearest_dist.mean()),
        "heldout_nn_mse_mean": float(reference_dist.mean()),
        "exact_pixel_copies": int(np.sum(nearest_dist == 0)),
        "nearest_class_counts": {
            CLASSES[i]: int((labels[fit_idx[nearest_idx]] == i).sum())
            for i in range(10)
        },
        "posterior_mc_metrics": posterior_metrics,
        "vae_kl_nats": kl,
        "mean_posterior_variance": np.exp(logvars).mean(axis=0).tolist(),
        "variance_of_posterior_means": means.var(axis=0).tolist(),
        "warning": "Pixel distances and nearest classes are diagnostics, not perceptual quality, semantic diversity or privacy guarantees.",
    }
    (reports / "diagnostics.json").write_text(
        json.dumps(diagnostics, indent=2), encoding="utf-8"
    )
    runtime = {
        "python": platform.python_version(),
        "tensorflow": tf.__version__,
        "keras": keras.__version__,
        "platform": platform.platform(),
        "processor": platform.processor(),
        "devices": [d.name for d in tf.config.list_physical_devices()],
        "fit_n": len(x_train),
        "validation_n": len(x_val),
        "test_n": len(x_test),
        "seed": args.seed,
        "panel_seed": 2026,
        "batch_size": 256,
        "latent_dim": args.latent_dim,
        "beta": 1,
        "learning_rate": 0.001,
        "split_sha256": split_hash,
        "run_utc": datetime.now(UTC).isoformat(),
        "arguments": vars(args),
        "deterministic_ops": True,
        "threads_intra": 4,
        "threads_inter": 2,
    }
    (reports / "runtime.json").write_text(
        json.dumps(runtime, indent=2), encoding="utf-8"
    )
    print(pd.DataFrame(rows).to_string(index=False), flush=True)


if __name__ == "__main__":
    main()
