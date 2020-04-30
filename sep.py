import requests
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
import re
import datetime
import os
import matplotlib.pyplot as plt

param = {'TS': [], 'Province': '1', 'from_year': '1981', 'to_year': '1982', 'to_week': '0', 'to_next': '52', 'output_id': 'plot'}


def get_url(province,from_year, to_year,from_week,to_week):


     if not os.path.isfile('ukraine_df.csv'):
        array_of_df = []
        for oblast in range(1, 28):
            api_url = "https://www.star.nesdis.noaa.gov/smcd/emb/vci/VH/get_TS_admin.php?country=UKR&provinceID={}&year1=1981&year2=2020&type=Mean".format(oblast)
            vhiUrl = str(
                BeautifulSoup(requests.get(api_url).content.decode("utf8"), 'html.parser').find('pre').contents[0])
            normData = []
            data = vhiUrl.split('\n')

            for j in range(len(data)):
                data[j] = re.sub(',', ' ', data[j])
                data[j] = data[j].split(' ')
                data[j] = list(filter(lambda x: x != '', data[j]))
                data[j].insert(2, oblast)
                data[j][0:3] = list(map(int, data[j][0:3]))
                data[j][3:] = list(map(float, data[j][3:]))
                normData.append(data[j])
            df = pd.DataFrame(normData, columns=['Year', 'Week', 'ProvinceID', 'SMN', 'SMT', 'VCI', 'TCI', 'VHI'])


            df = df[~df.isin([-1])]
            df = df.dropna()
            df.Week = df.Week.astype('int64')
            df.ProvinceID = df.ProvinceID.astype('int64')
            array_of_df.append(df)

        main_df = pd.concat(array_of_df)
        main_df.to_csv('ukraine_df.csv')
        return main_df.loc[
            (main_df['ProvinceID'] == province) & (main_df['Year'] >= from_year) & (main_df['Year'] <= to_year) & (
            main_df['Week'] >= from_week) & (main_df['Week'] <= to_week)]

     else:
         main_df = pd.read_csv('ukraine_df.csv',index_col=0)
         return main_df.loc[(main_df['ProvinceID'] == province) & (main_df['Year'] >= from_year) & (main_df['Year'] <= to_year) & (main_df['Week'] >= from_week) & (main_df['Week'] <= to_week)]












# def get_url(from_year,to_year):
#     if not os.path.isfile('ukraine_df.csv'):
#         array_of_df = []
#         for oblast in range(1,28):
#             api_url = "https://www.star.nesdis.noaa.gov/smcd/emb/vci/VH/get_TS_admin.php?country=UKR&provinceID={}&year1={}&year2={}&type=Mean".format(
#                 oblast, from_year, to_year)
#             vhiUrl = str(BeautifulSoup(requests.get(api_url).content.decode("utf8"), 'html.parser').find('pre').contents[0])
#             normData = []
#             data = vhiUrl.split('\n')
#
#             for j in range(len(data)):
#                 data[j] = re.sub(',', ' ', data[j])
#                 data[j] = data[j].split(' ')
#                 data[j] = list(filter(lambda x: x != '', data[j]))
#                 data[j].insert(2, oblast)
#                 data[j][0:3] = list(map(int, data[j][0:3]))
#                 data[j][3:] = list(map(float, data[j][3:]))
#                 normData.append(data[j])
#             df = pd.DataFrame(normData, columns=['Year', 'Week', 'ProvinceID', 'SMN', 'SMT', 'VCI', 'TCI', 'VHI'])
#             df = df[~df.isin([-1])]
#             df = df.dropna()
#             array_of_df.append(df)
#         main_df = pd.concat(array_of_df)
#         main_df.to_csv('ukraine_df.csv')
#     else:
#         df = pd.read_csv('ukraine_df.csv')
#
#         return df


df = get_url(11,1981,2020,1,7)
df = df[['Year','VHI']].groupby(['Year']).agg(['max','min']).reset_index()
print(df)
plt.plot(df['Year'], df['VHI'])
plt.show()