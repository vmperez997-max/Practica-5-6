"""Una corrida; run_experiments.py genera la comparación completa."""

import argparse
import json
import pickle
from time import perf_counter

import numpy as np

from inf8239_u03.config import MOVIELENS_DIR, ROOT
from inf8239_u03.data import load_movielens
from inf8239_u03.evaluation import RankingEngine, evaluate
from inf8239_u03.recommenders import MatrixFactorization, temporal_leave_one_out

parser = argparse.ArgumentParser()
parser.add_argument("--factors", type=int, default=20)
parser.add_argument("--epochs", type=int, default=12)
parser.add_argument("--alpha", type=float, default=0.75)
parser.add_argument("--seed", type=int, default=42)
args = parser.parse_args()
if not 0 <= args.alpha <= 1 or args.factors < 1 or args.epochs < 1:
    parser.error("alpha en [0,1]; factores y épocas positivos")
ratings, movies = load_movielens(MOVIELENS_DIR)
train, test = temporal_leave_one_out(ratings)
start = perf_counter()
model = MatrixFactorization(factors=args.factors, seed=args.seed).fit(
    train, epochs=args.epochs
)
fit_seconds = perf_counter() - start
engine = RankingEngine(train, movies, model)
start = perf_counter()
recs = {int(u): engine.recommend(int(u), "hybrid", args.alpha) for u in test.userId}
ranking_seconds = perf_counter() - start
predictions = [
    model.predict(r.userId, r.movieId)
    if r.movieId in model.item_index
    else model.global_mean
    for r in test.itertuples()
]
metrics = dict(
    **vars(args),
    **evaluate(recs, test, len(movies)),
    fit_seconds=fit_seconds,
    ranking_seconds=ranking_seconds,
    model_bytes=len(pickle.dumps(model)),
    rmse=float(np.sqrt(np.mean((test.rating - np.asarray(predictions)) ** 2))),
    cold_start_policy="popularidad suavizada; no personalizada",
)
(ROOT / "reports").mkdir(exist_ok=True)
name = f"run_f{args.factors}_e{args.epochs}_s{args.seed}_a{args.alpha}.json"
(ROOT / "reports" / name).write_text(json.dumps(metrics, indent=2), encoding="utf-8")
print(json.dumps(metrics, indent=2))
