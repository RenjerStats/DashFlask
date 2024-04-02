import requests
from bs4 import BeautifulSoup

import pandas as pd

first_date = '17.09.2013'
last_date = '02.04.2024'
URL = f'https://www.cbr.ru/hd_base/infl/?UniDbQuery.Posted=True&UniDbQuery.From={first_date}&UniDbQuery.To={last_date}'
html = requests.get(URL).text
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
infl_df = pd.DataFrame({'month': months, 'inflation': infl_pers})
