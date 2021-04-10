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

    elder = _met[_met.ANAIS < (2020-80)]

    met = _met.groupby(["ADEC", "MDEC", "JDEC"]).ANAIS.count()
    eld = elder.groupby(["ADEC", "MDEC", "JDEC"]).ANAIS.count()

    return met, eld, _met


def load_data():
    dc = pd.DataFrame()
    for year in [ 2018, 2019, 2020 ]:
        dc = dc.append(
                pd.read_csv(f"insee_dc/DC_{year}_det.csv", sep=";"))
    return dc


def plot_years(met):
    y = pd.DataFrame({
            y: met[y].reset_index().ANAIS
                for y in [2018, 2019, 2020]
            },
            index=range(365)
    )
    y.plot() ; plt.show()


def plot_age_split(_met, raw_data=0, noise=False, label_all=""):
    split = [200, 60, 70, 80, 90]
    sel = [ _met[_met.ANAIS > (2020-x)] \
            .groupby(["ADEC", "MDEC", "JDEC"]).ANAIS.count()
        for x in split
    ]
    if not label_all: label_all = "métropole"
    y = pd.DataFrame({ k: v[2020].reset_index().ANAIS
        for k,v in (
            { f"<{age}" if age < 200 else label_all : sel[i]
                    for i, age in enumerate(split)
            }).items()
        },
    )
    index = pd.date_range(freq='D', start="2020-01-01", periods=len(y))
    y = y.set_index(index)
    p = y.plot(alpha=0.5, linewidth=raw_data)

    for _sel in sel:
      for year in [2018, 2019]:
        ref = baseline(_sel[year])
        color = 'grey'
        p.plot(ref._avg, color=color, linestyle=':', linewidth=.7)
        if noise:
            p.axes.fill_between(ref.index, ref._avg-ref._std, ref._avg+ref._std, alpha=0.07, color=color)

    avg = y.rolling(7, center=True).mean()
    std = y.rolling(7, center=True).std()

    for i, c in enumerate(y.columns):
        _avg, _std = avg[c], std[c]
        color = p.lines[i].get_color()
        p.plot(_avg, color=color, alpha=0.8)
        if noise:
            p.axes.fill_between(y.index, _avg-_std, _avg+_std, alpha=0.3, color=color)

    p.legend(loc='upper left')
    for handle in p.legend_.legendHandles:
        handle.set_linewidth(3)

    p.figure.set(figheight=7, figwidth=16)
    p.set_title("Décès quotidiens toutes causes par tranche d'age\n" +
                "Données INSEE 2020 (couleur), 2018 et 2019 (gris)",
                fontsize='medium', horizontalalignment='left',
                bbox={'facecolor':'white', 'alpha':.2, 'boxstyle':'round,pad=.4'},
                x=.703, y=.92, transform=p.transAxes)

    plt.show()


def baseline(sel):
    index = pd.date_range(freq='D', start="2020-01-01", periods=59).append(
            pd.date_range(freq='D', start="2020-03-01", periods=len(sel)-59))
    data = sel.reset_index().ANAIS.rolling(7, center=True)
    return pd.DataFrame(
            { "_avg": data.mean(), "_std": data.std() }
    ).set_index(index)


def parse_args():
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument("--noise", action="store_true",
            help="graph noise")
    parser.add_argument("--raw", action="store_true",
            help="graph noise")
    parser.add_argument("--years", action="store_true",
            help="graph years")
    parser.add_argument('arg', nargs='*',
            help="dept [dept ...]")

    return parser.parse_args()


def main():
    #by_death_location()

    global opt
    opt = parse_args()

    sel = "|".join(opt.arg)

    met, eld, _met = overview_year_compare(sel)

    if opt.years:
        plot_years(met)
        return

    plot_age_split(_met, raw_data=0.7 if opt.raw else 0,
                    label_all=sel, noise=opt.noise)
    #plot_age_split(_met[_met.depdom.str.match("59")])


main()
