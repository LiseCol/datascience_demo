#Import common modules
import streamlit as st
import pandas as pd
pd.options.mode.chained_assignment = None
from PIL import Image

import numpy as np
import plotly.express as px

## Page config ##
st.set_page_config(page_title="Facebook ad Report", 
                   page_icon=":bar_chart:",
                   layout='wide')

# Page title                   
st.title("Facebook ad Report :bar_chart:")

# Load the data
df = pd.read_csv('data_clean_2.csv', index_col=0)
color_list = ['DarkCyan', 'GreenYellow', 'Orchid']

# Define functions
def groupby_all(variable):
    return df.groupby([variable]).agg(
                                        {'impressions':np.sum, 
                                      'spend': np.sum, 
                                      'purchase': np.sum, 
                                      'link click': np.sum, 
                                      'revenue': np.sum, 
                                      'daily budget $': np.sum,
                                      'spend $': np.sum, 
                                      'revenue $': np.sum, 
                                      'daily budget': np.sum,
                                     'currency':pd.Series.mode}).reset_index()

st.title('TO DECIDE WHAT I WANT TO PUT')
# add sth into sidebar
text = """
    ## Welcome to my interactive dashboard ##
    ---------------------
    **Note:**\n
    **The dashboard is based on a sample of 2 months facebook ads data.**\n
    ---------------------
    """
st.sidebar.markdown(text)

    #Checkbox
st.sidebar.subheader("Choose your favorite view")
    
st.sidebar.checkbox("Performance per country")
st.subheader("Performance per country")

st.table(groupby_all('country'))

# Static plots in two columns
col1, col2 = st.columns(2)

with col1:
    # View per country
    st.subheader('Per country')
    df_behaviour_countries = df.groupby(['country','date']).agg(
                                        {'spend $': np.sum,
                                         'revenue $': np.sum,
                                        'purchase': np.sum}
                                        ).reset_index()

    all_countries = df_behaviour_countries['country'].unique().tolist()
    options = st.selectbox('Which country are you interested in diving in?', all_countries)

    # Filter the information for this port specifically
    ind_country = df_behaviour_countries[df_behaviour_countries['country']== options]

    fig1 = px.bar(ind_country, 
                 x = "date", 
                 y = ["spend $","revenue $"])
    fig1.update_yaxes(visible=False, fixedrange=True)

    fig1.update_layout(barmode='group')
    st.plotly_chart(fig1)

with col2:    
    st.subheader('Per target type')
    df_behaviour_target = df.groupby(['target type','date']).agg(
                                        {'spend $': np.sum,
                                         'revenue $': np.sum,
                                        'purchase': np.sum}
                                        ).reset_index()

    all_target = df_behaviour_target['target type'].unique().tolist()
    options = st.selectbox('Which target type are you interested in diving in?', all_target)

    # Filter the information for this port specifically
    ind_target = df_behaviour_target[df_behaviour_target['target type']== options]

    fig2 = px.bar(ind_target, 
                 x = "date", 
                 y = ["spend $","revenue $"])
    fig2.update_yaxes(visible=False, fixedrange=True)

    fig2.update_layout(barmode='group')
    st.plotly_chart(fig2)
    