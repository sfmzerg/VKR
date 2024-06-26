# -*- coding: utf-8 -*-
"""Копия блокнота "Копия блокнота "Untitled22.ipynb""

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1X_Elcx3rjfvg8ldDvcYcJstHNxSBxWOL
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sb
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn import metrics
from sklearn.svm import SVC
from xgboost import XGBRegressor
from sklearn.linear_model import LinearRegression, Lasso, Ridge
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error as mae

import warnings
warnings.filterwarnings('ignore')

!pip install pyodbc

df = pd.read_csv('SBER.csv')
display(df.head())
display(df.tail())

df.describe()

parts = df["<DATE>"].astype('str')
df["year"]= parts[0]
df["month"]= parts[1]
df["day"]= parts[2]
df.head()

parts = df["<DATE>"].astype('str')
for n in range(0,5508):
  df["year"][n]= parts[n][:4]
  df["month"][n]= parts[n+1][4:6]
  df["day"][n]= parts[n+2][6:]
df.head()

#определяем, был ли в этот день праздник
from datetime import date
import holidays

def is_holiday(x):

  india_holidays = holidays.country_holidays('IN')

  if india_holidays.get(x):
    return 1
  else:
    return 0

df['holidays'] = df['<DATE>'].apply(is_holiday)
df.head()

df['m1'] = np.sin(df['month'].astype('int') * (2 * np.pi / 12))
df['m2'] = np.cos(df['month'].astype('int') * (2 * np.pi / 12))
for n in range (0,5508):
  df["month"][n]= parts[n][4:6]
df.head()

df.drop('<DATE>', axis=1, inplace=True)

df['<HIGH>'].nunique(), df['<VOL>'].nunique()

#постоение диаграмм
features = ['<OPEN>','<CLOSE>', 'year', 'month',
            '<HIGH>','<LOW>']

plt.subplots(figsize=(20, 10))
for i, col in enumerate(features):
    plt.subplot(2, 3, i + 1)
    df.groupby(col).mean()['<VOL>'].plot.bar()
plt.show()

#постоение диаграммы наивысшей стоимости по месяцам
plt.figure(figsize=(10,5))
df.groupby('month').mean()['<HIGH>'].plot()
plt.show()

#построение графика данных и его скользащего среднего
plt.figure(figsize=(15, 10))
window_size = 30
data = df[df['year']=='2008']
windows = data['<VOL>'].rolling(window_size)
sma = windows.mean()
sma = sma[window_size - 1:]

data['<VOL>'].plot()
sma.plot()
plt.legend()
plt.show()

#строем гистограмму и ящик с усами для наибольшей и наименьшей стоимости
plt.subplots(figsize=(12, 5))
plt.subplot(1, 2, 1)
sb.distplot(df['<HIGH>'])

plt.subplot(1, 2, 2)
sb.boxplot(df['<LOW>'])
plt.show()

#постоение тепловой карты
plt.figure(figsize=(10, 10))
sb.heatmap(df.corr() > 0.8,
           annot=True,
           cbar=False)
plt.show()

df = df[df['<HIGH>']<140]

#разделяем переменные на данные обучения и тестирования
features = df.drop(['<HIGH>', 'year'], axis=1)
target = df['<HIGH>'].values


X_train, X_val, Y_train, Y_val = train_test_split(features, target,
                                                  test_size = 0.05,
                                                  random_state=22)
X_train.shape, X_val.shape

#нормализуем функцию для стабильного и быстрого обучения
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_val = scaler.transform(X_val)

models = [LinearRegression(), XGBRegressor(), Lasso(), Ridge()]

for i in range(4):
    models[i].fit(X_train, Y_train)

    print(f'{models[i]} : ')

    train_preds = models[i].predict(X_train)
    print('Training Error : ', mae(Y_train, train_preds))

    val_preds = models[i].predict(X_val)
    print('Validation Error : ', mae(Y_val, val_preds))
    print()