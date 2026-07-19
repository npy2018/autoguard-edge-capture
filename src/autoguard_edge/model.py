from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class TinyLinearAutoencoder:
    """A PCA-equivalent linear autoencoder suited to very small edge budgets."""

    components: int = 3
    mean_: np.ndarray | None = None
    basis_: np.ndarray | None = None
    scale_: float = 1.0

    def fit(self, windows: np.ndarray) -> "TinyLinearAutoencoder":
        x = np.asarray(windows, dtype=float)
        if x.ndim != 2 or len(x) < 4:
            raise ValueError("windows must be a 2D array with at least four samples")
        self.mean_ = x.mean(axis=0)
        centered = x - self.mean_
        _, _, vt = np.linalg.svd(centered, full_matrices=False)
        k = max(1, min(self.components, vt.shape[0]))
        self.basis_ = vt[:k]
        errors = self._errors(x)
        self.scale_ = float(np.quantile(errors, 0.99) + 1e-9)
        return self

    def _errors(self, windows: np.ndarray) -> np.ndarray:
        if self.mean_ is None or self.basis_ is None:
            raise RuntimeError("model is not fitted")
        x = np.asarray(windows, dtype=float)
        centered = x - self.mean_
        reconstructed = (centered @ self.basis_.T) @ self.basis_ + self.mean_
        return np.mean((x - reconstructed) ** 2, axis=1)

    def score(self, window: np.ndarray) -> float:
        value = float(self._errors(np.asarray(window, dtype=float).reshape(1, -1))[0])
        return min(1.0, value / self.scale_)
