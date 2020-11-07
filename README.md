Overview
========

This is a tool for graphing French public health autorities hospital data.

- `réa` and `dc` graphs: moving averages (last 7 days), \
   ICU admissions and daily deaths respectively

- `grey line` subliminal dots: 50% of usual daily all causes mortality, \
   for département or zone (insee detailled data 2018+2019, monthly averages)

- `red chunks` on métropole graphs: « prédictor » = `réa` shifted by x days, \
   slightly squashed+offset (factor 0.885, offset 0.2)

- `green lines`: «linear» regressions (log scale) on chunks of `réa`, \
   green balls indicate doubling time

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
