all:

setup:
	sudo apt-get install -y python3 language-pack-fr
	pip3 install -r requirements.txt

check:
	./predictor.py --help
	:
	tail -1 data.csv
	:
	./predictor.py --noshow 38
	ls -lh 38.png


FONT = Yahfie/Yahfie-Heavy.ttf
ZIPFILE = Yahfie-Normal.font.zip

xkcd.ttf: fontname.py ~/.fonts
	wget https://www.ffonts.net/$(ZIPFILE)
	unzip -p $(ZIPFILE) $(FONT) > $@
	./fontname.py xkcd $@
	cp $@ ~/.fonts/
	rm -f ~/.cache/matplotlib/fontlist-*.json
	rm -f $(ZIPFILE)

fontname.py:
	pip3 install fonttools
	wget https://github.com/chrissimpkins/fontname.py/raw/master/fontname.py
	chmod +x fontname.py

~/.fonts:
	mkdir $@

clean:
	pip uninstall -y fonttools
	rm -f xkcd.ttf fontname.py


depts = \
		31 34 13 42 69 38 76 75 59 \
		33 67 30 73 74 50 06 35 \
		idf pc gc met
nonoise = \
		05 04

graphit = ./predictor.py --round

radar:
	unset DISPLAY; \
	for dept in $(nonoise); do \
		$(graphit) $$dept --two-months & \
	done; \
	for dept in $(depts); do \
		$(graphit) $$dept --two-months --noise & \
	done; \
	$(graphit) met --full & \
	wait

help.fr:
	curl -sL https://github.com/ofa-/predictor/blob/master/help.fr.md \
	| sed '/<article/ s:>:\n:' \
	| sed '1,/<article/ d; /<\/article/,$$ d' \
	| sed 's:<svg.*</svg>::g' \
	> help.fr.md.html

fetch:
	./fetch.sh

wait-for-data.csv:
	while [ `tail -1 data.csv | cut -d ';' -f2` != `date +%F` ]; do \
		sleep 1m	;\
		./fetch.sh	;\
	done

upload:
	lftp -c "open $(TARGET); mput *.png"

insee.diff:
	diff -ru insee_dc.2021-03-12 insee_dc.2021-03-19 |\
	egrep '^\+' | sed '1d' |\
	cut -c 1-8 | uniq -c

insee.fetch: release = 2021-03-19
insee.fetch:
	wget https://www.insee.fr/fr/statistiques/fichier/4487988/$(release)_detail.zip
	mkdir insee_dc.$(release)
	cd insee_dc.$(release); unzip ../$(release)_detail.zip
	rm -f $(release)_detail.zip
	ln -sfT insee_dc.$(release) insee_dc

insee.stat:
	./insee_dc.py
