
# imports
from sklearn.utils import all_estimators
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.model_selection import train_test_split, cross_val_predict, cross_val_score

import matplotlib.pyplot as plt
import seaborn as sns

from joblib import dump, load
import numpy as np
import pandas as pd

import config as cfg

import feature_store


# all sklearn models
sk_mdls = {i[0]: i[1] for i in all_estimators()}

def access_classes(est_list):
    models_dict = {i[0]: i[1] for i in est_list}
    return models_dict

clfs = access_classes(all_estimators(type_filter='classifier'))
rgrs = access_classes(all_estimators(type_filter='regressor'))
clusts = access_classes(all_estimators(type_filter='cluster'))
tforms = access_classes(all_estimators(type_filter='transformer'))

class Model():
    """# Model Wrapper
    ML Model wrapper for sklearn estimators

    Raises:
        FileNotFoundError: If unable to find saved model

    Returns:
        Model: Trained ML model
    """    
    active = []
    def __init__(self, model: str, X: pd.DataFrame, y: pd.Series, auto: bool=True, test_size: float=0.4, shuffle: bool=True, encode_features: bool=False,
            random_state: int=13, stratify: int=None, tform: str=None, *args, **kwargs):
        """## init sklearn ML model wrapper

        Args:
            - model (str): String name of sklearn estimator.
            - X (pd.DataFrame, np.ndarray, array-like): X data set (features)
            - y (pd.Series, pd.DataFrame, np.ndarray): y data set (targets/labels)
            - auto (bool, optional): Auto train, test model. Defaults to True.
            - test_size (float, optional): Test size for train/test split. Defaults to 0.4.
            - shuffle (bool, optional): Shuffle data in train/test split. Defaults to True.
            - encode_features (bool, optional): Encode low cardinality features (requires pd.DataFrame). Defaults to False.
            - random_state (int, optional): Used for the randomused. Defaults to None.
            - stratify (int, optional): Stratify for train/test split. Defaults to None.
            - tform (sklearn.transformer, optional): Whether to scale/normalize the data. Defaults to None.   
        optional kwargs:
            - Any specific parameters to pass to the model
        """        
        self.model = sk_mdls[model](*args, **kwargs)
        self.X = X
        self.y = y
        self.auto = auto
        if encode_features:
            self.X = self.encode_features()
        if test_size:
            # Split the data into training and testing sets
            (self.X_train, self.X_test,
            self.y_train, self.y_test) = train_test_split(self.X, self.y, test_size=test_size, shuffle=shuffle,
                                                                    random_state=random_state, stratify=stratify)
        else:
            self.X_train = self.X
            self.y_train = self.y
            self.X_test = None
            self.auto = False

        self.needs_tform = False if tform == None else True
        if self.needs_tform:
            self.tformer = sk_mdls[tform]()

        self.active.append(self)
        if self.auto:
            self.fit_model(self.auto)

    def transform_data(self, prediction_data: pd.DataFrame=None):
        if not self.needs_tform:
            pass
        else:
            self.tformer.fit(self.X)
            self.X = self.tformer.transform(self.X)
            # if prediction_data != []:
            #     prediction_data = self.tformer.transform(prediction_data)
            #     return prediction_data

    def transform_pred_features(self, prediction_data: np.ndarray) -> np.ndarray:
        """transforms the features for making predictions outside of the existing dataset

        Args:
            prediction_data (np.ndarray): The untransformed data

        Returns:
            np.ndarray: The transformed data for predicting
        """        
        if self.needs_tform:
            return self.tformer.transform(prediction_data)
        else:
            return prediction_data
    
    def fit_model(self, auto: bool=False):
        """Fit the model with the training dataset

        Args:
            auto (bool, optional): Proceeds to the test method if True. Defaults to False.

        Returns:
            sklearn.model: The trained model
        """        
        if self.needs_tform:
            self.transform_data()
        self.model.fit(self.X_train, self.y_train)
        if auto:
            self.test()

    def test(self):
        """
        Test dataset
        """        
        self.predictions = self.model.predict(self.X_test)
        self.cross_val_preds = cross_val_predict(self.model, self.X, self.y, n_jobs=-1)
        self.results = {
            'model': self.model,
            'm_score': round(self.model.score(self.X_test, self.y_test), 5),
            'cv_avg': round(np.mean(cross_val_score(self.model, self.X_test, self.y_test, n_jobs=-1)), 5),
            'RMSE': round(mean_squared_error(self.y_test, self.predictions, squared=False), 5),
            'MAE': round(mean_absolute_error(self.y_test, self.predictions), 5)
        }

    def make_prediction(self, _X):
        """Make on-demand predictions

        Args:
            _X (array-like): Features to make predictions

        Returns:
            np.ndarray: The prediction generated by the model
        """        
        self.prediction_data = _X
        _X = self.transform_pred_features(_X)
        prediction = self.model.predict(_X)
        print(_X)
        return prediction
    
    def display_comps(self, only_error: bool=False):
        """Prints out all 'active' models' results

        Args:
            only_error (bool, optional): Only displays the error metrics (doesn't include model score or cv score). Defaults to False.
        """        
        for m in self.active:
            self.display_results(mdl=m, only_error=only_error)
    
    def display_results(self, mdl=None, only_error: bool=False):
        """Prints out current model's results

        Args:
            mdl (self.model, optional): Only used internally. Defaults to None.
            only_error (bool, optional): Only displays the error metrics (doesn't include model score or cv score). Defaults to False.
        """        
        if not mdl:
            mdl = self
        print('='*50)
        for k, v in mdl.results.items():
            if only_error:
                if 'M' not in k and k != 'model':
                    continue
            print('-'*50)
            print(k, '|', v, sep='\t')
        #print('='*5)

    def encode_features(self):
        """Class method to encode features of low cardinality

        Returns:
            X -> array-like: returns X with encoded columns
        """        
        encode_cols = []
        for col in self.X.columns:
            if len(self.X[col].value_counts()) < 12:
                self.X[col].astype('category')
                encode_cols.append(col)
                dummies = pd.get_dummies(self.X[col], drop_first=True)
                self.X = pd.concat([self.X, dummies], axis=1)
        self.X = self.X.drop(columns=encode_cols)
        return self.X
            

    def model_name(self, *args, **kwargs):
        model_name = str(self.model)[:str(self.model).index('(')]
        
        self.kwargs = {
            'fname': f'{model_name}_{cfg.TODAY_DATE}'
        }
        self.kwargs.update(kwargs)
        return self.kwargs['fname']

    def save_model(self, *args, **kwargs):
        
        dump(self, self.model_name(*args, **kwargs))

    def load_model(self, *args, **kwargs):
        from os import listdir
        loaded_model = None
        name = str(self.model)[:str(self.model).index('(')]
        try:
            loaded_model = load(self.model_name(*args, **kwargs))
        except:
            # looks for similar file name in ml directory
            for f in listdir(cfg.ML_DIR):
                if name[:5] in f:
                    name = f
            loaded_model = load(self.model_name(fname=name))
        finally:
            if not loaded_model:
                raise FileNotFoundError(f'Model file not found. Tried:\n{self.model_name()}\n{self.model_name(fname=name)}')
            return loaded_model

    def __repr__(self):
        i = self.active.index(self)
        rep = f'<{self.model}:active_model[{i}]>'
        return rep


    

if __name__ == '__main__':
    # some tests
    # test1: Picks a random regression model from sklearn's estimators
           # Runs model with the boston housing dataset
    from random import choice
    from sklearn.datasets import load_boston
    X, y = load_boston(return_X_y=True)
    regr_mdls = []
    for k in sk_mdls:
        if 'Regress' in k:
            regr_mdls.append(k)
    mdl_str = choice(regr_mdls)
    model1 = Model(sk_mdls[mdl_str], X, y, tform=sk_mdls['StandardScaler'])
    model1.display_results()
    # test2: Saves model
    model1.save_model()
    # test3: Uses class method to load model

    