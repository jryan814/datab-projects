########################################
#
# SEE MY NEWLY CREATED VERSION IN THE stock_market_project
#
########################################


import pandas as pd
from datetime import datetime as dt
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, mean_absolute_error
import numpy as np

print('''
.______________________________.
|   STOCK MARKET PREDICTIONS   |
|        version 0.0.0.5       |
'------------------------------'
''')
# TODO: Get up-to-date data, and make it customizeable to different stocks
# Implement API and possibly SQL db to track different stocks
df = pd.read_csv('sphist.csv')
df['Date'] = pd.to_datetime(df['Date'])

df = df.sort_values('Date', ascending=True).reset_index()
df.drop(columns=['index'], inplace=True)

def mean_n_prev_days(df, n=5):
    '''
    Calculates the mean of the previous 5 day closes [does not count current row].
    Creates new column in df with values.
    '''
    new_col = 'avg_{}_day'.format(n)
    vals = []
    for index, row in df.iterrows():
        n_mean = df.iloc[index-n:index]['Close'].mean()
        if pd.isnull(n_mean):
            n_mean = 0
        vals.append(n_mean)
    df[new_col] = vals
    return df

def add_features(df, col, n_days=5, measure='std'):
    '''
    Multiple feature additions in one function.
    measures include: 'std', 'day_of_week', 'vol_diff'
    '''
    if measure == 'day_of_week':
        new_col = measure
        df[new_col] = df[col].dt.weekday
        return df
    if measure == 'std':
        vals = []
        new_col = '{measure}_rolling_{n_days}'.format(measure=measure, n_days=n_days)
        for index, row in df.iterrows():
            stds = df.iloc[index-n_days:index][col].std()
            vals.append(stds)
        df[new_col] = vals
        return df
    if measure == 'vol_diff':
        vals = []
        new_col = '{measure}_{n_days}_days_avg'.format(measure=measure, n_days=n_days)
        if n_days < 2:
            n_days = 2
        for index, row in df.iterrows():
            vol_diff = df.iloc[index-n_days:index-1][col].mean() - df.iloc[index-1][col]
            if pd.isnull(vol_diff):
                vol_diff = 0
            vals.append(vol_diff)
        df[new_col] = vals
        return df
# TODO: Create class to do the feature engineering
new_features = df.copy()
new_features = mean_n_prev_days(new_features)
new_features = mean_n_prev_days(new_features, n=10)
new_features = add_features(new_features, 'Close')
new_features = add_features(new_features, 'Volume', n_days=5, measure='vol_diff')
new_features = add_features(new_features, 'Close', measure='std')

df_data = new_features[new_features['Date'] > '1951-01-02'].copy()
df_data.dropna(axis=0)
df_data.reset_index(drop='index', inplace=True)

def train_test(train, test, target='Close', add=True):
    features = []
    target = 'Close'

    for col in train.columns:
        if col[0].isupper():
            continue
        else:
            features.append(col)

    lr = LinearRegression()

    lr.fit(train[features], train[target])
    predictions = lr.predict(test[features])
    
    metric_err1 = mean_absolute_error(test[target], predictions)
    # Originally for printing out both MAE & MSE
    # output1 = 'Mean Absolute Error:'
    # metric_err2 = mean_squared_error(test[target], predictions)
    # output2 = 'Mean Squared Error:'
    if not add:
        return metric_err1
    else:
        return (metric_err1, train, test)

train_0 = df_data[df_data['Date'] < '2013-01-01']
test_0 = df_data[df_data['Date'] >= '2013-01-01']
err_metric, tr1, te1 = train_test(train_0, test_0)
print('Traditional train and test data sets...')
print('Absolute Mean Error:', err_metric, '\n---------------------------------------')

results_list = []
residual_df = df_data.copy()

def train_test_run(train, test, incremen, results_list, testing=False):
    '''
    Recursively runs train_test() on individual rows of the dataset.
    After each row it adds that row to the training dataset, and tests the next row in the testing data.
    '''
    ## created the testing parameter to make sure it was exhausting the testing dataset 1 by 1
    ## Effectively it does the same thing as below, but drops the row after testing
    if testing:
        test1 = test.iloc[0:1]
        if test1.shape[0] == 0:
            return results_list
        metric_err, train, test0 = train_test(train, test1)
        results_list.append(metric_err)
        train = pd.concat([train, test0], ignore_index=True)
        test = test.drop(test1.index, axis=0)
        incremen += 1
        train_test_run(train, test, incremen, results_list, testing=True)
        return results_list
        
    test1 = test.iloc[incremen:incremen+1]
    if test1.shape[0] == 0:
        return results_list
    metric_err, train, test0 = train_test(train, test1)
    results_list.append(metric_err)
    train = pd.concat([train, test0], ignore_index=True)
    incremen += 1
    train_test_run(train, test, incremen, results_list)
    return results_list
    
train = df_data[df_data['Date'] < '2013-01-01']
test = df_data[df_data['Date'] >= '2013-01-01']
results = train_test_run(train, test, 0, results_list=[], testing=True)
print("'Daily' test and concatenating test into training data for next 'day'.")
print('Average error:', np.mean(results), '\n_________________________________')

# Next steps...get a better dataset and make it more cross-functional.

