import requests
from bs4 import BeautifulSoup
import pandas as pd


class Economic_data:
    def __init__(self, start_date, end_date):
        self.set_dates(start_date, end_date)
        self.currency_links = {'USD': 'R01235', 'CNY': 'R01375', 'EUR': 'R01239', 'GBP': 'R01035'}
        self.names_exchange_rate = {'USD': 'Доллар', 'CNY': 'Китайский юань', 'EUR': 'Евро', 'GBP': 'Фунт стерлингов'}

    def set_dates(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date
        
    def central_bank_rate(self):
        html = requests.get(f'https://cbr.ru/hd_base/KeyRate/?UniDbQuery.Posted=True&UniDbQuery.From={self.start_date}'
                            f'&UniDbQuery.To={self.end_date}').text
        soup = BeautifulSoup(html, 'html.parser')
        tables = str(soup.find_all('table')).split()
        dates = []
        rates = []
        for line in tables:
            if line[:4] == '<td>' and line[-5:] == '</td>':
                if line.find('.') > -1:
                    dates.append(line[4:-5])
                elif line.find(',') > -1:
                    rates.append(line[4:-5])
        return pd.DataFrame({'date': dates, 'rate': rates})

    def inflation_rate(self):
        html = requests.get(f'https://www.cbr.ru/hd_base/infl/?UniDbQuery.Posted=True&UniDbQuery.From={self.start_date}'
                            f'&UniDbQuery.To={self.end_date}').text
        soup = BeautifulSoup(html, 'html.parser')
        tables = str(soup.find_all('table')).split()
        months = []
        infl_pers = []
        print(tables)
        for i in range(len(tables) - 1):
            if tables[i][:4] == '<td>' and tables[i][-5:] == '</td>':
                if tables[i].find('.') > -1:
                    months.append(tables[i][4:-5])
                elif tables[i].find(',') > -1 and not (tables[i] == '<td>4,00</td>' and tables[i + 1] == '</tr>'):
                    infl_pers.append(tables[i][4:-5])
        infl_pers = infl_pers[1::2]
        return pd.DataFrame({'month': months, 'inflation': infl_pers})

    def currency_exchange_rate(self, currency):
        html = requests.get(f'https://www.cbr.ru/currency_base/dynamics/?UniDbQuery.Posted=True&UniDbQuery.so=1&'
                            f'UniDbQuery.mode=1&UniDbQuery.date_req1=&UniDbQuery.date_req2=&UniDbQuery.'
                            f'VAL_NM_RQ={self.currency_links[currency]}&UniDbQuery.From={self.start_date}&'
                            f'UniDbQuery.To={self.end_date}').text
        soup = BeautifulSoup(html, 'html.parser')
        tables = str(soup.find_all('table')).split()
        dates = []
        rates = []
        for line in tables:
            if line[:4] == '<td>' and line[-5:] == '</td>':
                if line.find('.') > -1:
                    dates.append(line[4:-5])
                elif line.find(',') > -1:
                    rates.append(line[4:-5])
        return pd.DataFrame({'date': dates, 'rate': rates})