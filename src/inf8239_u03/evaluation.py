"""Full-catalog ranking with train-only signals and explicit cold-start policy."""

from __future__ import annotations

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from .recommenders import ContentRecommender, weighted_popularity


def normalize(values):
    values = np.asarray(values, dtype=float)
    return (values - values.min()) / max(float(np.ptp(values)), 1e-12)


class RankingEngine:
    def __init__(self, train, movies, model=None):
        self.train, self.movies, self.model = (
            train,
            movies.reset_index(drop=True),
            model,
        )
        self.ids = self.movies.movieId.to_numpy()
        self.rows = {int(item): i for i, item in enumerate(self.ids)}
        self.content = ContentRecommender().fit(self.movies)
        popular = weighted_popularity(train, movies)
        self.pop = (
            popular.weighted_score.reindex(self.ids)
            .fillna(train.rating.mean())
            .to_numpy()
        )
        self.groups = {int(u): h for u, h in train.groupby("userId")}

    def recommend(self, user, method="hybrid", alpha=0.75, k=10):
        history = self.groups.get(user)
        seen = set() if history is None else set(history.movieId)
        mask = ~np.isin(self.ids, list(seen))
        candidate = np.flatnonzero(mask)
        if history is None:
            score = self.pop[candidate]
        else:
            weights = np.clip(history.rating.to_numpy() - 2.5, 0.1, None)
            rows = [self.rows[int(i)] for i in history.movieId]
            profile = (
                np.asarray(
                    self.content.matrix[rows].multiply(weights[:, None]).sum(axis=0)
                )
                / weights.sum()
            )
            content = cosine_similarity(profile, self.content.matrix[candidate]).ravel()
            if method == "content":
                score = content
            elif method == "popularity":
                score = self.pop[candidate]
            else:
                cf = np.full(len(self.ids), self.model.global_mean)
                if user in self.model.user_index:
                    predictions = (
                        self.model.global_mean
                        + self.model.item_factors
                        @ self.model.user_factors[self.model.user_index[user]]
                    )
                    cf[[self.rows[int(i)] for i in self.model.items]] = predictions
                cf = cf[candidate]
                score = (
                    cf
                    if method == "collaborative"
                    else alpha * normalize(cf) + (1 - alpha) * normalize(content)
                )
        order = np.lexsort((self.ids[candidate], -score))[:k]
        return self.ids[candidate[order]].astype(int).tolist()


def evaluate(recommendations, truth, catalog_size, k=10):
    hits = [
        int(r.movieId in recommendations[int(r.userId)][:k]) for r in truth.itertuples()
    ]
    positive = truth[truth.rating >= 4]
    positive_hits = [
        int(r.movieId in recommendations[int(r.userId)][:k])
        for r in positive.itertuples()
    ]
    return {
        "hit_rate_at_10": float(np.mean(hits)),
        "precision_at_10": float(np.mean(hits) / k),
        "positive_hit_rate_at_10": float(np.mean(positive_hits))
        if positive_hits
        else 0.0,
        "positive_users": len(positive),
        "coverage": len({i for rec in recommendations.values() for i in rec})
        / catalog_size,
        "evaluated_users": len(truth),
    }


def pareto_mask(frame):
    """Maximize HR and coverage, minimize fit+ranking wall time and serialized size."""
    values = frame[
        ["hit_rate_at_10", "coverage", "total_seconds", "model_bytes"]
    ].to_numpy() * [1, 1, -1, -1]
    return [
        not any(np.all(other >= row) and np.any(other > row) for other in values)
        for row in values
    ]
