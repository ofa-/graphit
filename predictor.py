#!/usr/bin/env python

import pandas as pd
import matplotlib.pyplot as plt

import locale; locale.setlocale(locale.LC_ALL, "fr_FR.UTF8")
import numpy as np

from matplotlib.dates import DateFormatter
from sklearn.linear_model import LinearRegression

from sys import argv

regions = {
        "pc":  [ "Petite Couronne", "92|93|94" ],
        "gc":  [ "Grande Couronne", "77|78|91|95" ],
        "idf": [ "Île de France", "75|91|92|93|94|95|77|78" ],
        "sud": [ "13|30|34|83" ],
        "brg": [ "Bourgogne Franche-Comté", "21|25|39|58|70|71|89|90" ],
        "fc":  [ "Franche-Comté", "25|39|70|90" ],
        "met": [ "Métropole" ],
}

def main():

    data = pd.read_csv('data.csv', sep=";", parse_dates=['jour'])

    metropole = data[~data.dep.str.match("^97")]

    arg = "met" if len(argv) <= 1 else "|".join(argv[1:])

    region = regions[arg][-1] if arg in regions else arg

    selection = metropole if arg == "met" else \
                data[data.dep.str.match(region)]

    sums = selection.groupby('jour').sum()

    data = sums.rolling(7).mean()

    avg_dc = avg_dc_line(region if arg != "met" else arg)

    reg_line, chunks = regressor(data)

    pred, cuts = predictor(data) \
                    if arg == "met" else ([],[])

    plot = data \
            .drop(['incid_hosp', 'incid_rad'], axis=1) \
            .join(reg_line) \
            .join(pred, how='outer')

    with plt.xkcd():
    #if True:
        plot = plot.plot(logy=True)
        show_dbl(plot, reg_line, chunks)
        annotate(plot, pred, cuts)
        avg_dc.plot(linestyle=":", linewidth=.5, color="grey")
        #(data.incid_rea * 5/8).rename('Fouché-fix réa') \
        #        .plot(linestyle="--", linewidth=.7, color="#00D")

        set_opts(plot)
        set_view(plot, arg)
        set_title(plot, arg, double_times(data, chunks[-2:]))

    plt.show()


def regressor(data):
    reg_data = data['incid_rea']

    chunks = [
                [9,14],
                [19,28],
                [30,100],
                [120,140],
                [150,160],
                [172,192],
                [193,206],
                [207,len(data)],
            ]

    reg_line = pd.concat([
        exp_lin_reg(reg_data[range(*chunk)])
            for chunk in chunks ])

    return reg_line, chunks


def predictor(data):
    scaled = 10**0.2 * data['incid_rea'].pow(0.885)

    shifts = [
                [ [0,20], 5 ],
                [ [19,26], 13 ],
                [ [25,40], 15 ],
                [ [40,66], 17 ],
                [ [70,91], 14 ],
                [ [84,136], 27 ],
                [ [135,144], 32 ],
                [ [153,159], 23 ],
                [ [165,172], 17 ],
                [ [172,179], 19 ],
                [ [178,len(scaled)], 26 ],
            ]

    shifted = pd.concat([
        scaled[range(*chunk[0])] .shift(periods=chunk[1], freq='D')
            for chunk in shifts
        ]) \
        .rename('pred')

    return shifted, shifts


def avg_dc_line(region):
    dc_j = pd.read_csv("dc_j.csv")

    sel = dc_j.depdom.str.match(region) if region != "met" else \
         ~dc_j.depdom.str.match("9[7-9]|na")

    dc_j = dc_j[sel].groupby("MDEC").dc_j.sum()

    dates = pd.date_range("2020-03-01", "2021-04-01")
    avg_dc = [ dc_j[month]/10 for month in dates.month ]

    return pd.Series(index=dates, data=avg_dc).rename('dc_j')


def double_times(data, chunks):
    data = data['incid_rea']
    return [ double_time(data[range(*chunk)]) for chunk in chunks ]


def double_time(data):
    # y = ax + b  =>  dy = a dx  =>  dx = 1/a dy
    # y = log(u)  =>  dy = log(u2) - log(u1) = log(u2/u1)
    # u2/u1 = 2   =>  dx = 1/a log(2)

    return np.log(2) / slope(data)


def annotate(plot, shifted, shifts):
    curr = 0
    for shift in shifts:
        chunk, nb_days = shift
        size = len(range(*chunk))
        middle = int(size/2)
        print(chunk, size, nb_days)
        side = shifted[middle+curr] - shifted[curr] < 0
        point = (
            shifted.index[middle+curr],
            shifted[middle+curr]
        )
        _annotate(plot, point, nb_days, side)
        curr += size


def _annotate(plot, point, nb_days, side):
    plot.annotate(
        f'+{nb_days} j ',
        xy=point,
        bbox=dict(boxstyle="round4", fc="w"),
        arrowprops=dict(arrowstyle="-|>", connectionstyle="arc3,rad=-0.2", fc="w"),
        xytext=(
            point[0] + pd.Timedelta(days=3),
            point[1] * (1.2 if side else 1/1.2) # logscale => offset via * or /
        )
    )


def show_dbl(plot, reg_line, chunks):
    size = [ len(range(*chunk)) for chunk in chunks ]
    spots = [ int(size[i]/2) + sum(size[:i]) for i in range(len(size)) ]
    for spot in spots:
        nb_days = double_time(reg_line[spot-1:spot+1])
        point = (reg_line.index[spot], reg_line[spot])
        if abs(nb_days) > 90:
            continue
        plot.annotate(
            f'{abs(round(nb_days))}',
            fontsize="x-small",
            color="green",
            bbox=dict(boxstyle="circle", color="green", alpha=0.2), # fc="white"),
            xy=text_xy(point, nb_days),
        )


def text_xy(point, nb_days):
    a = np.log(2)/nb_days
    d = 1.1
    dy = d/np.sqrt(1 + a**2)
    dx = d/np.sqrt(1 + 1/a**2)
    return (
        point[0] - pd.Timedelta(hours=dx),
        point[1] * (dy if nb_days > 0 else 1/dy)
    )


def set_opts(plot):
    log_scalator = [1,2,3,4,5,7,10,20,30,50,70,100,200,300,500,700]
    int_formatter = lambda x, pos: f'{x:.0f}'
    plot.axes.yaxis.set_minor_locator(plt.FixedLocator(log_scalator))
    plot.axes.yaxis.set_minor_formatter(int_formatter)
    plot.axes.yaxis.set_major_formatter(int_formatter)
    plot.axes.xaxis.set_major_formatter(DateFormatter('\xAF\n%b'))
    plot.axes.set_xlabel(None)
    plot.grid(axis='y', which='both')
    plot.grid(axis='x', which='major')
    plot.axes.tick_params(which='both', right=True, labelright=True)
    plot.axes.tick_params(which='both', axis="y", length=6, width=1)
    plot.axes.set_xticks(plot.axes.get_xticks()[1:-1])

    plot.legend(["admis. réa / j", "nouv. dc / j"], fontsize="small")
    plot.figure.set(figwidth=6, figheight=6)
    plot.figure.subplots_adjust(bottom=0.16)




def set_view(plot, arg):
    td = pd.Timedelta
    now = pd.to_datetime("now")

    #plot.set(xlim=("2020-03-20", now+td(days=15)), ylim=(4.2, 900))   # full story
    #plot.set(xlim=("2020-09-07", "2020-10-20"), ylim=(16, 190))  # 1 month + predictor / 2w
    #plot.set(xlim=("2020-09-14", "2020-10-12"), ylim=(16, 190))  # 1 month = 4 weeks
    #plot.set(xlim=("2020-09-08", "2020-10-08"), ylim=(0.6, 12))  # 3 weeks, low volumes (dept.)
    #plot.set(xlim=("2020-07-14", "2020-10-12"), ylim=(8, 180))   # 3 months
    #plot.set(xlim=("2020-07-27", "2020-10-30"), ylim=(6.5, 190))   # 3 months
    #plot.set(xlim=(now-td(days=25), now+td(days=4)), ylim=(9, 190))   # 3 weeks, to date

    plot.set(xlim=(now-td(days=28), now+td(days=1)), ylim=(0.8, 24))

    if arg == "idf":
        plot.set(ylim=(8, 240)) # keep scale (x10 vs other dept.)

    if arg == "met":
        plot.set( xlim=(now-td(days=25), now+td(days=10)), # 10 days predictor
                    ylim=(8, 240))


def exp_lin_reg(reg_data):
    line, slope = _exp_lin_reg(reg_data)
    return line

def slope(reg_data):
    line, slope = _exp_lin_reg(reg_data)
    return slope


def _exp_lin_reg(reg_data):
    X = reg_data.index.values.reshape(-1,1)
    Y = reg_data.mask(reg_data == 0).apply(np.log)

    reg = LinearRegression()
    reg.fit(X, Y.fillna(0))

    reg_line = reg.predict(X.astype('float64'))
    slope = reg_line[1]-reg_line[0]

    return pd.Series(index=Y.index, data=reg_line) \
                .rename('reg') \
                .apply(np.exp) \
            , slope


def pop_info_string(arg):
    region = regions[arg][-1] if arg in regions else arg

    metropole = dep[~dep.NUMÉRO.str.match("97")].POPULATION.sum()
    pop_region = dep[dep.NUMÉRO.str.match(region)].POPULATION.sum()

    return "" if arg == "met" else \
            "({:.0f}% de la population)".format(pop_region/metropole*100.)


def set_title(plot, arg, dbl_time):
    if arg in regions:
        region = regions[arg][0]
    elif "|" in arg:
        region = arg
    else:
        region = dep[dep.NUMÉRO == arg].NOM.values[0]

    region = region.replace("|", " ")

    pop_info = pop_info_string(arg)

    dbl_t_prev = pretty_time(dbl_time[0])
    dbl_t_curr = pretty_time(dbl_time[1])

    title = f"{region} {pop_info}"
    title += f"\nréa x2 : {dbl_t_prev} –> {dbl_t_curr}"

    plot.set_title(title, pad=20, fontsize="small")


def pretty_time(val):
    return f"_" if abs(val) > 90 else f"{val:.0f} j"


def init():
    from os import path, system
    if not path.exists("data.csv"):
        system("fetch.sh")


init()

dep = pd.read_csv("dep.csv", sep="\t")

main()
