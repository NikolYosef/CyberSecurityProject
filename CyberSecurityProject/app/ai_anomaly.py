from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable, List, Optional
import os

import joblib
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.ensemble import IsolationForest

HF_MODEL_NAME = os.getenv("HF_EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

MODEL_DIR = os.getenv("AI_MODEL_DIR", "app/ai_models")
os.makedirs(MODEL_DIR, exist_ok=True)

IF_PATH = os.path.join(MODEL_DIR, "isoforest.joblib")


@dataclass
class AnomalyResult:
    score: float
    is_anomaly: bool


class LogAnomalyDetector:
    # Sets up the embedding model and prepares the anomaly model.
    def __init__(self):
        self.embedder = SentenceTransformer(HF_MODEL_NAME)
        self.model: Optional[IsolationForest] = None

    # Turns log texts into numeric vectors the model can use.
    def _embed(self, texts: List[str]) -> np.ndarray:
        emb = self.embedder.encode(texts, normalize_embeddings=True)
        return np.array(emb, dtype=np.float32)

    # Trains the anomaly model on normal logs and saves it to a file.
    def train(self, normal_texts: List[str], contamination: float = 0.02):
        X = self._embed(normal_texts)
        self.model = IsolationForest(
            n_estimators=250,
            contamination=contamination,
            random_state=42
        )
        self.model.fit(X)
        joblib.dump(self.model, IF_PATH)

    # Loads a saved anomaly model from disk if it exists.
    def load(self) -> bool:
        if os.path.exists(IF_PATH):
            self.model = joblib.load(IF_PATH)
            return True
        return False

    # Gives one log a risk score and marks it as anomaly if it passes the threshold.
    def score_one(self, text: str, threshold: float = 0.65) -> AnomalyResult:
        if not self.model:
            return AnomalyResult(score=0.0, is_anomaly=False)

        X = self._embed([text])
        normality = float(self.model.decision_function(X)[0])
        score = 1.0 / (1.0 + np.exp(3.0 * normality))
        return AnomalyResult(score=score, is_anomaly=score >= threshold)
