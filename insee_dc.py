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


def overview_year_compare():
    dc = load_data()

    dc['depdom'] = dc.COMDOM.astype(str).apply(lambda x: x[0:2])

    _met = dc[dc.depdom < "97"]

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


def plot_age_split(_met):
    split = [200, 60, 70, 80, 90]
    sel = [ _met[_met.ANAIS > (2020-x)] \
            .groupby(["ADEC", "MDEC", "JDEC"]).ANAIS.count()
        for x in split
    ]
    y = pd.DataFrame({ k: v[2020].reset_index().ANAIS
        for k,v in (
            { f"<{age}" if age < 200 else "métropole" : sel[i]
                    for i, age in enumerate(split)
            }).items()
        },
    )
    index = pd.date_range(freq='D', start="2020-01-01", periods=len(y))
    y = y.set_index(index)
    p = y.plot(alpha=0.5, linewidth=.7)

    avg = y.rolling(7, center=True).mean()
    std = y.rolling(7, center=True).std()

    for i, c in enumerate(y.columns):
        _avg, _std = avg[c], std[c]
        color = p.lines[i].get_color()
        p.plot(_avg, color=color, alpha=0.8)
        p.axes.fill_between(y.index, _avg-_std, _avg+_std, alpha=0.3, color=color)

    for _sel in sel[1:]: # all slices but metropole
      for year in [2018, 2019]:
        ref = baseline(_sel[year])
        p.plot(ref, color='grey', linestyle=':', linewidth=.7)

    for handle in p.legend_.legendHandles:
        handle.set_linewidth(3)
    p.figure.set(figheight=7, figwidth=16)
    p.set_title("Décès quotidiens par tranche d'age - données INSEE 2020\n" +
                "en gris : données 2018 et 2019",
                {'fontsize': 'medium'}, pad=20)

    plt.show()


def baseline(sel):
    index = pd.date_range(freq='D', start="2020-01-01", periods=59).append(
            pd.date_range(freq='D', start="2020-03-01", periods=len(sel)-59))
    return pd.DataFrame(
                sel.reset_index().ANAIS.rolling(7, center=True).mean()
    ).set_index(index)


def main():
    #by_death_location()

    met, eld, _met = overview_year_compare()

    #plot_years(met)
    plot_age_split(_met)
    #plot_age_split(_met[_met.depdom.str.match("59")])


main()
