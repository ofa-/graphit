Overview
========

This is a tool for graphing French public health autorities hospital data.

- `réa` and `dc` graphs: moving averages (7 days, centered), \
   ICU admissions and daily deaths respectively

- `grey line` subliminal dots: 50% of usual daily all causes mortality, \
   for département or zone (insee detailled data 2018+2019, monthly averages)

- `red lines`: «exponential» regressions on chunks of `dc`,
   red balls indicate doubling time (or divide-by-two time),
   above line when increasing, below line when decreasing

- `green lines`: «exponential» regressions on chunks of `réa`, \
   green balls indicate doubling or divide-by-two time

data: Santé Publique France >
[data.gouv.fr][data.gouv.hospi] >
[nouveaux-covid19.csv][data]


[data]: https://www.data.gouv.fr/fr/datasets/r/6fadff46-9efd-4c53-942a-54aca783c30c
[data.gouv.hospi]: https://www.data.gouv.fr/fr/datasets/donnees-hospitalieres-relatives-a-lepidemie-de-covid-19/


Installing
==========

```
sudo apt-get install python3-tk

mkvirtualenv python=`which python3`

pip install -r requirements.txt
```


Running
=======

```
./fetch.sh
./predictor.py
```

```
./predictor.py idf
./predictor.py 13
./predictor.py 69 38
```


Installing an xkcd-style font
=============================

```
make xkcd.ttf clean
```

Note: the usual xkcd-like font is `Humor-Sans`, but it has no latin glyphs.
