import os
import requests
from bs4 import BeautifulSoup

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import calendar

import aiohttp
import aiomoex

currency_links = {'USD': 'R01235', 'CNY': 'R01375', 'EUR': 'R01239', 'GBP': 'R01035'}
companies = ['YNDX', 'SBER', 'TCSG', 'GAZP', 'RNFT', 'ROSN', 'SNGSP', 'NVTK', 'AFKS', 'FIVE', 'MGNT']
names_curses = {'USD': 'Доллар', 'CNY': 'Юань', 'EUR': 'Евро', 'GBP': 'Фунт стерлингов'}
names_companies = {'YNDX':'Яндекс', 'SBER':'Сбер', 'TCSG':'Тинькофф', 'GAZP':'Газпром', 'RNFT':'РуссНефть', 'ROSN':'Роснефть', 'SNGSP':'Сургутнефтегаз', 'NVTK':'Новатэк', 'AFKS':'АФК «Система»', 'FIVE':'X5 Retail Group', 'MGNT':'Магнит'}
today_date = str(datetime.now().date().strftime('%d-%m-%Y'))
delta = timedelta(days=1)
start_data = "01.01.2023"

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
        df['date'] = [datetime.strptime(d, '%d-%m-%Y').date().strftime('%Y-%m-%d') for d in df['date'].to_list()]
        df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
        return df.iloc[::-1].reset_index(drop=True)

    def update_inflation_rate():
        if os.path.exists('./data/inflation_rate.csv'):
            os.remove('./data/inflation_rate.csv')
        html = requests.get(f'https://www.cbr.ru/hd_base/infl/?UniDbQuery.Posted=True&UniDbQuery.From=01.01.2013'
                            f'&UniDbQuery.To={today_date.replace("-", ".")}').text
        soup = BeautifulSoup(html, 'html.parser')
        tables = str(soup.find_all('table')).split()
        dates = []
        infl_pers = []
        for i in range(len(tables)):
            if tables[i][:4] == '<td>' and tables[i][-5:] == '</td>':
                if tables[i].find('.') > -1:
                    month = tables[i][4:6]
                    year = tables[i][7:-5]
                    first_day, second_day = calendar.monthrange(int(year), int(month))
                    for i in range(first_day, second_day + 1):
                        if i == 0: continue
                        if i < 10:
                            dates.append(f'0{i}-{month}-{year}')
                        else:
                            dates.append(f'{i}-{month}-{year}')
                elif tables[i].find(',') > -1 and not (tables[i] == '<td>4,00</td>' and tables[i + 1] == '</tr>') \
                        and i % 2 == 1:
                    infl_pers.extend([float(tables[i][4:-5].replace(',', '.'))] * (len(dates) - len(infl_pers)))
        df = pd.DataFrame({'date': dates, 'rate': infl_pers}).sort_values('date')
        df.to_csv('data/inflation_rate.csv')

    def select_inflation_rate(start_date, end_date):
        df = pd.read_csv('data/inflation_rate.csv')
        df['date'] = [datetime.strptime(d, '%d-%m-%Y').date().strftime('%Y-%m-%d') for d in df['date'].to_list()]
        df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
        return df.iloc[::-1].reset_index(drop=True)

    def update_currency_exchange_rate():
        for curr in currency_links.keys():
            if os.path.exists(f'./data/currency/{curr}_exchange_rate.csv'):
                old_df = pd.read_csv(f'./data/currency/{curr}_exchange_rate.csv')
                start_date = old_df.iloc[[0]].date.tolist()[0]
                if start_date == today_date:
                    return
                first_run = False
            else:
                print('update ' + curr + ' exchange rate')
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
                        fixed_data.append([date, line['CLOSE']])
                        last_date = datetime.strptime(date, '%d-%m-%Y')
                    else:
                        date = datetime.strptime(line['TRADEDATE'], '%Y-%m-%d')
                        while last_date < date:
                            last_date += delta
                            fixed_data.append([str(last_date.strftime('%d-%m-%Y')), line['CLOSE']])
                        last_date = date
                df = pd.DataFrame(fixed_data, columns=['date', 'rate'])
                if os.path.exists(f'./data/shares/{cmpny}_shares_rate.csv'):
                    os.remove(f'./data/shares/{cmpny}_shares_rate.csv')
                df.to_csv(f'data/shares/{cmpny}_shares_rate.csv')

    def select_currency_exchange_rate(currency, start_date, end_date):
        df = pd.read_csv(f'data/currency/{currency}_exchange_rate.csv')
        df['date'] = [datetime.strptime(d, '%d-%m-%Y').date().strftime('%Y-%m-%d') for d in df['date'].to_list()]
        df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
        return df.iloc[::-1].reset_index(drop=True)
    
    def select_shares_rate_percent(company, start_date, end_date):
        df = pd.read_csv(f'data/shares/{company}_shares_rate.csv')
        df['date'] = [datetime.strptime(d, '%d-%m-%Y').date().strftime('%Y-%m-%d') for d in df['date'].to_list()]
        df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
        
        x = df['rate'].to_list()
        x = np.diff(x) / x[:-1] * 100
        df = df.iloc [1: , :]
        df['rate'] = x
        
        df['color'] = df['rate'].apply(lambda x: 'green' if x >= 0 else 'crimson')
        return df

    def select_shares_rate(company, start_date, end_date):
        df = pd.read_csv(f'data/shares/{company}_shares_rate.csv')
        df['date'] = [datetime.strptime(d, '%d-%m-%Y').date().strftime('%Y-%m-%d') for d in df['date'].to_list()]
        df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
        return df
    
    def convert_date(date):
        
        return datetime.strptime(date, '%Y-%m-%d').strftime('%d-%m-%Y')
    