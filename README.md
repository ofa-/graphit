Overview
========

This is a tool for graphing French public health autorities hospital data.

- `réa` and `dc` graphs: moving averages (7 days, centered), \
   ICU admissions and daily deaths respectively

- `grey line` subliminal dots: 25% of usual daily all causes mortality, \
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



Daily graphs
============

![met.png](https://github.com/coviiid/coviiid.github.io/raw/master/fig/met.png)

http://coviiid.free.fr



Usage
=====

```
$ ./predictor.py -h
usage: predictor.py [-h] [--zoom-1-100] [--two-months] [--full] [--episode-1]
                    [--fouché] [--pred] [--noise] [--round] [--hills]
                    [--log-scale] [--style <style>] [--noshow]
                    arg [arg ...]

positional arguments:
  arg              dept [dept ...] or region
                   (pc|gc|idf|paca|sud|ra|auv|ara|bfc|fc|ge|met)

optional arguments:
  -h, --help       show this help message and exit
  --zoom-1-100     graph using 1-100 y scale [default is 1-50]
  --two-months     graph last two months
  --full           graph full history from day one
  --episode-1      graph Episode I time window
  --fouché         graph Fouché-fixed réa (5/8)
  --pred           graph predictor
  --noise          show mortality noise level
  --round          show rounded values graphs
  --hills          show dc as hills instead of bars
  --log-scale      use logarithmic y-scale for graphs
  --style <style>  use <style> instead of xkcd [try: fast]
  --noshow         don't display graph on screen
```


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

```
./predictor.py met --full
./predictor.py met --two-months --noise
./predictor.py met --episode-1
./predictor.py met --style seaborn
```


Installing an xkcd-style font
=============================

```
make xkcd.ttf clean
```

Note: the usual xkcd-like font is `Humor-Sans`, but it has no latin glyphs.
