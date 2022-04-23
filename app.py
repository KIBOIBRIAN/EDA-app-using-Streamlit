from ast import If
from cProfile import label
from logging.config import fileConfig
import numpy as np
import pandas as pd 
import matplotlib.pyplot as plt
import streamlit as st
import io
import sqlite3


# Upload CSV data
st.sidebar.info('Upload dataset to analyze')
with st.sidebar.info('1. Upload your CSV data'):
    uploaded_file = st.file_uploader("Upload  CSV files:", accept_multiple_files=True)
# project header
st.header('Data Analysis tool')
# Condition 'if' there a csv is uploaded or not
# Load a csv and define it as df
if uploaded_file is not None:
    # st.info('Awaiting for CSV files to be uploaded.')
    
    # read files uploaded
    for file in uploaded_file:
        file.seek(0)
        uploaded_data_read = [pd.read_csv(file) for file in uploaded_file]
        length=len(uploaded_data_read)

        for i in range(length):
            if i==0:
                df1=pd.DataFrame(uploaded_data_read[i])
                
                
            elif i==1:
                df2=pd.DataFrame(uploaded_data_read[i])
                
            else:
                df3=pd.DataFrame(uploaded_data_read[i])
              
        df3=df3.rename(columns={'ident':'airport_ident'})
        df=pd.merge(df3,df1,on='airport_ident')        
   
        st.header('Clean the Dataset')
        # Rename and merge
        st.info('Rename the ident column on airports dataset and merge with the airport frequencies dataset')
        if st.button('Rename & Merge'):
            st.write('Shape of the merged dataset:',df.shape)
            st.write(df.head())
       
        # Display dataset info
        st.info('View the dataset non null values size and data types:')
        if st.button('Dataset Info'):
            buffer = io.StringIO()
            df.info(buf=buffer)
            s = buffer.getvalue()   
            st.text(s)
        # Drop all data with 'tye' is 'closed'
        st.info('Drop data with type is closed' )
        if st.button('Drop type:closed'):
            df=df[df['type_x']!='closed']
            st.write('New data shape:', df.shape)
        # fill null values
        st.info('Fill in the missing values:')
        if st.button("Fill null values"):
            df.fillna('',inplace=True)
            st.write(df.head())    
        # Database
        st.info('Back up you cleaned file')
        if st.button('To database'):
            conn=sqlite3.connect('data_project')
            c=conn.cursor()
            c.execute('CREATE TABLE IF NOT EXISTS airports (id_x, airport_ident, type_x, name, latitude_deg,longitude_deg, elevation_ft, continent, iso_country,iso_region, municipality, scheduled_service, gps_code, iata_code, local_code, home_link, wikipedia_link, keywords,id_y, airport_ref, type_y, description, frequency_mhz, large_airport, medium_airport, small_airport, large_airport_fq_mhz, medium_airport_fq_mhz, small_airport_fq_mhz)')
            conn.commit()
            df.to_sql('airports', conn, if_exists='replace', index = False)
       
        # Download Backup files, csv,json and xml
        st.info('Backup files:')
        if st.button('Download backup files'):
            st.write('Download backup files in the following formats:')
            @st.cache 
            def convert_csv(df):
                return df.to_csv()
            @st.cache
            def convert_json(df):
            # IMPORTANT: Cache the conversion to prevent computation on every rerun
                return df.to_json().encode('utf-8')
            @st.cache
            def to_xml(df):
                def row_xml(row):
                    xml = ['<item>']
                    for i, col_name in enumerate(row.index):
                        xml.append('  <{0}>{1}</{0}>'.format(col_name, row.iloc[i]))
                        xml.append('</item>')
                        return '\n'.join(xml)
                res = '\n'.join(df.apply(row_xml, axis=1))
                return(res)
            csv=convert_csv(df)
            json = convert_json(df)
            xml= to_xml(df)
            st.download_button(
                label='Download data to csv',
                data=csv,
                file_name='data.csv',
                mime='text/csv'
            )
            st.download_button(
                label="Download data to Json",
                data=json,
                file_name='data.json',
                mime='text/json',
            )
            st.download_button(
                label="Download data to XML",
                data =xml,
                file_name="data.xml",
                mime='text/json'
            )
        st.header('Data manipulation')
        # Columns for all uk airports
        st.info('Create columns for UK(GB) airports that are large airports,medium airports, small airports')
        df['large_airport']=df['type_x'].apply(lambda x: 'large_airport' if x == 'large_airport' else ' ' )
        df['medium_airport']=df['type_x'].apply(lambda x: 'medium_airport' if x == 'medium_airport' else ' ' )
        df['small_airport']=df['type_x'].apply(lambda x: 'small_airport' if x == 'small_airport' else ' ' )
        if st.button('Create columns'):
            st.write('Columns has been created!')
        st.info('join each category, large_airport, medium_airport, small airportto the communication frequencies ‘ frequency_mhz’ that the airport uses for communication')
        
        def f(row):
            if row['type_x']==row['large_airport']:
                value=row['frequency_mhz']
            else:
                value=''
            return value
        df['large_airport_fq_mhz']=df.apply(f, axis=1)
        def z(row):
            if row['type_x']==row['medium_airport']:
                value_m=row['frequency_mhz']
            else:
                value_m=''
            return value_m
        df['medium_airport_fq_mhz']=df.apply(z, axis=1)
        def w(row):
            if row['type_x']==row['small_airport']:
                value_s=row['frequency_mhz']
            else:
                value_s=''
            return value_s
        df['small_airport_fq_mhz']=df.apply(w, axis=1)
        if st.button('Airport frequencies'):
            st.write('Frequencies of each type has been created in new columns')
            st.write(df.head())
        st.info('Mean, median and mode of the frequency for the large airport')
        df['large_airport_fq_mhz']=pd.to_numeric(df['large_airport_fq_mhz'])
        df['medium_airport_fq_mhz']=pd.to_numeric(df['medium_airport_fq_mhz'])
        df['small_airport_fq_mhz']=pd.to_numeric(df['small_airport_fq_mhz'])
        if st.button('Mean,Mode, Median'):
            mean=df['large_airport_fq_mhz'].mean()
            st.write("The mean of large airports frequency is", mean)
            mode=df['large_airport_fq_mhz'].mode()[0]
            st.write("The mode of large airports frequency is", mode)
            median=df['large_airport_fq_mhz'].median()
            st.write("The median of large airports frequency is", median)

        st.info('Mean, mode, median for frequencies large than 100mhz')
        if st.button('Mean, Mode, Median'):
            df1_df3_100=df[df['frequency_mhz'] > 100]
            mean_100=df1_df3_100['frequency_mhz'].mean()
            st.write("The mean of large airports frequency is",mean_100)
            mode_100=df1_df3_100['large_airport_fq_mhz'].mode()[0]
            st.write("The mode of large airports frequency is", mode_100)
            median_100=df1_df3_100['large_airport_fq_mhz'].median()
            st.write("The median of large airports frequency is",median_100)
        st.info('Plot to display the communication frequencies used by ‘small_airport’')
        if st.button('Plot'):
            df1_df3_small=df[df['type_x']=='small_airport']
            plt.figure(figsize=(15,6))
            plt.scatter(df1_df3_small.iso_region,df1_df3_small.frequency_mhz)
            plt.xlabel('Iso region')
            plt.ylabel('Frequency_mhz')
            plt.title('Frequencies used by ‘small_airport’')
            st.pyplot(fig=plt) 
        st.info('Correlation')
        if st.button('Correlation'):
            st.write(df.corr().style.background_gradient(cmap="Blues"))
            

    else:
       
        st.sidebar.info('Use previously saved dataset in the database.')
        if st.sidebar.button('Retrieve from database'):
            conn=sqlite3.connect('data_project')
            c=conn.cursor()
            c.execute(''' SELECT * FROM airports''')
            df = pd.DataFrame(c.fetchall(), columns=['id_x', 'airport_ident', 'type_x', 'name', 'latitude_deg',
            'longitude_deg', 'elevation_ft', 'continent', 'iso_country',
            'iso_region', 'municipality', 'scheduled_service', 'gps_code',
            'iata_code', 'local_code', 'home_link', 'wikipedia_link', 'keywords',
            'id_y', 'airport_ref', 'type_y', 'description', 'frequency_mhz',
            'large_airport', 'medium_airport', 'small_airport',
            'large_airport_fq_mhz', 'medium_airport_fq_mhz',
            'small_airport_fq_mhz'])
            df.set_index('index',inplace=True)
            df.fillna('',inplace=True)
            st.write (df.head())
    # retrieve
   
    # if st.button('Press to use Example Dataset'):
    #     # Example data
    #     @st.cache
    #     def load_data():
    #         a = pd.DataFrame(np.random.rand(100, 5),columns=['a', 'b', 'c', 'd', 'e'])
    #         return a
    #     df = load_data()
    #     st.write(df)
        
