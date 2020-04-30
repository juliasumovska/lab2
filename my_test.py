from spyre import server
from bs4 import BeautifulSoup
from sep import get_url
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
            "type": 'checkboxgroup',
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
            "options": [{"label": i,"value": i} for i in range(1982,2021)],
            "key": 'from_year',
            "action_id": "refresh",
        },
        {
            "type": 'dropdown',
            "label": 'To year',
            "options": [{"label": i, "value": i} for i in range(1983, 2021)],
            "key": 'to_year',
            "action_id": "refresh",
        },
        {
            "type": 'text',
            "label": 'To week',
            "value": '0',
            "key": 'to_week',
            "action_id": "refresh",
        },
        {
            "type": 'text',
            "label": 'To next week',
            "value": '52',
            "key": 'to_next',
            "action_id": "refresh",
        }
    ]

    controls = [{"type": "hidden",
                 "id": "update_data"}]

    tabs = ["Plot", "Table","Plot2","Table2"]

    outputs = [{"type": "plot",
                "id": "getPlot_whole",
                "control_id": "update_data",
                "tab": "Plot"},
               {"type": "plot",
                "id": "getPlot_grouped",
                "control_id": "update_data",
                "tab": "Plot2"},
               {"type": "table",
                "id": "getData_whole",
                "control_id": "update_data",
                "tab": "Table",
                "on_page_load": True},
               {"type": "table",
                "id": "getData_grouped",
                "control_id": "update_data",
                "tab": "Table2",
                "on_page_load": True},
               ]

    def getData_whole(self, params):

        provinceID = int(params['Province'])
        from_year = int(params['from_year'])
        to_year = int(params['to_year'])
        week_form = int(params['to_week'])
        week_too = int(params['to_next'])
        df = get_url(provinceID,from_year,to_year,week_form,week_too)
        return df

    def getPlot_whole(self, params):
        datatype = params['TS']
        df = self.getData_whole(params)
        plt_obj = df.plot(x='Week', y=datatype)
        plt_obj.set_ylabel(datatype)
        fig = plt_obj.get_figure()
        return fig

    def getData_grouped(self,params):
        provinceID = int(params['Province'])
        from_year = int(params['from_year'])
        to_year = int(params['to_year'])
        week_form = int(params['to_week'])
        week_too = int(params['to_next'])
        df2 = get_url(provinceID,from_year,to_year,week_form,week_too)
        return df2[['Year','VHI']].groupby(['Year']).agg(['max','min']).reset_index()


    def getPlot_grouped(self, params):
        datatype = params['TS']
        df = self.getData_grouped(params)

        plt_obj = df.plot(x='Year',
                          linestyle='-',
                          linewidth=3

                          )


        fig = plt_obj.get_figure()
        return fig




app = WebApp()
app.launch(port=8009)