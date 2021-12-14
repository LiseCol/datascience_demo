#Import common modules
import streamlit as st
import pandas as pd
pd.options.mode.chained_assignment = None
from PIL import Image
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import datetime

## Page config ##
st.set_page_config(page_title="Facebook ad Report", 
                   page_icon=":bar_chart:",
                   layout='wide')
# Define functions
@st.cache
def load_data():
    df = pd.read_csv('data_clean_3.csv', index_col=0)
    df['date'] = pd.to_datetime(df['date'])
    df['date'] = df['date'].dt.strftime('%Y-%m-%d')
    return  df

#color_list = ['DarkCyan', 'GreenYellow', 'Orchid']

# Define functions
def custom_col(df):
    df['CPA'] = round(df['spend']/df['purchase'],2)
    df['CPM'] = round(df['spend']/(df['impressions']/1000),2)
    df['CPC'] = round(df['spend']/df['link click'],2)
    df['CTR'] = round((df['link click']/df['impressions']) ,5)
    df['ROAS'] = round(df['revenue']/df['spend'],2)
    
def ROAS_col(df):   
    df['ROAS'] = round(df['revenue $']/df['spend $'],2)

def custom_col_USD(df):
    df['CPA'] = round(df['spend $']/df['purchase'],2)
    df['CPM'] = round(df['spend $']/(df['impressions']/1000),2)
    df['CPC'] = round(df['spend $']/df['link click'],2) 
    df['CTR'] = round((df['link click']/df['impressions']),5)
    df['ROAS'] = round(df['revenue $']/df['spend $'],2)
    df['currency'] = 'USD'
    
def CPA_col(df):   
    df['CPA $'] = round(df['spend $']/df['purchase'],2)    
    
def df_clean(df):
    df.rename(columns = {'spend $':'spend','revenue $':'revenue','link click':'clicks'},inplace=True)
    df['CTR'] = df['CTR'].apply(lambda x: '{:.2%}'.format(x))
    for col in df.columns:
        if col == 'currency':
            df.drop(['currency'],axis=1,inplace=True)
        
def groupby_all(variable1,variable2,cur):
    # one variable only
    if cur == "local":
        df_var= load_data().groupby([variable1,variable2]).agg(
                                        {'impressions':np.sum, 
                                      'link click': np.sum, 
                                      'spend': np.sum, 
                                      'purchase': np.sum, 
                                      'revenue': np.sum
                                     }).reset_index()
        custom_col(df_var)
        df_clean(df_var)
        return df_var
    else:
        df_var= load_data().groupby([variable1,variable2]).agg(
                                        {'impressions':np.sum,
                                         'link click': np.sum,
                                         'spend $': np.sum,
                                      'purchase': np.sum, 
                                      'revenue $': np.sum}).reset_index()
        custom_col_USD(df_var)
        df_clean(df_var)
        return df_var

def main():
    # Page title                   
    st.title("Facebook ad Report :bar_chart:")

    # Add sth into sidebar
    text = """
    :arrow_forward: **To start**: \n
    Don't forget to select your favorite filters\n
    ---------------------\n
    `This dashboard is based on a sample of 2 months facebook historical data.`\n
    ---------------------
    """
    st.sidebar.markdown(text)
    st.sidebar.subheader("FILTERS")
    
    # Selectbox : View of the dataframe
    status = st.sidebar.selectbox('Select your favorite KPI view:',["Per country",
                                                            "Per target type",
                                                            "Per day"])
    ## Reporting per country
    if status == "Per country":
        status2 = st.sidebar.radio("Select the prefered currency :",("Local currency","USD"))    
        ## In local currency
        if status2 == "Local currency":
            with st.expander("See the data grouped by country in local currency"):
                st.dataframe((groupby_all('country','currency','local').set_index('country')).style.format(subset=[
                                                        'spend', 'revenue', 'CPA','CPM','CPC', 'ROAS'],
                                                        formatter="{:,.2f}"))  
            st.markdown('---------------------\n')
            ## Country per day
            st.subheader("Let's dive in:")
            col1, col2, col3 = st.columns(3)
            with col1: # Select date
                start_date, end_date = st.date_input('Date range  :',[datetime.date(2021,11,1),datetime.date(2021,11,18)])
            
            
            with col2: # Selectbox country
                df_behaviour_country = groupby_all('country','date','local')
                all_countries = df_behaviour_country['country'].unique().tolist()
                options = st.selectbox('Country:', all_countries)
            
            with col3: # Select KPI
                KPI= ['CPA','revenue','ROAS']
                selected_KPI = st.selectbox("KPI:",KPI)
            
            ind_country = df_behaviour_country[df_behaviour_country['country']== options]
            mask = (ind_country['date'] >= (start_date).strftime('%Y-%m-%d')) & (ind_country['date'] <= (end_date).strftime('%Y-%m-%d'))
            ind_country = ind_country [mask]

            # Create plot
            fig1 = make_subplots(specs=[[{"secondary_y": True}]])
    
            fig1.add_trace(
                    go.Bar(x=ind_country['date'],
                    y=ind_country['spend'],
                    name="Spend"),
                    secondary_y=False,
                )
        
            fig1.add_trace(
                    go.Scatter(x=ind_country['date'],
                    y=ind_country[selected_KPI], name= selected_KPI,
                    line_color='black'),
                    secondary_y=True,
                )

            fig1.update_xaxes(title_text="Days")
        
            fig1.update_yaxes(title_text="Spend", secondary_y=False)
            fig1.update_yaxes(title_text=selected_KPI, secondary_y=True)
            
            st.plotly_chart(fig1)

        ## In USD
        elif status2 == "USD":  
            st.subheader("Per country - USD")
            st.dataframe((groupby_all('country','currency','us').set_index('country')).style.format(subset=[
                                                        'spend', 'revenue', 'CPA','CPM','CPC', 'ROAS'],
                                                        formatter="{:,.2f}"))
            st.markdown('---------------------\n')
            # Metrics highlight

            #col1, col2, col3 = st.columns(3)
            #country = df_country_us[df_country_us['ROAS']==df_country_us['ROAS'].max()].index[0]
            #col1.metric("Top spender", '2', "1.2 °F")
            #col2.metric("Top CPA", "9 mph", "-8%")
            #col3.metric("Top ROAS", "86%", "4%")
        
            ## Country per day
            st.subheader("Let's dive in:")
            
            col1, col2, col3 = st.columns(3)
            with col1: # Select date
                start_date, end_date = st.date_input('Date range:',[datetime.date(2021,11,1),datetime.date(2021,11,18)])
            
            
            with col2: # Selectbox country
                df_behaviour_country = groupby_all('country','date','us')
                all_country = df_behaviour_country['country'].unique().tolist()
                options = st.selectbox('Country:', all_country)
            
            with col3: # Select KPI
                KPI= ['CPA','revenue','ROAS']
                selected_KPI = st.selectbox("KPI:",KPI)
            
            ind_country = df_behaviour_country[df_behaviour_country['country']== options]
            mask = (ind_country['date'] >= (start_date).strftime('%Y-%m-%d')) & (ind_country['date'] <= (end_date).strftime('%Y-%m-%d'))
            ind_country = ind_country[mask]

            # Create plot
            fig2 = make_subplots(specs=[[{"secondary_y": True}]])
    
            fig2.add_trace(
                    go.Bar(x=ind_country['date'],
                    y=ind_country['spend'],
                    name="Spend"),
                    secondary_y=False,
                )
        
            fig2.add_trace(
                    go.Scatter(x=ind_country['date'],
                    y=ind_country[selected_KPI], name= selected_KPI,
                    line_color='black'),
                    secondary_y=True,
                )

            fig2.update_xaxes(title_text="Days")
        
            fig2.update_yaxes(title_text="Spend", secondary_y=False)
            fig2.update_yaxes(title_text=selected_KPI, secondary_y=True)
        
            st.plotly_chart(fig2)

    ## Reporting per target type
    elif status == "Per target type": 
        ## In USD
        st.subheader("Per target type - USD")
        st.dataframe((groupby_all('target type','currency','usd').set_index('target type')).style.format(subset=[
                                                        'spend', 'revenue', 'CPA','CPM','CPC', 'ROAS'],
                                                        formatter="{:,.2f}"))
        st.markdown('---------------------\n')
        # Metrics highlight
        
        ## Target type per day
        st.subheader("Let's dive in:")
            
        col1, col2, col3 = st.columns(3)
        with col1: # Select date
            start_date, end_date = st.date_input('Date range:',[datetime.date(2021,11,1),datetime.date(2021,11,18)])
            
            
        with col2: # Selectbox country
            df_behaviour_target = groupby_all('target type','date','local')
            all_target = df_behaviour_target['target type'].unique().tolist()
            options = st.selectbox('Target type:', all_target)
            
        with col3: # Select KPI
            KPI= ['CPA','revenue','ROAS']
            selected_KPI = st.selectbox("KPI:",KPI)
            
        ind_target = df_behaviour_target[df_behaviour_target['target type']== options]
        mask = (ind_target['date'] >= (start_date).strftime('%Y-%m-%d')) & (ind_target['date'] <= (end_date).strftime('%Y-%m-%d'))
        ind_target = ind_target[mask]

        # Create plot
        fig3 = make_subplots(specs=[[{"secondary_y": True}]])
    
        fig3.add_trace(
                    go.Bar(x=ind_target['date'],
                    y=ind_target['spend'],
                    name="Spend"),
                    secondary_y=False,
                )
        
        fig3.add_trace(
                    go.Scatter(x=ind_target['date'],
                    y=ind_target[selected_KPI], name= selected_KPI,
                    line_color='black'),
                    secondary_y=True,
                )
        
        fig3.update_xaxes(title_text="Days")
        
        fig3.update_yaxes(title_text="Spend", secondary_y=False)
        fig3.update_yaxes(title_text=selected_KPI, secondary_y=True)
        
        st.plotly_chart(fig3)
    
    ## Reporting per day
    elif status == "Per day":
        # In USD
        st.subheader("Per day - USD")
        # Add date selector
        start_date, end_date = st.date_input('Choose your date range  :',[datetime.date(2021,11,1),datetime.date(2021,11,18)])
        df_daily = groupby_all('date','currency','usd')
        mask = (df_daily['date'] >= (start_date).strftime('%Y-%m-%d')) & (df_daily['date'] <= (end_date).strftime('%Y-%m-%d'))
        
        # Display DF
        st.dataframe(df_daily[mask].set_index('date').style.format(subset=[
                                                        'spend', 'revenue', 'CPA','CPM','CPC', 'ROAS'],
                                                        formatter="{:,.2f}"))
 
main()  