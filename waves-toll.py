#!/usr/bin/env python3

import pandas as pd

def main():

    data = pd.read_csv('data.csv', sep=";", parse_dates=['jour'])

    metropole = data[~data.dep.str.match("^97")]

    selection = metropole

    sums = selection.groupby('jour').sum()

    dc = sums.incid_dc

    wave = [
        dc[(dc.index <= "2020-06-30")],
        dc[(dc.index >= "2020-09-01") & (dc.index <= "2021-06-30")],
        dc[(dc.index >= "2021-07-14") & (dc.index <= "2021-09-15")],
        dc[(dc.index >= "2021-11-01")],
    ]

    print({
        str(w.index[0].date()): {
            "nb jours": len(w.index),
            "nb morts": w.sum()
        }
        for w in wave
    })

main()
