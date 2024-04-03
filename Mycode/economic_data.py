import os
import requests
from bs4 import BeautifulSoup

import pandas as pd
from datetime import datetime
from datetime import timedelta

import aiohttp
import aiomoex

currency_links = {'USD': 'R01235', 'CNY': 'R01375', 'EUR': 'R01239', 'GBP': 'R01035'}
companies = ['YNDX', 'SBER', 'TCSG', 'GAZP', 'RNFT', 'ROSN', 'SNGSP', 'NVTK', 'AFKS', 'FIVE', 'MGNT']
names_curses = {'USD': 'Доллар', 'CNY': 'Юань', 'EUR': 'Евро', 'GBP': 'Фунт стерлингов'}
names_companies = {'YNDX':'Яндекс', 'SBER':'Сбер', 'TCSG':'Тинькофф', 'GAZP':'Газпром', 'RNFT':'РуссНефть', 'YNDX':'Роснефть', 'SNGSP':'Сургутнефтегаз', 'NVTK':'Новатэк', 'AFKS':'АФК «Система»', 'FIVE':'X5 Retail Group', 'MGNT':'Магнит'}
today_date = str(datetime.now().date().strftime('%d-%m-%Y'))
delta = timedelta(days=1)
start_data = "02.03.2023"

class Economic_data:
    def create_dir():     
        if not os.path.exists('./data'):
            os.mkdir("./data")
        if not os.path.exists('./data/currency'):
            os.mkdir("./data/currency")
        if not os.path.exists('./data/shares'):
            os.mkdir("./data/shares")

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
        if os.path.exists('./data/central_bank_rate.csv'):
            old_df = pd.read_csv('./data/central_bank_rate.csv')
            start_date = old_df.iloc[[0]].date.tolist()[0]
            if start_date == today_date:
                return
            first_run = False
        else:
            start_date = '17.09.2013'
            first_run = True
        html = requests.get(f'https://cbr.ru/hd_base/KeyRate/?UniDbQuery.Posted=True&UniDbQuery.From={start_date}'
                            f'&UniDbQuery.To={today_date.replace("-", ".")}').text
        soup = BeautifulSoup(html, 'html.parser')
        tables = str(soup.find_all('table')).split()
        dates = []
        rates = []
        last_date = ''
        for line in tables:
            if line[:4] == '<td>' and line[-5:] == '</td>':
                if line.find('.') > -1:
                    if last_date != '':
                        date = datetime.strptime(line[4:-5].replace('.', '-'), '%d-%m-%Y')
                        while last_date > date:
                            last_date -= delta
                            dates.append(str(last_date.strftime('%d-%m-%Y')))
                        last_date = date
                    else:
                        date = line[4:-5].replace('.', '-')
                        dates.append(date)
                        last_date = datetime.strptime(date, '%d-%m-%Y')
                elif line.find(',') > -1:
                    rate = float(line[4:-5].replace(',', '.'))
                    rates.extend([rate] * (len(dates) - len(rates)))
        df = pd.DataFrame({'date': dates, 'rate': rates})
        if not first_run:
            df = pd.concat([df, old_df])
            os.remove('./data/central_bank_rate.csv')
        df.to_csv('./data/central_bank_rate.csv')

    def select_central_bank_rate(start_date, end_date):
        df = pd.read_csv('data/central_bank_rate.csv')
        return df.iloc[df.index[df['date'] == end_date].tolist()[0]:df.index[df['date'] == start_date].tolist()[0] + 1]

    def update_inflation_rate():
        html = requests.get(f'https://www.cbr.ru/hd_base/infl/?UniDbQuery.Posted=True&UniDbQuery.From=01.01.2013'
                            f'&UniDbQuery.To={today_date.replace("-", ".")}').text
        soup = BeautifulSoup(html, 'html.parser')
        tables = str(soup.find_all('table')).split()
        months = []
        infl_pers = []
        for i in range(len(tables) - 1):
            if tables[i][:4] == '<td>' and tables[i][-5:] == '</td>':
                if tables[i].find('.') > -1:
                    months.append(tables[i][4:-5].replace(".", "-"))
                elif tables[i].find(',') > -1 and not (tables[i] == '<td>4,00</td>' and tables[i + 1] == '</tr>'):
                    infl_pers.append(float(tables[i][4:-5].replace(',', '.')))
        infl_pers = infl_pers[1::2]
        df = pd.DataFrame({'month': months, 'inflation': infl_pers})
        df.to_csv('data/inflation_rate.csv')

    def select_inflation_rate(start_month, end_month):
        df = pd.read_csv('data/inflation_rate.csv')
        return df.iloc[df.index[df['month'] == end_month].tolist()[0]:df.index[df['month'] == start_month].tolist()[0] + 1]

    def update_currency_exchange_rate():
        for curr in currency_links.keys():
            print('update ' + curr + ' exchange rate')
            if os.path.exists(f'./data/currency/{curr}_exchange_rate.csv'):
                old_df = pd.read_csv(f'./data/currency/{curr}_exchange_rate.csv')
                start_date = old_df.iloc[[0]].date.tolist()[0]
                if start_date == today_date:
                    return
                first_run = False
            else:
                start_date = '01.01.2000'
                first_run = True
            html = requests.get(f'https://www.cbr.ru/currency_base/dynamics/?UniDbQuery.Posted=True&UniDbQuery.so=1&'
                                f'UniDbQuery.mode=1&UniDbQuery.date_req1=&UniDbQuery.date_req2=&UniDbQuery.'
                                f'VAL_NM_RQ={currency_links[curr]}&UniDbQuery.From=01.01.2000&'
                                f'UniDbQuery.To={today_date}').text
            soup = BeautifulSoup(html, 'html.parser')
            tables = str(soup.find_all('table')).split()
            dates = []
            rates = []
            last_date = ''
            for line in tables:
                if line[:4] == '<td>' and line[-5:] == '</td>':
                    if line.find('.') > -1:
                        if last_date != '':
                            date = datetime.strptime(line[4:-5].replace('.', '-'), '%d-%m-%Y')
                            while last_date > date:
                                last_date -= delta
                                dates.append(str(last_date.strftime('%d-%m-%Y')))
                            last_date = date
                        else:
                            date = line[4:-5].replace('.', '-')
                            dates.append(date)
                            last_date = datetime.strptime(date, '%d-%m-%Y')
                    elif line.find(',') > -1:
                        rate = float(line[4:-5].replace(',', '.'))
                        rates.extend([rate] * (len(dates) - len(rates)))
            df = pd.DataFrame({'date': dates, 'rate': rates})
            if not first_run:
                df = pd.concat([df, old_df])
                os.remove(f'./data/currency/{curr}_exchange_rate.csv')
            df.to_csv(f'./data/currency/{curr}_exchange_rate.csv')
    
    async def update_shares_rate():
        for cmpny in companies:
            print('update ' + cmpny + ' shares rate')
            async with aiohttp.ClientSession() as session:
                data = list(await aiomoex.get_board_history(session, cmpny))
                fixed_data = []
                last_date = ''
                for line in data:
                    if last_date == '':
                        date = datetime.strptime(line['TRADEDATE'], '%Y-%m-%d').strftime('%d-%m-%Y')
                        fixed_data.append([date, line['VOLUME'], line['VALUE']])
                        last_date = datetime.strptime(date, '%d-%m-%Y')
                    else:
                        date = datetime.strptime(line['TRADEDATE'], '%Y-%m-%d')
                        while last_date < date:
                            last_date += delta
                            fixed_data.append([str(last_date.strftime('%d-%m-%Y')), line['VOLUME'], line['VALUE']])
                        last_date = date
                df = pd.DataFrame(fixed_data, columns=['date', 'volume', 'value'])
                df['rate'] = df.value / df.volume
                df.drop(['volume', 'value'], axis=1, inplace=True)
                if os.path.exists(f'./data/shares/{cmpny}_shares_rate.csv'):
                    os.remove(f'./data/shares/{cmpny}_shares_rate.csv')
                df.to_csv(f'data/shares/{cmpny}_shares_rate.csv')

    def select_currency_exchange_rate(currency, start_date, end_date):
        df = pd.read_csv(f'data/currency/{currency}_exchange_rate.csv')
        return df.iloc[df.index[df['date'] == end_date].tolist()[0]:df.index[df['date'] == start_date].tolist()[0] + 1]

    def select_shares_rate(company, start_date, end_date):
        df = pd.read_csv(f'data/shares/{company}_shares_rate.csv')
        return df.iloc[df.index[df['date'] == start_date].tolist()[0]:df.index[df['date'] == end_date].tolist()[0] + 1]
    
    def convert_date(date):
        return datetime.strptime(date, '%Y-%m-%d').strftime('%d-%m-%Y')
    