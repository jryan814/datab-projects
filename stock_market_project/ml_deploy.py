
from joblib import dump, load
from pandas import DataFrame, Series
import  numpy as np
from sklearn.utils import all_estimators
from sklearn.metrics import mean_squared_error

import config as cfg

mdls = {i[0]: i[1] for i in all_estimators()}


    
class StockPredictor():
    def __init__(self, model: str, X: DataFrame, y: Series, tform: str=None, *args, **kwargs):
        """Stock Prediction Modeler

        Args:
            model (str): Name of sklearn estimator to use.
            X (DataFrame): Features
            y (Series): Targets
            tform (str, optional): sklearn scaler to use. Defaults to None.
        """        
        self.model = mdls[model](**kwargs)
        self.needs_tform = False if tform == None else True
        if self.needs_tform:
            self.tformer = mdls[tform]()
        self.X, self.y = X, y
        self.prediction_data = None

    def transform_data(self):
        if not self.needs_tform:
            pass
        else:
            self.tformer.fit(self.X)
            self.X = self.tformer.transform(self.X)

    def transform_pred_features(self, prediction_data: np.ndarray) -> np.ndarray:
        if self.needs_tform:
            return self.tformer.transform(prediction_data)
        else:
            return prediction_data

    def train_model(self):
        if self.needs_tform:
            self.transform_data()
        self.model.fit(self.X, self.y)

    def make_prediction(self, _X: np.ndarray) -> np.ndarray:
        self.prediction_data = _X
        _X = self.transform_pred_features(_X)
        prediction = self.model.predict(_X)
        print(_X)
        return prediction

    def rmse(self):
        full_prediction = self.model.predict(self.X)
        rmse = mean_squared_error(self.y, full_prediction, squared=False)
        return rmse
    def save_model(self):
        pass

    def load_model(self):
        pass


if __name__ == '__main__':
    from sklearn.datasets import load_boston
    # X, y = load_boston(return_X_y=True)
    
    # sp = StockPredictor('LinearRegression', X, y, 'PowerTransformer')
    # sp.train_model()
    # print(sp.model.score(sp.X, sp.y))
    # print(sp.make_prediction(X[-1:]),y[-1:])
    # print(sp.prediction_data)

    
