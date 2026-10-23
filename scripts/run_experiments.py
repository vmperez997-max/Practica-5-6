"""Rebuild LAB08/LAB09 evidence; no MovieLens rows are exported."""

import hashlib
import json
import pickle
import platform
from datetime import UTC, datetime
from time import perf_counter

import numpy as np
import pandas as pd
from plot_results import plot_results

from inf8239_u03.config import MOVIELENS_DIR, ROOT
from inf8239_u03.data import load_movielens
from inf8239_u03.evaluation import RankingEngine, evaluate, pareto_mask
from inf8239_u03.recommenders import (
    ContentRecommender,
    MatrixFactorization,
    temporal_leave_one_out,
    weighted_popularity,
)


def main():
    reports = ROOT / "reports"
    reports.mkdir(exist_ok=True)
    ratings, movies = load_movielens(MOVIELENS_DIR)
    train, test = temporal_leave_one_out(ratings)
    audit = {
        "users": int(ratings.userId.nunique()),
        "movies": len(movies),
        "rated_movies": int(ratings.movieId.nunique()),
        "ratings": len(ratings),
        "density": len(ratings) / (ratings.userId.nunique() * len(movies)),
        "min_utc": str(pd.to_datetime(ratings.timestamp.min(), unit="s", utc=True)),
        "max_utc": str(pd.to_datetime(ratings.timestamp.max(), unit="s", utc=True)),
        "rating_distribution": {
            str(k): int(v)
            for k, v in ratings.rating.value_counts().sort_index().items()
        },
        "train_rows": len(train),
        "test_rows": len(test),
        "unseen_test_items": int((~test.movieId.isin(train.movieId)).sum()),
        "timestamp_ties_at_boundary": int(
            sum(
                test.set_index("userId").timestamp
                == train.groupby("userId").timestamp.max()
            )
        ),
        "file_sha256": {
            p.name: hashlib.sha256(p.read_bytes()).hexdigest()
            for p in MOVIELENS_DIR.glob("*.csv")
        },
        "run_utc": datetime.now(UTC).isoformat(),
        "python": platform.python_version(),
        "platform": platform.platform(),
    }
    (reports / "audit.json").write_text(json.dumps(audit, indent=2), encoding="utf-8")
    weighted_popularity(ratings, movies).head(10).to_csv(reports / "popular_top10.csv")
    content = ContentRecommender().fit(movies)
    queries = [
        "Toy Story (1995)",
        "Shawshank Redemption, The (1994)",
        "Exorcist, The (1973)",
    ]
    pd.concat([content.recommend(q).assign(query=q) for q in queries]).to_csv(
        reports / "content_recommendations.csv", index=False
    )
    rows, profiles = [], []
    engine = RankingEngine(train, movies)
    users = test.userId.astype(int).tolist()
    counts = train.groupby("userId").size()
    profile_users = {
        "amplio": int(counts.idxmax()),
        "pequeno": int(counts.idxmin()),
        "nuevo": -1,
    }
    titles = movies.set_index("movieId").title

    def record(
        engine,
        method,
        factors=0,
        epochs=0,
        seed=0,
        alpha=0,
        fit_seconds=0,
        size=0,
        rmse=None,
    ):
        state = {"ids": engine.ids, "popularity": engine.pop}
        if method in ["content", "hybrid"]:
            state["content"] = engine.content
        if method in ["collaborative", "hybrid"]:
            state["factorization"] = engine.model
        size = len(pickle.dumps(state))
        start = perf_counter()
        recs = {u: engine.recommend(u, method, alpha) for u in users}
        elapsed = perf_counter() - start
        row = dict(
            method=method,
            factors=factors,
            epochs=epochs,
            seed=seed,
            alpha=alpha,
            fit_seconds=fit_seconds,
            ranking_seconds=elapsed,
            total_seconds=fit_seconds + elapsed,
            model_bytes=size,
            rmse=rmse,
            **evaluate(recs, test, len(movies)),
        )
        rows.append(row)
        for label, user in profile_users.items():
            rec = engine.recommend(user, method, alpha)
            assert not set(rec) & set(train.loc[train.userId.eq(user), "movieId"])
            for rank, item in enumerate(rec, 1):
                profiles.append(
                    {
                        "profile": label,
                        "userId": user,
                        "history_size": int(counts.get(user, 0)),
                        "method": method,
                        "factors": factors,
                        "epochs": epochs,
                        "seed": seed,
                        "alpha": alpha,
                        "rank": rank,
                        "movieId": item,
                        "title": titles.loc[item],
                    }
                )
        print(json.dumps(row), flush=True)

    mean_rmse = float(np.sqrt(np.mean((test.rating - train.rating.mean()) ** 2)))
    record(engine, "popularity", rmse=mean_rmse)
    record(engine, "content")
    for factors, epochs in [(8, 4), (20, 12)]:
        for seed in [17, 42, 83]:
            start = perf_counter()
            model = MatrixFactorization(factors=factors, seed=seed).fit(
                train, epochs=epochs
            )
            duration = perf_counter() - start
            predictions = [
                model.predict(r.userId, r.movieId)
                if r.movieId in model.item_index
                else model.global_mean
                for r in test.itertuples()
            ]
            rmse = float(np.sqrt(np.mean((test.rating - np.array(predictions)) ** 2)))
            size = len(pickle.dumps(model))
            engine = RankingEngine(train, movies, model)
            record(
                engine, "collaborative", factors, epochs, seed, 1, duration, size, rmse
            )
            for alpha in [0.25, 0.75]:
                record(
                    engine, "hybrid", factors, epochs, seed, alpha, duration, size, rmse
                )
    result = pd.DataFrame(rows)
    result.to_csv(reports / "metrics.csv", index=False)
    summary = result.groupby(
        ["method", "factors", "epochs", "alpha"], as_index=False
    ).agg(
        runs=("seed", "size"),
        hit_rate_at_10=("hit_rate_at_10", "mean"),
        hr_std=("hit_rate_at_10", "std"),
        precision_at_10=("precision_at_10", "mean"),
        positive_hit_rate_at_10=("positive_hit_rate_at_10", "mean"),
        coverage=("coverage", "mean"),
        rmse=("rmse", "mean"),
        total_seconds=("total_seconds", "mean"),
        model_bytes=("model_bytes", "mean"),
    )
    summary["pareto"] = pareto_mask(summary)
    summary.to_csv(reports / "pareto.csv", index=False)
    pd.DataFrame(profiles).to_csv(reports / "profile_recommendations.csv", index=False)
    plot_results(summary, reports / "pareto.png")


if __name__ == "__main__":
    main()
