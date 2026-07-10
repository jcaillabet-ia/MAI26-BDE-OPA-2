from abc import ABC, abstractmethod
import pandas as pd
from sklearn.model_selection import train_test_split

class MachineLearning(ABC):
    candles : pd.DataFrame = None

    X_train : pd.DataFrame = None
    y_train : pd.DataFrame = None
    X_test : pd.DataFrame = None
    y_test : pd.DataFrame = None

    model = None

    def __init__(self, candles):
        self.candles = pd.DataFrame(candles, columns= ['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        self.candles['timestamp'] = (self.candles['timestamp'].astype('int64') // 10**6)
    
    def clean(self):
        self.candles = self.candles.drop_duplicates(subset=['timestamp']).reset_index(drop=True)
        self.candles = self.candles.sort_values(by='timestamp', ascending=True)

        self.target = self.build_target()
        self.features = self.build_features()
    
    @abstractmethod
    def build_target(self):
        pass

    @abstractmethod
    def build_features(self):
        pass

    def setup(self):
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(self.features, self.target, test_size = 0.25, random_state=42, shuffle=False)
    
    def train(self):
        self.model.fit(self.X_train, self.y_train)
    
    def predict(self, xs):
        return self.model.predict(xs)

    def score(self):
        return {"train": self.model.score(self.X_train, self.y_train), "test": self.model.score(self.X_test, self.y_test)}
    