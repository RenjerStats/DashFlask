import requests
from bs4 import BeautifulSoup

import pandas as pd
from datetime import datetime

import asyncio
import aiohttp
import aiomoex


currency_links = {'USD': 'R01235', 'CNY': 'R01375', 'EUR': 'R01239', 'GBP': 'R01035'}
names_curses = {'USD': 'Доллар', 'CNY': 'Юань', 'EUR': 'Евро', 'GBP': 'Фунт стерлингов'}
companies = ['YNDX', 'SBER', 'TCSG', 'GAZP', 'RNFT', 'ROSN', 'SNGSP', 'NVTK', 'AFKS', 'FIVE', 'MGNT']
names_companies = {'YNDX': 'R01235', 'SBER': 'R01375', 'TCSG': 'R01239', 'GAZP': 'R01035'}
#today_date = datetime.now().date().replace("-", ".")
today_date = "02.03.2024"
start_data = "02.03.2023"


class Economic_data:
    def get_start_date():
        return datetime.strptime(start_data, "%d.%m.%Y").date()
    def get_today_date():
        return datetime.now().date()
    def get_name_curses():
        return names_curses
    def get_name_companies():
        return names_companies
    def get_short_name_curses():
        return list(names_curses.keys())
    def get_short_name_companies():
        return list(names_companies.keys())
    
    def update_central_bank_rate():
        html = requests.get(f'https://cbr.ru/hd_base/KeyRate/?UniDbQuery.Posted=True&UniDbQuery.From=17.09.2013'
                            f'&UniDbQuery.To={today_date}').text
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
        df = pd.DataFrame({'date': dates, 'rate': rates})
        df.to_csv('data/central_bank_rate.csv')

    def select_central_bank_rate(start_date, end_date):
        df = pd.read_csv('data/central_bank_rate.csv')
        return df.iloc[df[df['date'] == start_date].index:df[df['date'] == end_date]]

    def update_inflation_rate():
        html = requests.get(f'https://www.cbr.ru/hd_base/infl/?UniDbQuery.Posted=True&UniDbQuery.From=01.01.2013'
                            f'&UniDbQuery.To={today_date}').text
        soup = BeautifulSoup(html, 'html.parser')
        tables = str(soup.find_all('table')).split()
        months = []
        infl_pers = []
        for i in range(len(tables) - 1):
            if tables[i][:4] == '<td>' and tables[i][-5:] == '</td>':
                if tables[i].find('.') > -1:
                    months.append(tables[i][4:-5])
                elif tables[i].find(',') > -1 and not (tables[i] == '<td>4,00</td>' and tables[i + 1] == '</tr>'):
                    infl_pers.append(tables[i][4:-5])
        infl_pers = infl_pers[1::2]
        df = pd.DataFrame({'month': months, 'inflation': infl_pers})
        df.to_csv('data/inflation_rate.csv')

    def select_inflation_rate(start_date, end_date):
        df = pd.read_csv('data/inflation_rate.csv')
        return df.iloc[df[df['date'] == start_date].index:df[df['date'] == end_date]]

    def update_currency_exchange_rate():
        for curr in currency_links.keys():
            html = requests.get(f'https://www.cbr.ru/currency_base/dynamics/?UniDbQuery.Posted=True&UniDbQuery.so=1&'
                                f'UniDbQuery.mode=1&UniDbQuery.date_req1=&UniDbQuery.date_req2=&UniDbQuery.'
                                f'VAL_NM_RQ={currency_links[curr]}&UniDbQuery.From=01.07.1992&'
                                f'UniDbQuery.To={today_date}').text
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
            df = pd.DataFrame({'date': dates, 'rate': rates})
            df.to_csv(f'data/currency/{curr}_exchange_rate.csv')

    def select_currency_exchange_rate(currency, start_date, end_date):
        df = pd.read_csv(f'data/currency/{currency}_exchange_rate.csv')
        return df.iloc[df[df['date'] == start_date].index:df[df['date'] == end_date]]

    async def update_shares_rate():
        for cmpny in companies:
            async with aiohttp.ClientSession() as session:
                data = await aiomoex.get_board_history(session, cmpny)
                df = pd.DataFrame(data)
                df['rate'] = df.VALUE / df.VOLUME
                df.rename(columns={'TRADEDATE': 'date'}, inplace=True)
                df.drop(['BOARDID', 'CLOSE', 'VOLUME', 'VALUE'], axis=1, inplace=True)
                df.to_csv(f'data/shares/{cmpny} + _shares_rate.csv')

    def select_shares_rate(company, start_date, end_date):
        df = pd.read_csv(f'data/shares/{company}_shares_rate.csv')
        return df.iloc[df[df['date'] == start_date].index:df[df['date'] == end_date]]