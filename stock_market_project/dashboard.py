

import streamlit as st
import numpy as np
import config as cfg
import ml_deploy as mldep

import pandas as pd
import feature_store as fstore
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config('Stock.Predict', layout='wide')


ticker_selection = st.sidebar.selectbox('Ticker:', [cfg.STOCK_TICKER, 'aapl', 'googl', 'msft'], index=0)
model_selection = st.sidebar.selectbox('Model:', ['LinearRegression', 'ElasticNet'], index=0)
st.sidebar.title(ticker_selection)
# @st.cache
def get_data(ticker: str=None) -> tuple:
    """Builds data sets and engineers features
    Runs feature store pipeline

    Returns:
        tuple: X (pd.DataFrame), y (pd.Series), df (pd.DataFrame)
    """
    X_, X, y, df = fstore.pipeline.run(ticker)
    return X_, X, y, df

# Gets data from feature store pipeline
X_, X, y, df = get_data(ticker=ticker_selection)

col1, col2 = st.columns(2)


def modeler(X: pd.DataFrame=X, y: pd.Series=y, df: pd.DataFrame=df, X_: pd.DataFrame=X_, model: str=model_selection) -> None:
    """Builds model and generates predictions

    Args:
        X (pd.DataFrame, optional): The features df. Defaults to X.
        y (pd.Series, optional): The target Series. Defaults to y.
        df (pd.DataFrame, optional): The full df. Defaults to df.
        X_ (pd.DataFrame, optional): The data to make predictions with. Defaults to X_.
        model (str, optional): string value of sklearn estimator to use. Defaults to model_selection.
    """    
   
    stock_model = mldep.StockPredictor(model, X, y)
    stock_model.train_model()
    full_predictions = stock_model.make_prediction(stock_model.X)
    
    df['prediction'] = full_predictions
    df['date'] = pd.to_datetime(df['date'])
    df['date'] = df['date'].dt.date
    df['error'] = df['prediction'] - df['close']
    
    display_df = df.set_index(keys='date')
    last_5_predictions = display_df[['prediction', 'close', 'error']].tail()
    pred = stock_model.make_prediction(X_)
 
    with col1:
        st.header('Prediction for the next close:')
        st.title(f'{round(pred[0], 4)}')
        # st.write(round(pred[0],4))
    with col2:
        st.header('Previous Predictions & Actuals:')
        st.write(last_5_predictions)
    container1 = st.container()
    
    set_range = st.sidebar.select_slider('Select number of days to view on graph', options = np.arange(10, 800), value=410)
    dd = display_df.tail(set_range)
    
    fig = px.line(dd, x=dd.index, y='close')
    fig.add_trace(go.Scatter(x=dd.index, y=dd['prediction'], name='Predictions'))
    # st.line_chart(df_slice[['close', 'prediction']])
    container1.plotly_chart(fig)
    st.write('Overall RMSE for model:', round(stock_model.rmse(),4))
    st.sidebar.write('These predictions should not be taken as actual financial advice. It is only intended to showcase a machine learning project')

modeler()







