import requests
from bs4 import BeautifulSoup
import pandas as pd

class Parser(object):
    def __init__(self, path, start_data, end_data):
        self.path = path
        self.start_data = start_data
        self.end_data = end_data
    
    def get_infl(self):
        URL = self.path.replace("start_data", )
        html = requests.get(URL).text
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
    
        




