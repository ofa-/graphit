#!/usr/bin/env python

import pandas as pd
import matplotlib.pyplot as plt

import locale; locale.setlocale(locale.LC_ALL, "fr_FR.UTF8")
import numpy as np

from matplotlib.ticker import ScalarFormatter
from sklearn.linear_model import LinearRegression


def main():

    data = pd.read_csv('data.csv', sep=";", parse_dates=['jour'])

    metropole = data[~data.dep.str.match("^97")]

    sums = metropole.groupby('jour').sum()

    data = sums.rolling(7).mean()

    reg_data = data['incid_rea'].tail(21)
    reg_line = exp_lin_reg(reg_data)

    #with plt.xkcd():
    if True:
        plot = data \
                .drop(['incid_hosp', 'incid_rad'], axis=1) \
                .plot(logy=True)

        plot_opt(plot)

    plt.subplots_adjust(bottom=0.16)
    plt.show()


def plot_opt(plot):
    plot.axes.yaxis.set_minor_formatter(ScalarFormatter())
    plot.axes.yaxis.set_minor_formatter(lambda x, pos: f'{x:.0f}')
    plot.axes.yaxis.set_major_formatter(lambda x, pos: f'{x:.0f}')
    plot.grid(axis='y', which='both')
    plot.grid(axis='x', which='major')


def exp_lin_reg(reg_data):
    X = reg_data.index.values.reshape(-1,1)
    Y = reg_data.apply(np.log)

    reg = LinearRegression()
    reg.fit(X, Y)

    reg_line = reg.predict(X.astype('float64'))

    return pd.Series(index=Y.index, data=reg_line) \
                .rename('reg') \
                .apply(np.exp)


main()
