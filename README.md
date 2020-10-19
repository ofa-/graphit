
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
