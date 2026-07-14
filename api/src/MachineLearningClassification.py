from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import precision_score

from .MachineLearning import MachineLearning

class MachineLearningClassification(MachineLearning):
    def __init__(self, candles):
        super().__init__(candles)

        self.model = RandomForestClassifier(
            n_estimators=200,
            random_state=42           
        )

    def build_target(self):
        return self.candles['target_bin']

    def build_features(self):
        df_temp = self.candles[['timestamp', 'open', 'high', 'low', 'volume']]
        
        for i in range(1, 10):
            df_temp['close_m-{}'.format(i)] = self.candles['close_m-{}'.format(i)]

        return df_temp

    def add_features(self):
        self.candles['close_smoothed'] = self.candles['close'].rolling(window=1000, min_periods=1).mean()
        self.candles['target'] = self.candles['close'].shift(-(24))
        self.candles['target_pct'] = ((self.candles['close'].shift(-(24)) - self.candles['close']) / self.candles['close']) * 100
        
        self.candles['target_bin'] = (self.candles['close_smoothed'].shift(-(24)) > self.candles['close_smoothed']).astype(int)

        for i in range(1, 10):
            self.candles['close_m-{}'.format(i)] = self.candles['close'].shift(i)

        self.candles.dropna()
        
    def score(self):
        return precision_score(self.y_test, self.y_predict)
    
    