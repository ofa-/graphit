#!/usr/bin/env python3

import pandas as pd
import json

def main():

    data = pd.read_csv('data.csv', sep=";", parse_dates=['jour'])

    metropole = data[~data.dep.str.match("^97")]

    selection = metropole

    sums = selection.groupby('jour').sum()

    dc = sums.incid_dc

    wave = [
        dc[(dc.index <= "2020-06-30")],
        dc[(dc.index >= "2020-09-01") & (dc.index <= "2021-06-30")],
        dc[(dc.index >= "2021-07-14") & (dc.index <= "2021-10-10")],
        dc[(dc.index >= "2021-11-01") & (dc.index <= "2022-05-31")],
        dc[(dc.index >= "2022-06-01") & (dc.index <= "2022-09-15")],
        dc[(dc.index >= "2022-09-16") & (dc.index <= "2022-11-13")],
        dc[(dc.index >= "2022-11-14")],
    ]

    print(json.dumps(
    {
        str(w.index[0].date()) + " > " + str(w.index[-1].date()): {
            "nb jours": len(w.index),
            "nb morts": int(w.sum()),
        }
        for w in wave
    },
    indent=2))

main()
