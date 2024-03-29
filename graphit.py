#!/usr/bin/env python3

import pandas as pd
import matplotlib.pyplot as plt

import locale; locale.setlocale(locale.LC_ALL, "fr_FR.UTF8")
import numpy as np

from matplotlib.dates import DateFormatter, MonthLocator
from matplotlib import patheffects

from sklearn.linear_model import LinearRegression


regions = {
        "pc":  [ "Petite Couronne", "92|93|94" ],
        "gc":  [ "Grande Couronne", "77|78|91|95" ],
        "idf": [ "Île de France", "75|91|92|93|94|95|77|78" ],
	"paca": [ "Provence-Alpes-Côte d'Azur", "04|05|06|13|83|84" ],
        "sud": [ "13|30|34|83|06|2A|2B" ],
        "ra":  [ "Rhône-Alpes", "01|07|26|38|42|69|73|74" ],
        "auv": [ "Auvergne", "03|15|43|63" ],
        "ara": [ "Auvergne Rhône-Alpes", "69|38|01|26|73|74|03|07|15|42|43|63" ],
        "bfc": [ "Bourgogne Franche-Comté", "21|25|39|58|70|71|89|90" ],
        "fc":  [ "Franche-Comté", "25|39|70|90" ],
        "ge":  [ "Grand Est", "08|10|51|52|54|55|57|67|68|88" ],
        "brz": [ "Bretagne", "22|29|35|56" ],
        "met": [ "Métropole", "met" ],
}

def main():

    data = pd.read_csv('data.csv', sep=";", parse_dates=['jour'])

    metropole = data[~data.dep.str.match("^97")]

    arg = "|".join(opt.arg)

    region = regions[arg][-1] if arg in regions else arg

    selection = metropole if arg == "met" else \
                data[data.dep.str.match(region)]

    sums = selection.groupby('jour').sum()

    data = sums.rolling(7, center=True).mean() \
    #            .rolling(3, win_type="hamming").mean()

    dc_ref, dc_noise = avg_dc_line(region)
    reg_line, reg_rea_chunks = reg_rea(data)
    pred, cuts = predictor(data)
    reg_dc_line, reg_dc_chunks = reg_dc(data)

    pred_dc = mk_pred(data.incid_dc, reg_dc_chunks[-1])
    pred_rea = mk_pred(data.incid_rea, reg_rea_chunks[-1])

    incid = data[["incid_rea", "incid_dc"]]
    if opt.round:
        incid = incid.round()

    incid = incid \
            .join(reg_line) \
            .join(reg_dc_line) \
            .join(pred, how='outer')

    if not opt.pred:
        incid['pred'] = None
        pred = cuts = []

#    # xkcd style ignores alpha spec on lines ? draw them outside
#    with plt.style.context(opt.style) if opt.style else plt.xkcd():
#        plot = incid.plot(logy=True, y=["incid_rea", "incid_dc"])
#
#    def plot_alpha(data, color):
#        data.plot(alpha=0.5, linewidth=2, color=color)
#    plot_alpha(incid.reg, "darkgreen")
#    plot_alpha(incid.pred, "darkred") if len(pred) else None
#
#    with plt.style.context(opt.style) if opt.style else plt.xkcd():
#

    with plt.style.context(opt.style) if opt.style else plt.xkcd():
        plot = incid.plot(logy=opt.log_scale)
        show_dbl(plot, reg_line, reg_rea_chunks, color="green")
        show_dbl(plot, reg_dc_line, reg_dc_chunks, color="red")
        annotate(plot, pred, cuts)

        if opt.ref_dc:
            avg_dc = plot_avg_dc(plot, dc_ref, opt.ref_dc)
        if opt.round:
            dc_noise = dc_noise.round()
        if opt.noise:
            dc_noise.plot(linestyle=":", linewidth=.5, color="grey", zorder=0)

        if opt.fouché:
            (data.incid_rea * 5/8).rename('Fouché-fix réa') \
                    .plot(linestyle="--", linewidth=.7, color="#00D")

        if True:
            pred_dc.plot(linestyle=":", linewidth=.9, color="red")
            pred_rea.plot(linestyle=":", linewidth=.9, color="green")

        if opt.hills:
            plot_hills(plot, sums.incid_dc, color="orange", zorder=-1)
        else:
            plot_bars(plot, sums.incid_dc, alpha=.04, color="orange", zorder=-1)

        if opt.réa:
            #sums.incid_rea.plot(marker=".", ms=3, ls="", alpha=.1, color="blue")
            plot_bars(plot, sums.incid_rea, alpha=.04, color="blue", zorder=-1)

        if opt.week:
            plot_weekly_avg(sums.incid_dc, alpha=.5, color="#D0D", zorder=-1)

        set_opts(plot, arg)
        set_view(plot, arg, gap = cuts[-1][1] if cuts else 0)
        set_title(plot, arg, double_times(data, reg_rea_chunks[-2:]))

        x = pd.Timestamp(plot.axes.get_xlim()[0], unit="D")
        add_note(plot, x, avg_dc, f"{opt.ref_dc}%") \
                if opt.ref_dc else None
        add_note(plot, x, dc_noise, f"bruit") \
                if opt.noise else None

        if opt.proj_val:
            add_yaxis_note(plot, pred_dc, 'red')
            add_yaxis_note(plot, pred_rea, 'green')

        plot.figure.savefig(arg + ("-full" if opt.full else ""))


def add_yaxis_note(plot, data, color):
    import matplotlib.dates as mdates
    x = min(plot.axes.get_xlim()[1], mdates.date2num(data.index[-1]))

    x = pd.Timestamp(x, unit="D")
    y = data[str(x.date())]
    point = [x, y]
    text = round(y)
    offset = 15
    side = (y - data[x - pd.Timedelta(days=1)]) > 0
    plot.annotate(
        text,
        xy=point,
        fontsize="x-small",
        bbox=dict(boxstyle="round4", fc="w", color=color),
        arrowprops=dict(arrowstyle="-|>", lw=.7,
            connectionstyle="arc3,rad="+("-" if side else "+")+"0.2", fc="w"),
        xytext=(
            point[0] - pd.Timedelta(days=3),
            point[1] + (offset if side else -offset) # logscale => offset via * or /
        )
    )


def fill(line, **kwargs):
        line.plot(linestyle="-", **kwargs) \
        .axes.fill_between(line.index, line, 0.1, **kwargs)


def add_note(plot, x, data, text, side=True):
    plot.annotate(text, color="#AAA", size="x-small",
                    xy=(x+pd.Timedelta(days=1), data[x]))


def plot_bars(plot, data, **kwargs):
    for width in [1, .3]:
        plot.bar(data.index, data, sketch_params=0, width=width, **kwargs)


def plot_hills(plot, data, **kwargs):
        # light => alpha area: .05, markers: .25
        fill(data,  alpha=.1, **kwargs)
        data.plot  (alpha=.3, **kwargs, marker="+", linestyle="")


def plot_avg_dc(plot, dc_ref, dc_percent):
        avg_dc = dc_ref * dc_percent
        if opt.round:
            avg_dc = avg_dc.round()
        avg_dc.plot(linestyle=":", linewidth=.5, color="grey", zorder=0)
        return avg_dc


def plot_weekly_avg(data, **kwargs):
    before_thu = data.index[-1].weekday() < 3
    data = complement_week_from_last_one(data)
    w_avg = data.groupby(pd.Grouper(freq='W')) \
            .mean() \
            .round() \
            .shift(freq='W', periods=1) \
            [:-1 if before_thu else None]
    w_avg.plot(drawstyle='steps', linewidth=.5, **kwargs)


def complement_week_from_last_one(data):
    curr = data.index[-1].weekday()
    size = 6 - curr # weekday: 0 = Mon, 6 = Sun
    return data.append(
            data[-(curr+size+1):-(curr+1)] \
                .shift(freq='D', periods=7))


def reg_rea(data):
    chunks = [
                [9,14],
                [19,28],
                [30,100],
                [120,140],
                [150,160],
                [172,192],
                [193,206],
                [207,215],
                [216,229],
                [230,237],
                [245,256],
                [262,269],
                [270,279],
                [281,293],
                [295,302],
                [303,310],
                [311,317],
                [321,331],
                [333,341],
                [342,355],
                [357,365],
                [366,382],
                [385,403],
                [404,421],
                [422,470],
                [477,507],
                [509,522],
                [523,541],
                [542,567],
                [568,580],
                [582,604],
                [605,631],
                [633,653],
                [654,662],
                [663,672],
                [673,679],
                [680,688],
                [689,702],
                [703,710],
                [711,719],
                [722,730],
               #[731,737],
                [738,746],
                [747,752],
                [753,758],
               #[759,768],
               #[770,
                [773,779],
                [780,799],
                [811,825],
                [826,846],
                [847,854],
                [857,896],
                [910,920],
                [921,930],
                [938,945],
                [946,968],
                [969,976],
                [978,1000],
                [1004,1024],
                [1025,1044],
                [1052,
                len(data)],
            ]

    return mk_reg(data.incid_rea, chunks)


def mk_reg(reg_data, chunks):
    chunks = fix_indexes_for_centered_window(chunks)

    reg_line = pd.concat([
        exp_lin_reg(reg_data[range(*chunk)])
            for chunk in chunks ]) \
        .rename(reg_data.name + ".reg")

    return reg_line, chunks


def reg_dc(data):
    chunks = [
            [6,6+9],
            [33,33+14],
            [61,61+51],
            [203,203+28],
            [250,250+8],
            [263,263+6],
            [270,270+8],
            [282,282+5],
            [288,288+5],
            [295,295+5],
            [302,302+10],
            [313,313+8],
            [323,323+8],
            [332,332+12],
            [345,345+5],
            [351,351+24],
            [378,378+30],
            [409,486],
            [487,520],
            [521,539],
            [540,572],
            [573,591],
            [602,633],
            [634,659],
            [660,672],
            [673,679],
            [680,690],
            [693,704],
            [706,715],
            [716,723],
        #    [724,733],
        #   #[734,741],
        #    [741,748],
            [724,749],
            [750,758],
        #    [758,770],
            [773,785],
            [786,800],
            [811,837],
            [838,855],
            [857,909],
            [911,929],
            [930,944],
            [950,973],
            [981,992],
            [994,1002],
            [1009,1024],
            [1025,1035],
            [1036,1058],
            [1059,
            len(data)],
        ]

    return mk_reg(data.incid_dc, chunks)


def predictor(data):
    scaled = 10**0.2 * data['incid_rea'].pow(0.885)
    scale2 = 10**0.31 * data['incid_rea'].pow(0.885)

    shifts = [
                [ [3,20], 5 ],
                [ [19,26], 13 ],
                [ [25,40], 15 ],
                [ [40,66], 17 ],
                [ [70,91], 14 ],
                [ [84,136], 27 ],
                [ [135,144], 32 ],
                [ [153,159], 23 ],
                [ [165,172], 17 ],
                [ [172,179], 19 ],
                [ [178,185], 26 ],
                [ [207,213], 8 ],
                [ [219,225], 4 ],
                [ [230,231], 0 ],
                [ [238,245], 6 ],
                [ [252,253], 0 ],
                #[ [246,len(scaled)], 10 ],
            ]

    shifts = [ [ [x[0][0]-3, x[0][1]-3], x[1] ] for x in shifts ]

    shifted = pd.concat(
        shift(scaled, shifts[0:14]) +
        shift(scale2, shifts[14:])
        ) \
        .rename('pred')

    return shifted, shifts


def shift(scaled, shifts):
    return [
        scaled[range(*chunk[0])] .shift(periods=chunk[1], freq='D')
        for chunk in shifts
    ]


def fix_indexes_for_centered_window(chunks):
    # centered 7-day window => shift index -3 days
    return [ [x[0]-3, x[1]-3] for x in chunks ]


def avg_dc_line(region):
    dc_j = pd.read_csv("dc_j.csv")

    sel = dc_j.depdom.str.match(region) if region != "met" else \
         ~dc_j.depdom.str.match("9[7-9]|na")

    dc_ = dc_j[sel].groupby(['ADEC', 'MDEC', 'JDEC']).dc_j.sum()
    dc  = dc_[2018].append(dc_[2019])
    avg = dc.groupby('MDEC').mean()
    std = dc.groupby('MDEC').std()

    dates = pd.date_range("2020-03-01", "2024-04-01")
    avg_dc = [ avg[month]/100 for month in dates.month ]
    noise =  [ std[month] for month in dates.month ]

    return pd.Series(index=dates, data=avg_dc).rename('dc_j'), \
           pd.Series(index=dates, data=noise).rename('dc_noise')


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
        _annotate(plot, point, nb_days, side) if size > 1 else None
        curr += size


def _annotate(plot, point, nb_days, side):
    plot.annotate(
        f'+{nb_days} j ',
        xy=point,
        bbox=dict(boxstyle="round4", fc="w"),
        arrowprops=dict(arrowstyle="-|>",
            connectionstyle="arc3,rad="+("" if side else "-")+"0.2", fc="w"),
        xytext=(
            point[0] + pd.Timedelta(days=3),
            point[1] * (1.2 if side else 1/1.2) # logscale => offset via * or /
        )
    )


def show_dbl(plot, reg_line, chunks, color="green", above=False):
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
            color=color,
            bbox=dict(boxstyle="circle", color=color, alpha=.2),
            xy=text_xy(point, nb_days, above),
            path_effects=[
                patheffects.withStroke(linewidth=4, foreground="w"),
            ]
        )


def text_xy(point, nb_days, above):
    a = np.log(2)/nb_days
    d = 1.1 if nb_days > 0 or above else 1.2
    dy = d/np.sqrt(1 + a**2)
    dx = d/np.sqrt(1 + 1/a**2)
    return (
        point[0] - pd.Timedelta(hours=dx),
        point[1] * (dy if nb_days > 0 else 1/dy)
    )


def set_opts(plot, arg):
    log_scalator = [1,2,3,4,5,7,10,20,30,50,70,100,200,300,500,900,1500]
    lin_scalator = [1,5,10,20,30,50,100,200,300,500,900,1500]
    if arg == "met": lin_scalator = lin_scalator[5:]
    scalator = log_scalator if opt.log_scale else lin_scalator
    int_formatter = lambda x, pos: f'{x:.0f}'
    plot.axes.yaxis.set_minor_locator(plt.FixedLocator(scalator))
    plot.axes.yaxis.set_major_locator(plt.FixedLocator(scalator))
    plot.axes.yaxis.set_minor_formatter(int_formatter)
    plot.axes.yaxis.set_major_formatter(int_formatter)
    plot.axes.xaxis.set_major_locator(MonthLocator())
    plot.axes.xaxis.set_major_formatter(DateFormatter('\xAF\n%b'))
    plot.axes.set_xlabel(None)
    plot.axes.tick_params(which='both', right=True, labelright=True)
    plot.axes.tick_params(which='both', axis="y", length=6, width=1)
    plot.axes.set_xticks(plot.axes.get_xticks()[:-1])

    plot.legend(["admis. réa / j", "nouv. dc / j"], fontsize="small")
    plot.figure.set(figwidth=6, figheight=6)
    plot.figure.subplots_adjust(bottom=.12, left=.11, right=.89, top=.85)


def set_view(plot, arg, gap):
    td = pd.Timedelta
    now = pd.to_datetime("now")
    date = pd.to_datetime
    gap = 2 if gap < 2 else gap

    if opt.episode_1:
        now = date("2020-03-22") + td(days=64 if opt.two_months else 35)

    proj_gap = opt.proj-5
    plot.set(xlim=(now-td(days=35-proj_gap), now+td(days=proj_gap)))
    zoom_1_50_adaptive(plot, arg)


    if arg == "met" and opt.pred: # add room for predictor, keep xscale 35d
        plot.set( xlim=(now-td(days=35-gap), now+td(days=gap)))

    if opt.two_months:
        last_2_months = (now-td(days=62), now+td(days=2))
        plot.figure.set(figwidth=8, figheight=6)
        plot.set(xlim=last_2_months)

    if opt.zoom_1_100:
        zoom_1_100(plot, arg)

    if opt.zoom:
        plot.set(ylim=(0, opt.zoom))

    if opt.full:
        fig_xsize = 12 * ( (now - date("2020-03-20")).days /
            (date("2020-10-20") - date("2020-03-20")).days )
        margin_left = .05
        plot.figure.set(figwidth=fig_xsize, figheight=6)
        plot.set(xlim=("2020-03-20", now+td(days=gap)))
        plot.figure.subplots_adjust(left=margin_left, right=1-margin_left)
        zoom_full_adaptive(plot, arg)


def zoom_full_adaptive(plot, arg):
    yscale = pd.Series(
            [0.8, 64] if opt.log_scale else
            [0, 32])

    factor = 30 if arg == "met" else \
              7 if arg == "idf" else \
              4 if arg in regions else \
              1

    plot.set(ylim=(yscale * factor).values)


def zoom_1_10_adaptive(plot, arg):
    yscale = pd.Series(
            [0.4, 16] if opt.log_scale else
            [0, 8])

    factor = 21 if arg == "met" else \
              8 if arg == "idf" else \
              4 if arg in regions else \
              1

    plot.set(ylim=(yscale * factor).values)


def zoom_1_50_adaptive(plot, arg):
    yscale = pd.Series(
            [0.8, 64] if opt.log_scale else
            [0, 32])

    factor = 30 if arg == "met" else \
              4 if arg == "idf" else \
              2 if arg in regions else \
              1

    plot.set(ylim=(yscale * factor).values)


def zoom_1_100(plot, arg):
    yscale = pd.Series(
            [0.8, 128] if opt.log_scale else
            [0, 64])

    factor = 7.15 if arg == "met" else \
             1

    plot.set(ylim=(yscale * factor).values)


def mk_pred(data, chunk):
    line, slope = _exp_lin_reg(data[range(*chunk)])
    return line[-opt.proj-1:]


def exp_lin_reg(reg_data):
    line, slope = _exp_lin_reg(reg_data)
    return line[:-opt.proj]

def slope(reg_data):
    line, slope = _exp_lin_reg(reg_data)
    return slope if slope != 0 else 10**-9


def _exp_lin_reg(reg_data):
    X = reg_data.index.values.reshape(-1,1)
    Y = reg_data.mask(reg_data == 0).apply(np.log)

    reg = LinearRegression()
    reg.fit(X, Y.fillna(0))

    pred_chunk = pd.date_range(
            reg_data.index.values[-1], freq='D', periods=opt.proj+1)[1:]

    index = reg_data.index.append(pred_chunk)

    reg_line = reg.predict(index.values.reshape(-1,1).astype('float64'))
    slope = reg_line[1]-reg_line[0]

    return pd.Series(index=index, data=reg_line) \
                .rename('reg') \
                .apply(np.exp) \
            , slope


def pop_info(arg):
    region = regions[arg][-1] if arg in regions else arg

    metropole = dep[~dep.NUMÉRO.str.match("97")].POPULATION.sum()
    pop_region = dep[dep.NUMÉRO.str.match(region)].POPULATION.sum()

    return pop_region / metropole


def pop_info_string(arg):
    return "" if arg == "met" else \
            "({:.0f}% de la population)".format(pop_info(arg)*100)


def set_title(plot, arg, dbl_time):
    if arg in regions:
        region = regions[arg][0]
    elif "|" in arg:
        region = arg
    else:
        region = dep[dep.NUMÉRO == arg].NOM.values[0]

    region = region.replace("|", " ")

    pop_info = pop_info_string(arg)
    rea_x2_time = rea_time_change_string(dbl_time)

    title = f"{region} {pop_info}"
    title += f"\n{rea_x2_time}" \
                if not opt.episode_1 else "\n(Épisode 1)"

    plot.set_title(title, pad=20, fontsize="small")


def rea_time_change_string(dbl_time):
    prev = pretty_time(dbl_time[0])
    curr = pretty_time(dbl_time[1])

    if prev[0] == "-":
        head = f"/2 : {prev[1:]}"
        tail = f"{curr[1:]}"   if curr[0] == "-" else \
               f"x2 en {curr}" if curr != "_" else curr
    else:
        head = f"x2 : {prev}"
        tail = f"/2 en {curr[1:]}" if curr[0] == "-" else \
               f"{curr}"

    return f"réa {head} –> {tail}"


def pretty_time(val):
    return f"_" if abs(val) > 90 else f"{val:.0f} j"


def init():
    from os import path, system
    if not path.exists("data.csv"):
        system("./fetch.sh")

    global dep
    dep = pd.read_csv("dep.csv", sep="\t")

    global opt
    opt = parse_args()


def show():
    from os import getenv
    if getenv("DISPLAY") and not opt.noshow: plt.show()


def parse_args():
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument("--zoom-1-100", action="store_true",
            help="graph using 1-100 y scale [default is 1-50]")
    parser.add_argument("--zoom", action="store",
            type=int, metavar='<max-y>',
            help="graph using 1-<max-y> for y-scale")
    parser.add_argument("--two-months", action="store_true",
            help="graph last two months")
    parser.add_argument("--full", action="store_true",
            help="graph full history from day one")
    parser.add_argument("--episode-1", action="store_true",
            help="graph Episode I time window")
    parser.add_argument("--fouché", action="store_true",
            help="graph Fouché-fixed réa (5/8)")
    parser.add_argument("--proj", action="store",
            type=int, metavar='<nb-days>', default=7,
            help="show <nb-days> of projection for regressors")
    parser.add_argument("--proj-val", action="store_true",
            help="show projections values on right y-axis")
    parser.add_argument("--pred", action="store_true",
            help="graph predictor")
    parser.add_argument("--noise", action="store_true",
            help="show mortality noise level")
    parser.add_argument("--ref-dc", action="store",
            type=int, metavar='<% level>', default=0,
            help="show reference mortality level")
    parser.add_argument("--round", action="store_true",
            help="show rounded values graphs")
    parser.add_argument("--week", action="store_true",
            help="show weekly average graph")
    parser.add_argument("--réa", action="store_true",
            help="show réa raw values")
    parser.add_argument("--hills", action="store_true",
            help="show dc as hills instead of bars")
    parser.add_argument("--log-scale", action="store_true",
            help="use logarithmic y-scale for graphs")
    parser.add_argument("--style", action="store",
            choices=plt.style.available, metavar='<style>',
            help="use <style> instead of xkcd [try: fast]")
    parser.add_argument("--noshow", action="store_true",
            help="don't display graph on screen")
    parser.add_argument('arg', nargs='+',
            help="dept [dept ...] or region (%s)" % "|".join(regions.keys()))

    return parser.parse_args()


init()
main()
show()
