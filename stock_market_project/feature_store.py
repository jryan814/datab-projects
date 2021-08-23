from datetime import timedelta
import datetime as dt

from yahooquery import Ticker
import pandas as pd

import config as cfg


class FeaturesPipeline():
    def __init__(self, original_df: pd.DataFrame, target_col: str='close', *args, **kwargs):
        """## Pipeline for feature engineering

        Args:
            original_df (pd.DataFrame): Origin df
            target_col (str, optional): Target column for feature engineering and predictions. Defaults to 'close'.
        """        
        self.original_df = original_df
        self.df = self.original_df.copy()
        self.target_col = target_col
        try:
            self.df = self.df.reset_index().drop(columns='symbol')
        except:
            pass
        self.df = self.df[['date', 'high', 'low', 'volume', 'close']].copy()
        self.df['date'] = pd.to_datetime(self.df['date'])
        self.features = []
    
    def add_weekday(self):
        """Adds weekday column to df

        Returns:
            pd.DataFrame: Updated df.
        """        
        self.df['weekday'] = self.df['date'].dt.weekday
        self.features.append('weekday')
        return self.df

    def avg_volume(self, window: int=2) -> pd.DataFrame:
        new_col_name = f'avg_vol_{window}_periods'
        self.features.append(new_col_name)
        self.df[new_col_name] = self.df['volume'].shift(periods=1).rolling(window).mean()
        return self.df

    def avg_period(self, window: int=7):
        new_col_name = f'avg_{window}_periods'
        self.features.append(new_col_name)
        self.df[new_col_name] = self.df[self.target_col].shift(periods=1).rolling(window).mean()
        return self.df

    def multiple_avg_periods(self, windows: list=[2, 3, 5]):
        """Calculates averages for multiple periods

        Args:
            windows (list, optional): Periods to shift by. Defaults to [2, 3, 5, 30].

        Returns:
            pd.DataFrame: Updated df.
        """        
        for n in windows:
            self.df = self.avg_period(n)
        return self.df

    def std_period(self, window: int=7):
        """Calculates the standard deviation for the period shift  

        Args:
            window (int, optional): periods to shift by. Defaults to 7.
        
        Returns:
            pd.DataFrame: Updated df.
        """        
        new_col_name = f'std_{window}_periods'
        self.features.append(new_col_name)
        self.df[new_col_name] = self.df[self.target_col].shift(periods=1).rolling(window).std()
        return self.df
    
    def multiple_std_periods(self, windows: list=[2, 3]):
        """Calculates the standard deviations for multiple period shifts

        Args:
            windows (list, optional): [description]. Defaults to [2, 3].

        Returns:
            pd.DataFrame: Updated df.
        """        
        for n in windows:
            self.df = self.std_period(n)
        return self.df

    def avg_high_low_period(self, window: int=7):
        """Calculates the avg high low difference for the period shift  

        Args:
            window (int, optional): periods to shift by. Defaults to 7.
        
        Returns:
            pd.DataFrame: Updated df.
        """        
        new_col_name = f'high_low_{window}_periods'
        self.features.append(new_col_name)
        self.df[new_col_name] = self.df['high'].shift(periods=1).rolling(window).mean() - self.df['low'].shift(periods=1).rolling(window).mean()
        return self.df

    def multiple_avg_hl_periods(self, windows: list=[2, 3, 5, 30]):
        """Calculates the standard deviations for multiple period shifts

        Args:
            windows (list, optional): [description]. Defaults to [5, 15, 30].

        Returns:
            pd.DataFrame: Updated df.
        """        
        for n in windows:
            self.df = self.avg_high_low_period(n)
        return self.df
    
    def prev_day_close_period(self, window: int=1):
        """Prev day closing price  

        Args:
            window (int, optional): periods to shift by. Defaults to 1.
        
        Returns:
            pd.DataFrame: Updated df.
        """        
        new_col_name = f'high_low_{window}_periods'
        self.features.append(new_col_name)
        self.df[new_col_name] = self.df['high'].shift(periods=1).rolling(window).mean() - self.df['low'].shift(periods=1).rolling(window).min()
        return self.df

    def auto_encode(self):
        cols_to_encode = []
        for col in self.df.columns:
            uniq_vals = len(self.df[col].value_counts())
            if uniq_vals <= 8:
                cols_to_encode.append(col)
                self.features.remove(col)
        self.df[cols_to_encode] = self.df[cols_to_encode].astype('category')
        dummies = pd.get_dummies(self.df[cols_to_encode], drop_first=True)
        for c in dummies.columns:
            self.features.append(c)
        encoded_df = pd.concat([self.df, dummies], axis=1)
        return encoded_df

    def run(self, return_X_y: bool=True, encode: bool=True, **kwargs):
        """Runs pipeline

        Args:
            return_X_y (bool, optional): Automatically separate features/target sets. Defaults to True.
            encode (bool, optional): Encode features with low cardinality with one-hot encoder. Defaults to True.

        Returns:
            pd.DataFrame, pd.Series: if return_X_y == False then only returns full dataframe.
        """        
        self.add_weekday()
       
        self.multiple_avg_periods(**kwargs)
        self.multiple_std_periods(**kwargs)
        self.multiple_avg_hl_periods(**kwargs)
        
        self.df = self.df.dropna()
        if encode:
            self.df = self.auto_encode()
        if return_X_y:
            return self.filter_Xy()
        else:
            return self.df

    def filter_Xy(self):
        # X is only features and y is the targets
        X = self.df[self.features]
        y = self.df[self.target_col]
        return X, y, self.df

def next_prediction_features(df):
    pred_row = df.iloc[-1].copy()
    pred_df = df.append(pred_row)
    p = FeaturesPipeline(pred_df)
    X, *_ = p.run()
    X_ = X.iloc[-1:].copy()
    return X_
    

def get_prev_close_date(today: dt.date=cfg.TODAY_DATE, date_string: bool=False):
    """Calculates the previous business date  

    TODO: Factor in holidays.

    Args:
        today (dt.date, optional): Today's date or specific date to predict the next day. Defaults to cfg.TODAY_DATE.

    Returns:
        dt.date: The prev business day's date.
    """    
    prev_date = today + timedelta(days=-1)
    while prev_date.weekday() > 5:
        prev_date += timedelta(days=-1)
    if date_string:
        prev_date = dt.date.strftime(prev_date, '%Y-%m-%d')
    return prev_date

def get_new_data(ticker: str=None, get_df: bool=False):
    
    if not ticker:
        stock = Ticker(cfg.STOCK_TICKER)
        stock_df = stock.history(period='max', interval='1d', start=cfg.START_DATE)
        pipeline = FeaturesPipeline(stock_df)
        X, y = pipeline.run()
        if get_df:
            stock_df2 = pipeline.run(return_X_y=False, encode=False)
            return X, y, stock_df2
        return X, y
    else:
        try:
            stock = Ticker(ticker)
        except:
            raise Exception(f'{ticker} not a valid ticker symbol, or is not accepted via yahoo finance')
        stock_df = stock.history(period='max', interval='1d', start=cfg.START_DATE)
        cfg.STOCK_TICKER = ticker
        pipeline = FeaturesPipeline(stock_df)
        X, y = pipeline.run()
        if get_df:
            stock_df2 = pipeline.run(return_X_y=False, encode=False)
            return X, y, stock_df2
        return X, y





########################################################################
from time import time



class Pipeline:
    def __init__(self):
        self.tasks = []
        
    def task(self, depends_on=None):
        idx = 0
        if depends_on:
            idx = self.tasks.index(depends_on) + 1
        def inner(f):
            self.tasks.insert(idx, f)
            return f
        return inner
    def run(self, x):
        for i in self.tasks:
            x = i(x)
        return x
start = time()
pipeline = Pipeline()

@pipeline.task()
def first_task(ticker: str=None) -> pd.DataFrame:
    """Get dataframe from yahoo finance

    Args:
        ticker (str, optional): ticker symbol to collect data for. Defaults to None.

    Raises:
        Exception: if ticker is invalid.

    Returns:
        pd.DataFrame: The un-engineered dataframe
    """    
    if not ticker:
        stock = Ticker(cfg.STOCK_TICKER) 
    else:
        try:
            stock = Ticker(ticker)
        except:
            raise Exception(f'{ticker} not valid stock ticker')
    stock_df = stock.history(period='max', interval='1d')
    return stock_df
        
@pipeline.task(depends_on=first_task)
def second_task(df: pd.DataFrame) -> pd.DataFrame:
    """Get final datasets and features for prediction

    Args:
        df (pd.DataFrame): Initial dataframe

    Returns:
        pd.DataFrame: Fully transformed and engineered df
    """    
    p = FeaturesPipeline(df)
    X_ = next_prediction_features(df)
    X, y, df = p.run()
    return X_, X, y, df
    








if __name__ == '__main__':
    X, y, df = pipeline.run(None)
    print(X.shape, y.shape, df.shape)
    end = time()
    print('-'*30)
    print('seconds to complete:', round(end-start, 1))
    print('-'*30)






    
            
