import requests
from bs4 import BeautifulSoup

import pandas as pd

first_date = '17.09.2013'
last_date = '02.04.2024'
URL = f'https://cbr.ru/hd_base/KeyRate/?UniDbQuery.Posted=True&UniDbQuery.From={first_date}&UniDbQuery.To={last_date}'


