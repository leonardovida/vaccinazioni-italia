import pandas as pd
import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt
from datetime import timedelta
from statsmodels.tsa.arima.model import ARIMA
import arrow


def clean_dataset(df):
    # Select relevant data
    df = df[["prima_dose", "Data"]]  # prima_dose = first time vaccinated

    # Rename columns and format
    df.rename(
        columns={"Data": "date"}, inplace=True)
    df['date'] = pd.to_datetime(df['date'])

    return df


def split_dataset(df):
    # Create date to split dataset
    cutoff_date = df['date'].max() - timedelta(days=35)

    # Eliminate older weeks
    df = df[df['date'] >= cutoff_date]

    # Change index
    df.set_index("date", inplace=True)

    return df


# create a differenced series
def difference(df, interval=1):
    """Create a differenced series on week."""
    diff = list()
    for i in range(interval, len(df)):
        value = df[i] - df[i - interval]
        diff.append(value)
    return np.array(diff)


def inverse_difference(history, yhat, interval=1):
    """Put back the seasonality inside."""
    return yhat + history[-interval]


def arima_forecast(df):
    """Arima forecast."""
    # Difference the data per week
    days_in_week = 7
    X = df.values
    #differenced = difference(X, days_in_week)
    differenced = X
    model = ARIMA(differenced, order=(7, 1, 1))  # history
    # fit the model
    model_fit = model.fit()
    # make forecast
    now = arrow.utcnow()
    today = now.format('YYYY-MM-DD')
    future = now.shift(months=+3).format('YYYY-MM-DD')
    start_index = today
    end_index = future
    forecast = model_fit.predict(
        start=1, end=90)

    list_results = []
    [list_results.append(int(x)) for x in forecast]
    return pd.DataFrame(list_results)
