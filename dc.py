#!/usr/bin/env python

import pandas as pd
import matplotlib.pyplot as plt


# https://www.insee.fr/fr/statistiques/4487988
# https://www.insee.fr/fr/statistiques/fichier/4487988/2020-10-02_detail.zip


def compute_dc_j():
    dc = pd.DataFrame()
    dc = dc.append(pd.read_csv(f"insee_dc/DC_2018_det.csv", sep=";"))
    dc = dc.append(pd.read_csv(f"insee_dc/DC_2019_det.csv", sep=";"))

    dc['depdom'] = dc.COMDOM.astype(str).apply(
                    lambda x: x[0:2 if x[0:2] != "97" else 3])

    dc_j = dc.groupby(['depdom', 'MDEC', 'JDEC']).ADEC.count() / 2 # 2 years
    mean = dc_j.groupby(['depdom', 'MDEC']).mean()

    return mean.round().astype(int).rename("dc_j")


def graph(dc_j, selection):
    depts = [f"{dep:02}" for dep in selection]

    p = pd.DataFrame({dep: dc_j[dep] for dep in depts}, index=range(1,13))

    with plt.xkcd():
        plot(p).set_xlim(-0.5, 5.7)
        plot(p).set_xlim(5.5, 11.7)


def plot(p):
        _ = p.plot.bar(rot=0)
        _.set_xlabel('MOIS', labelpad=14)
        _.set_ylabel('DC / JOUR', labelpad=14)
        _.legend(handlelength=1, markerfirst=False)
        _.set_ylim(1)
        _.figure.set(figheight=7, figwidth=12)
        return _


def alt_compute_and_graph(dc_m, days_in_month):
    z = pd.DataFrame([
        [ dep, month, round(dc_m[(dep,month)] / days_in_month[month]) ]
                for dep, month in dc_m.index ],
        columns=['depdom', 'mois', 'dc_j'])

    p = z.pivot(index='mois', columns='depdom')

    p[[('dc_j', dep) for dep in depts]] \
            .plot.bar(ylabel='dc / jour') \
            .legend(depts)


def main():
    dc_j = compute_dc_j()

    with open("dc_j.csv", "w") as f:
        f.write(dc_j.to_csv())

    graph(dc_j, [13, 33, 69, 83, 31, 38, 1, 26, 73])

    plt.show()


main()
