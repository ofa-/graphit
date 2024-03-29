all:

setup:
	sudo apt-get install -y python3 language-pack-fr
	pip3 install -r requirements.txt

check:
	./graphit.py --help
	:
	tail -1 data.csv
	:
	./graphit.py --noshow 38
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
		idf pc gc
nonoise = \
		05 04

graphit = ./graphit.py --noshow --round --week --style fast

radar: opts = --two-months
radar: met.opt = --zoom 350 --proj-val
radar:
	for dept in $(nonoise); do \
		$(graphit) $$dept $(opts) & \
	done; \
	for dept in $(depts); do \
		$(graphit) $$dept $(opts) --noise & \
	done; \
	$(graphit) met $(met.opt) $(opts) --noise & \
	$(graphit) met --full & \
	wait

met:
	./graphit.py \
		--style fast \
		--week --round --noise \
		--zoom 150 \
		--proj-val --proj $$((12 - `date +%u`)) \
		met

help.fr:
	curl -sL https://github.com/ofa-/graphit/blob/master/help.fr.md \
	| sed '/<article/ s:>:\n:' \
	| sed '1,/<article/ d; /<\/article/,$$ d' \
	| sed 's:<svg.*</svg>::g' \
	> help.fr.md.html

fetch:
	./fetch.sh

wait-for-data.csv:
	@(\
	today=`date +%F`	;\
	last_data() { tail -1 data.csv | cut -d ';' -f2; } ;\
	while true; do \
		./fetch.sh	;\
		printf "."	;\
		if [ "`last_data`" = $$today ]; then break; fi;\
		sleep 1m	;\
	done ) 2>/dev/null


day.dc:
day.dc: day = $(shell tail -1 data.csv | cut -d\; -f2)

%.dc:
	grep $(day) data.csv | grep -v '"97' \
			| cut -f5 -d\; | xargs | tr ' ' + | bc

%.dc: day = $*


waves-toll:
	./waves-toll.py

death-rate:
	./waves-toll.py  |\
		jq '.[] | ."nb morts" / ."nb jours"' |\
	        awk '{printf("%.0f\n", $$1)}'

insee.%: release = 2023-02-24

insee.diff: prev_rel = $(shell ls | grep insee_dc.20 | sort -r | sed -n 2p)
insee.diff:
	diff -ru $(prev_rel) insee_dc.$(release) |\
	egrep '^\+' | sed '1d' |\
	cut -c 1-8 | uniq -c

insee.fetch: zip_file = $(release)_detail.zip
insee.fetch:
	: home: https://www.insee.fr/fr/statistiques/4487988
	curl -k $(insee.url)/$(zip_file) > $(zip_file)
	mkdir -p insee_dc.$(release)
	cd insee_dc.$(release); 7z x ../$(zip_file)
	rm -f $(zip_file)
	ln -sfT insee_dc.$(release) insee_dc

insee.url = https://www.insee.fr/fr/statistiques/fichier/4487988

insee.stat:
	./insee_dc.py --baseline-noise --age-split

insee.home:
	./insee_dc.py --baseline-noise --age-split --at-home
