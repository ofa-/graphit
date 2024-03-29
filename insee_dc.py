#!/usr/bin/env python

import pandas as pd
import matplotlib.pyplot as plt

import locale; locale.setlocale(locale.LC_ALL, "fr_FR.UTF8")


def by_death_location():
    dc = load_data()

    print(
    dc.groupby(["LIEUDEC2", "ADEC"]).count().MDEC.reset_index() \
        .pivot(index="LIEUDEC2", columns="ADEC")
    )


def overview_year_compare(sel=""):
    dc = load_data()

    dc['depdom'] = dc.COMDOM.astype(str).apply(lambda x: x[0:2])

    _met = dc[dc.depdom < "97"]

    if sel: _met = dc[dc.depdom.str.match(sel)]

    if opt.at_home:
        _met = _met[_met.LIEUDEC2 == "Logem"]

    elder = _met[_met.ANAIS < (2021-80)]

    met = _met.groupby(["ADEC", "MDEC", "JDEC"]).ANAIS.count()
    eld = elder.groupby(["ADEC", "MDEC", "JDEC"]).ANAIS.count()

    return met, eld, _met


def load_data():
    dc = pd.DataFrame()
    for year in [ 2018, 2019, 2020, 2021, 20222023 ]:
        dc = dc.append(
                pd.read_csv(f"insee_dc/DC_{year}_det.csv", sep=";"))
    return dc


def plot_years(met):
    y = pd.DataFrame({
            y: met[y].reset_index().ANAIS
                for y in [2018, 2019, 2020, 2021, 2022]
            },
            index=range(365)
    )
    y.plot() ; plt.show()


def plot_age_split(_met, opt, raw_width=0, label_all=""):
    split = [200, 90, 80, 70, 60]
    if not label_all: label_all = "métropole"

    index = pd.date_range(freq='D', start="2022-01-01", periods=365)

    y = get_age_split(_met, 2020, split, label_all)
    y = y.drop(59).set_index(index)
    p = y.plot(alpha=0.5, linewidth=raw_width)

    y1 = get_age_split(_met, 2021, split, label_all)
    y1 = y1.set_index(index)
    p.plot(y1, alpha=0.5, linewidth=raw_width)

    Y = get_age_split(_met, 2022, split, label_all).rolling(7, center=True).mean()
    Y = Y.set_index(index[:len(Y)])
    for i, c in enumerate(y.columns):
        _y = Y[c]
        color = p.lines[i].get_color()
        p.plot(_y, color=color, alpha=0.8)

    for year in [2018, 2019]:
      dta = get_age_split(_met, year, split, label_all)
      for spl in range(len(split)):
        ref = baseline(dta.iloc[:,spl], index)
        color = 'grey'
        p.plot(ref._avg, color=color, linestyle=':', linewidth=.7)
        if opt.baseline_noise or opt.noise:
            p.axes.fill_between(ref.index, ref._avg-ref._std, ref._avg+ref._std, alpha=0.07, color=color)
    plot_avg(p, y, linestyle=":")
    plot_avg(p, y1)

    add_yaxis_note(p, "2020", y[label_all], 'grey')
    add_yaxis_note(p, "2022", Y[label_all], 'blue', days=13)

    set_legend(p)

    plt.show()


def plot_avg(p, y, **kwargs):
    avg = y.rolling(7, center=True).mean()
    std = y.rolling(7, center=True).std()

    for i, c in enumerate(y.columns):
        _avg, _std = avg[c], std[c]
        color = p.lines[i].get_color()
        p.plot(_avg, color=color, alpha=0.4, **kwargs)
        if opt.noise:
            p.axes.fill_between(y.index, _avg-_std, _avg+_std, alpha=0.3, color=color)


def set_legend(p):
    p.legend(loc='upper left')
    for handle in p.legend_.legendHandles:
        handle.set_linewidth(3)

    p.figure.set(figheight=7, figwidth=10)
    p.figure.subplots_adjust(left=.08, right=.96, top=.94)
    p.set_title("Décès quotidiens toutes causes par tranche d'age\n" +
                "Données INSEE 2020-22 (couleur), 2018+19 (gris)" +
                ("\nDécès à domicile seulement" if opt.at_home else ""),
                fontsize='medium',
                bbox={'facecolor':'white', 'alpha':.2, 'boxstyle':'round,pad=.4'},
                x=.98, y=.9 - (.02 if opt.at_home else 0), loc="right")


def add_yaxis_note(plot, text, data, color, days=45):
    x = pd.Timestamp(plot.axes.get_xlim()[1], unit="D") - pd.Timedelta(days=days)
    y = data[str(x.date())] - (30 if opt.at_home else 0)
    point = [x, y]
    plot.annotate(
        text,
        xy=point,
        fontsize="x-small",
        bbox=dict(boxstyle="round4", fc="w", color=color),
        arrowprops=dict(arrowstyle="-|>", lw=.7,
            connectionstyle="arc3,rad=+0.2", fc="w"),
        xytext=(
            point[0] + pd.Timedelta(days=10),
            point[1] + 200 / (10 if opt.at_home else 1)
        )
    )


def get_age_split(data, year, split, label_all):
    sel = { x: data[data.ANAIS > (year-x)] \
            .groupby(["ADEC", "MDEC", "JDEC"]).ANAIS.count()
        for x in split
    }
    return pd.DataFrame({
        k: v[year].reset_index().ANAIS
        for k,v in (
            { f"<{age}" if age < 200 else label_all : sel[age]
                    for age in split
            }).items()
    })

def baseline(sel, index):
    data = sel.rolling(7, center=True)
    return pd.DataFrame(
            { "_avg": data.mean(), "_std": data.std() }
    ).set_index(index)


def parse_args():
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument("--noise", action="store_true",
            help="graph noise")
    parser.add_argument("--baseline-noise", action="store_true",
            help="graph noise for baseline")
    parser.add_argument("--raw", action="store_true",
            help="graph raw data")
    parser.add_argument("--years", action="store_true",
            help="graph years")
    parser.add_argument("--death-location", action="store_true",
            help="graph by death location")
    parser.add_argument("--age-split", action="store_true",
            help="graph age-split data")
    parser.add_argument("--at-home", action="store_true",
            help="graph only death at home")
    parser.add_argument('arg', nargs='*',
            help="dept [dept ...]")

    return parser.parse_args()


def main():
    global opt
    opt = parse_args()

    sel = "|".join(opt.arg)

    if opt.years:
        data, _, _ = overview_year_compare(sel)
        plot_years(data)
        return

    if opt.death_location:
        by_death_location()
        return

    if opt.age_split:
        _, _, data = overview_year_compare(sel)
        raw_width = 0.7 if opt.raw else 0
        plot_age_split(
                data,
                raw_width=raw_width,
                label_all=sel,
                opt=opt)
        return


main()
