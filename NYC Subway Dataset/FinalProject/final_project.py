from pandas import *
from ggplot import *
import numpy as np
import pandas as pd
import statsmodels.api as sm


def linear_regression(features, values):
    features = sm.add_constant(features)
    model = sm.OLS(values, features)
    results = model.fit()
    params = results.params[1:]
    intercept = results.params[0]
    # print(params)
    return intercept, params

def predictions(dataframe):
    features = dataframe[['hour', 'wspdi', 'rain', 'weekday', 'fog', 'pressurei', 'meantempi', 'precipi']]
    dummy_units = pandas.get_dummies(dataframe['UNIT'], prefix = 'unit')
    features = features.join(dummy_units)
    # Values
    values = dataframe['ENTRIESn_hourly']

    # Perform linear regression
    intercept, params = linear_regression(features, values)
    
    predictions = intercept + np.dot(features, params)
    return predictions

def compute_r_squared(data, predictions):
    
    # your code here
    num = 0
    for i, y in data.iteritems():
        num += (y - predictions[i]) * (y - predictions[i])
    
    mean = np.mean(data)
    den = 0
    for i, y in data.iteritems():
        den += (y - mean) * (y - mean)
    
    r_squared = 1 - (num / den)
    
    return r_squared
    
def plot_weather_data(turnstile_weather):
    
    pandas.options.mode.chained_assignment = None

    df = turnstile_weather[['UNIT', 'Hour', 'ENTRIESn_hourly']]
    df['Num'] = df['UNIT'].apply(lambda s: int(s[1:]))
    
    grouped = df.groupby('Hour')
    df1 = grouped.agg({'ENTRIESn_hourly' : np.sum}).reset_index()
    plot = ggplot(df1, aes('Hour', 'ENTRIESn_hourly')) + geom_histogram(stat='bar') + ggtitle('Ridership By Hour')
    return plot

def plot_weather_data_2(turnstile_weather):
    
    pandas.options.mode.chained_assignment = None
    df = turnstile_weather[['UNIT', 'ENTRIESn_hourly', 'rain']]
    df['Num'] = df['UNIT'].apply(lambda s: int(s[1:]))
    
    grouped = df.groupby(['Num', 'rain'])
    df1 = grouped.agg({'ENTRIESn_hourly' : np.sum}).reset_index()
    
    plot = ggplot(df1, aes('Num', 'ENTRIESn_hourly', color = 'rain')) + geom_point() + geom_line() + ggtitle('Ridership Wihout Rain vs With Rain')
    
    # plot = # your code here
    return plot
    
df = pd.read_csv("turnstile_weather.csv")
pred = predictions(df)
r_2 = compute_r_squared(pd.Series(df['ENTRIESn_hourly'].values), pred)
print(r_2)
plot_weather_data(df)
plot_weather_data_2(df)
