import xgboost as xgb, joblib, numpy as np, pandas as pd
from stable_baselines3 import PPO
import datetime as dt, os

class AIEngine:
    def __init__(self, model_path: str):
        self.model_path = model_path
        self.model = self._load()

    def _load(self):
        try:
            return joblib.load(self.model_path)
        except FileNotFoundError:
            return None

    def train(self, df: pd.DataFrame, label: str = "y"):
        X = df.drop(columns=[label])
        y = df[label]
        dtrain = xgb.DMatrix(X, label=y)
        params = {"objective": "binary:logistic", "eta": 0.05, "max_depth": 6}
        bst = xgb.train(params, dtrain, num_boost_round=200)
        joblib.dump(bst, self.model_path)
        self.model = bst

    def predict(self, features: np.ndarray) -> float:
        if not self.model:
            return 0.5
        dmat = xgb.DMatrix(features.reshape(1, -1))
        return float(self.model.predict(dmat)[0])

    # ---------- RL pipeline ----------
    def train_rl(self, env, timesteps: int = 50_000, tag: str | None = None):
        model = PPO("MlpPolicy", env, verbose=0)
        model.learn(total_timesteps=timesteps)
        tag = tag or dt.datetime.utcnow().strftime("%Y%m%d%H%M")
        path = f"{os.path.splitext(self.model_path)[0]}_{tag}.zip"
        model.save(path)
        self.model = model
        return path

    def load_rl(self, path: str | None = None):
        from stable_baselines3.common.base_class import BaseAlgorithm  # lazy import
        p = path or self.model_path
        self.model: BaseAlgorithm = PPO.load(p)

    def predict_rl(self, obs):
        if not hasattr(self, "model"):
            self.load_rl()
        return self.model.predict(obs, deterministic=True)[0]