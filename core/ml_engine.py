import numpy as np
from sklearn.ensemble import RandomForestRegressor

class MarketPredictor:
    def __init__(self):
        self._train_model()

    def _train_model(self):
        np.random.seed(42)
        n_samples = 2000
        
        inflation = np.random.uniform(1.0, 15.0, n_samples)
        marketing = np.random.uniform(10000, 150000, n_samples)
        comp_price = np.random.uniform(80, 250, n_samples)
        
        self.X_train = np.column_stack((inflation, marketing, comp_price))
        
        base_volume = 15000 - (inflation * 400) + (marketing * 0.08) + (comp_price * 15)
        noise_vol = np.random.normal(0, 800, n_samples)
        y_volume = np.maximum(base_volume + noise_vol, 1000)
        
        base_volatility = 0.05 + (inflation * 0.012)
        noise_volat = np.random.normal(0, 0.01, n_samples)
        y_volatility = np.clip(base_volatility + noise_volat, 0.01, 0.60)
        
        self.y_train = np.column_stack((y_volume, y_volatility))
        
        self.model = RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42)
        self.model.fit(self.X_train, self.y_train)

    def predict_conditions(self, inflation: float, marketing: float, comp_price: float) -> dict:
        X_new = np.array([[inflation, marketing, comp_price]])
        prediction = self.model.predict(X_new)[0]
        
        return {
            "PredictedVolume": int(prediction[0]),
            "PredictedVolatility": float(prediction[1])
        }