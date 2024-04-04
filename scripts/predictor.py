import os
import datetime
from datetime import date
from datetime import datetime
from datetime import timedelta

import pandas as pd
from prophet import Prophet
from prophet.serialize import model_to_json, model_from_json

from CONST import MODELS_PATHS, PREDICTIONS_PATHS

delta = timedelta(days=1)
today_date = str(date.today() + delta)


def train_models():
    if not os.path.exists('../models'):
        os.mkdir("../models")
    if not os.path.exists('../predictions'):
        os.mkdir("../predictions")
    for filepath in MODELS_PATHS.keys():
        data = pd.read_csv(filepath)
        data['date'] = data['date'].apply(lambda x: x[6:] + x[2:6] + x[:2])
        data['date'] = pd.to_datetime(data['date'])
        data.rename({'date': 'ds', 'rate': 'y'}, axis=1, inplace=True)
        model = Prophet()
        model.fit(data)
        with open(MODELS_PATHS[filepath], 'w') as file:
            file.write(model_to_json(model))
        print(MODELS_PATHS[filepath][10:-5] + ' saved')


def make_predictions(count):
    for path in MODELS_PATHS.values():
        date = datetime.strptime(today_date, '%Y-%m-%d')
        dates = [date]
        for i in range(count):
            date += delta
            dates.append(date)
        df = pd.DataFrame({'ds': dates, 'y': [0] * len(dates)})
        with open(path, 'r') as file:
            model = model_from_json(file.read())
            predict = model.predict(df)
            predict = predict[['ds', 'yhat']]
            predict = predict.iloc[::-1].reset_index(drop=True)
            if os.path.exists(PREDICTIONS_PATHS[path]):
                os.remove(PREDICTIONS_PATHS[path])
            predict.rename({'ds': 'date', 'y': 'rate'}, axis=1, inplace=True)
            predict.to_csv(PREDICTIONS_PATHS[path])


def update_predictions():
    for path in PREDICTIONS_PATHS.values():
        df = pd.read_csv(path)
        index = df.index[df['date'] == today_date].tolist()
        if not index:
            make_predictions(365)
            return
        else:
            df = df.iloc[:index[0]+1]
            os.remove(path)
            df.to_csv(path)


def one_day_prediction(model_name, date):
    df = pd.DataFrame({'ds': [datetime.strptime(date, '%d-%m-%Y')], 'y': [0]})
    with open(f'../models/{model_name}r_model.json', 'r') as file:
        model = model_from_json(file.read())
        predict = model.predict(df)
        return predict.yhat.to_list()[0]

