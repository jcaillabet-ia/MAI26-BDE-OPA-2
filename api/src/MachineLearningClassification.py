from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import precision_score

from .MachineLearning import MachineLearning

class MachineLearningClassification(MachineLearning):
    def __init__(self):
        #super().__init__()

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

    def add_features(self, df):
        df['close_smoothed'] = df['close'].rolling(window=1000, min_periods=1).mean()
        df['target'] = df['close'].shift((24))
        df['target_pct'] = ((df['close'].shift((24)) - df['close']) / df['close']) * 100

        df['target_bin'] = (df['close_smoothed'].shift((24)) > df['close_smoothed']).astype(int)

        for i in range(1, 10):
            df['close_m-{}'.format(i)] = df['close'].shift(i)

        df.dropna()

        return df
        
    def score(self):
        return precision_score(self.y_test, self.y_predict)
    
    