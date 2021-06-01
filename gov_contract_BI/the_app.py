import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go

import seaborn as sns
import matplotlib.style as style

import datetime as dt

style.use('fivethirtyeight')

pd.options.display.max_columns = 50


st.set_page_config(page_title='Biz Intel for Gov Contracting', page_icon='random', layout='wide')
st.set_option('deprecation.showPyplotGlobalUse', False)

st.title('Business Intelligence for Government Contracting', 'gov_contracting')
st.write("### For NAICS code range 5416's for Small Businesses in Target Range")
target = 'TOEROEK ASSOCIATES INC'
data = pd.read_csv('https://raw.githubusercontent.com/jryan814/datab-projects/main/gov_contract_BI/cleaned_gov_contracts_data.csv')

data = data.rename(columns={'recipient_name': 'Company', 'award_id': 'number_of_awards'})
data['naics_code'] = data['naics_code'].astype(str)
data.style.format({'dollars_obligated': '{:$.2f}'})

company_names = data['Company'].unique()
selection = st.selectbox('Company selection', company_names)

naics_codes = data['naics_code'].unique()
naics_data = data.groupby(['naics_code', 'Company']).agg({'dollars_obligated': 'sum', 'number_of_awards': 'nunique'}).reset_index()
    
left, right = st.beta_columns([5,5])
   
    
    
@st.cache(suppress_st_warning=True)
def company_profile(co_name, data):
    co_data = data[data['Company'] == co_name]
    naics_cats = co_data.groupby(['naics_code']).agg({'dollars_obligated': 'sum'})
    awards = co_data.groupby('naics_code').agg({'number_of_awards': 'nunique'})
    fig = px.bar(naics_cats, naics_cats.index, naics_cats['dollars_obligated'], template='seaborn', title='Dollars Obligated per NAICS Code')
    fig2 = px.bar(awards, awards.index, awards['number_of_awards'], template='seaborn', title='Number of Awards per NAICS Code')
    fig.update_xaxes(type='category')
    fig2.update_xaxes(type='category')
    other_info = {
        'dollar_total': round(naics_cats['dollars_obligated'].sum(), 2),
        'award_total': awards['number_of_awards'].astype(int).sum()
    }
    return fig, fig2, naics_cats, other_info

fig, fig2, d, other = company_profile(selection, data)
other_award = other['award_total']
other_dollars = other['dollar_total']
with left:
    st.plotly_chart(fig)
    st.info(f'Total Dollars Obligated: ${other_dollars}')
    
with right:
    st.plotly_chart(fig2)
    st.info(f'Total Awards Rec: {other_award}')
st.info(selection)
st.write(d)
