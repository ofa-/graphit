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

    reg_line = regressor(data)

    pred, cuts = predictor(data)

    #with plt.xkcd():
    if True:
        plot = data \
                .drop(['incid_hosp', 'incid_rad'], axis=1) \
                .join(reg_line) \
                .join(pred, how='outer') \
                .plot(logy=True)

        plot_opt(plot)

    plt.subplots_adjust(bottom=0.16)
    plt.show()


def regressor(data):
    reg_data = data['incid_rea']

    return exp_lin_reg(reg_data[200-7:]) \
            .append(exp_lin_reg(reg_data[200-28:200-8])) \
            .append(exp_lin_reg(reg_data[200-50:200-40])) \
            .append(exp_lin_reg(reg_data[200-80:200-60])) \


def predictor(data):
    scaled = 10**0.2 * data['incid_rea'].pow(0.885).rename('pred')

    shifts = [ 19 ]
    nb_days = 19
    shifted = scaled.shift(periods=nb_days, freq='D') \
                .mask(data.index < "2020-09-07")

    return shifted, shifts


def double_time(data):
    # y = ax + b  =>  dy = a dx  =>  dx = 1/a dy
    # y = log(u)  =>  dy = log(u2) - log(u1) = log(u2/u1)
    # u2/u1 = 2   =>  dx = 1/a log(2)

    return np.log(2) / slope(data)


def annotate(plot, shifted, shifts):
    nb_days = shifts[0]
    plot.annotate(
        '+%d j ' % nb_days,
        xy=(shifted.index[-10], shifted[-10]),
        bbox=dict(boxstyle="round4", fc="w"),
        arrowprops=dict(arrowstyle="-|>", connectionstyle="arc3,rad=-0.2", fc="w"),
        xytext=(shifted.index[-18], shifted[-10]+12))


def plot_opt(plot):
    log_scalator = [0,5,10,20,40,80,100,160,200,400,800]
    int_formatter = lambda x, pos: f'{x:.0f}'
    plot.axes.yaxis.set_minor_locator(plt.FixedLocator(log_scalator))
    plot.axes.yaxis.set_minor_formatter(int_formatter)
    plot.axes.yaxis.set_major_formatter(int_formatter)
    plot.axes.set_xlabel(None)
    plot.grid(axis='y', which='both')
    plot.grid(axis='x', which='major')
    plot.axes.tick_params(which='both', right=True, labelright=True)
    plot.axes.tick_params(which='both', axis="y", length=6, width=1)


def exp_lin_reg(reg_data):
    line, slope = _exp_lin_reg(reg_data)
    return line

def slope(reg_data):
    line, slope = _exp_lin_reg(reg_data)
    return slope


def _exp_lin_reg(reg_data):
    X = reg_data.index.values.reshape(-1,1)
    Y = reg_data.apply(np.log)

    reg = LinearRegression()
    reg.fit(X, Y)

    reg_line = reg.predict(X.astype('float64'))
    slope = reg_line[1]-reg_line[0]

    return pd.Series(index=Y.index, data=reg_line) \
                .rename('reg') \
                .apply(np.exp) \
            , slope


main()
