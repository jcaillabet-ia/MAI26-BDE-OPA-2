from abc import ABC, abstractmethod
import pandas as pd
from sklearn.model_selection import train_test_split

class MachineLearning(ABC):
    candles : pd.DataFrame = None

    X_train : pd.DataFrame = None
    y_train : pd.DataFrame = None
    X_test : pd.DataFrame = None
    y_test : pd.DataFrame = None
    y_predict : pd.DataFrame = None

    model = None

    def __init__(self, candles):
        ##self.candles = pd.DataFrame(candles, columns= ['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        
        #self.candles['timestamp'] = (self.candles['timestamp'].astype('int64') // 10**6)
        #self.add_features()
        #self.candles = self.candles.dropna()
        pass
    
    def transform(self, candles):
        df = pd.DataFrame(candles, columns= ['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df = self.add_features(df)
        df = self.clean(df)

        df_res = df[['timestamp', 'open', 'high', 'low', 'close', 'volume', 'target_bin']]
        df_res['timestamp'] = (df_res['timestamp'].astype('int64') // 10**6)

        for i in range(1, 10):
            df_res['close_m-{}'.format(i)] = df['close'].shift(i)
        df_res = df_res.dropna()

        target_indice = df_res.columns.get_loc('target_bin')

        return {"target_indice": target_indice, "data": df_res.to_numpy().tolist()}

    def clean(self, df):
        df = df.drop_duplicates(subset=['timestamp']).reset_index(drop=True)
        df = df.sort_values(by='timestamp', ascending=True)

        # df = self.build_target(df)
        # df = self.build_features(df)

        return df

    @abstractmethod
    def build_target(self, df):
        pass

    @abstractmethod
    def build_features(self, df):
        pass

    @abstractmethod
    def add_features(self, df):
        pass

    def setup(self, data, target_indice):
        df = pd.DataFrame(data)
        
        taille_min = min(len(df.drop(columns=[target_indice])), len(df.iloc[:, target_indice]))

        features = df.drop(columns=[target_indice]).iloc[:taille_min]
        target = df.iloc[:, target_indice].iloc[:taille_min]

        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(features, target, test_size = 0.25, random_state=42, shuffle=False)
    
    def train(self):
        self.model.fit(self.X_train, self.y_train)
    
    def predict(self, xs):
        self.y_predict = self.model.predict(xs)
        return self.y_predict 

    @abstractmethod
    def score(self):
        pass