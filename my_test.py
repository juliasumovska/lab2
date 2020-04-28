from spyre import server
from bs4 import BeautifulSoup
import pandas as pd
import json
import requests
import re
import os

provinces = {1: "Cherkasy", 2: "Chernihiv",3: "Chernivtsi", 4: "Crimea",5: "Dnipropetrovs'k",6: "Donets'k",7: "Ivano-Frankivs'k",8: "Kharkiv",
             9: "Kherson",10: "Khmel'nyts'kyy",11: "Kiev",12: "Kiev City",13: "Kirovohrad",14: "Luhans'k",15: "L'viv",16: "Mykolayiv",
             17: "Odessa",18: "Poltava",19: "Rivne",20: "Sevastopol'",21: "Sumy",22: "Ternopil'",23: "Transcarpathia",24: "Vinnytsya",
             25: "Volyn",26: "Zaporizhzhya",27: "Zhytomyr"}


class WebApp(server.App):
    title = "Analys"

    inputs = [
        {
            "type": 'dropdown',
            "label": 'Take a TS',
            "options": [{"label": "VCI", "value": "VCI"},
                        {"label": "TCI", "value": "TCI"},
                        {"label": "VHI", "value": "VHI"}],
            "key": 'TS',
            "action_id": "update_data"
        },
        {
            "type": 'dropdown',
            "label": 'Take a province',
            "options": [{"label": name, "value": id} for id, name in provinces.items()],
            "key": 'Province',
            "action_id": "update_data"
        },
        {
            "type": 'dropdown',
            "label": 'From year',
            "options": [{"label": i,"value": i} for i in range(1981,2021)],
            "key": 'from_year',
            "action_id": "update_data",
        },
        {
            "type": 'dropdown',
            "label": 'To year',
            "options": [{"label": i, "value": i} for i in range(1982, 2021)],
            "key": 'to_year',
            "action_id": "update_data",
        },
        {
            "type": 'text',
            "label": 'To week',
            "value": '0',
            "key": 'to_week',
            "action_id": "update_data",
        },
        {
            "type": 'text',
            "label": 'To next week',
            "value": '52',
            "key": 'to_next',
            "action_id": "update_data",
        }
    ]

    controls = [{"type": "hidden",
                 "id": "update_data"}]

    tabs = ["Plot", "Table"]

    outputs = [{"type": "plot",
                "id": "plot",
                "control_id": "update_data",
                "tab": "Plot"},

               {"type": "table",
                "id": "table_id",
                "control_id": "update_data",
                "tab": "Table",
                "on_page_load": True}]

    def getData(self, params):
        provinceID = params['Province']
        from_year = params['from_year']
        to_year = params['to_year']
        week_form = params['to_week']
        week_too = params['to_next']
        api_url = "https://www.star.nesdis.noaa.gov/smcd/emb/vci/VH/get_TS_admin.php?country=UKR&provinceID={}&year1={}&year2={}&type=Mean".format(
            provinceID, from_year, to_year)
        vhiUrl = str(BeautifulSoup(requests.get(api_url).content.decode("utf8"),'html.parser').find('pre').contents[0])
        normData = []
        data = vhiUrl.split('\n')

        for j in range(len(data)):
            data[j] = re.sub(',', ' ', data[j])
            data[j] = data[j].split(' ')
            data[j] = list(filter(lambda x: x != '', data[j]))
            data[j].insert(2, provinceID)
            data[j][0:3] = list(map(int, data[j][0:3]))
            data[j][3:] = list(map(float, data[j][3:]))
            normData.append(data[j])
        df = pd.DataFrame(normData, columns=['Year', 'Week', 'ProvinceID', 'SMN', 'SMT', 'VCI', 'TCI', 'VHI'])
        df = df[~df.isin([-1])]
        df = df.dropna()
        return df.loc[(df['Week'] >= float(week_form)) & (df['Week'] <= float(week_too))]



    def getPlot(self, params):
        datatype = params['TS']
        df = self.getData(params)
        plt_obj = df.plot(x='Week', y=datatype)
        plt_obj.set_ylabel(datatype)
        fig = plt_obj.get_figure()
        return fig


app = WebApp()
app.launch(port=8005)