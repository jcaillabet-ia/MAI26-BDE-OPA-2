from sklearn.ensemble import RandomForestRegressor
from .MachineLearning import MachineLearning

class MachineLearningV1(MachineLearning):
    def __init__(self, candles):
        super().__init__(candles)

        self.model = RandomForestRegressor(
            n_estimators=200,
            random_state=42           
        )

    def build_target(self):
        self.candles['target'] = self.candles['close'].shift(-(24))
        self.candles = self.candles.dropna()
        return self.candles['target']

    def build_features(self):
        return self.candles[['timestamp', 'open', 'high', 'low', 'volume']]
    