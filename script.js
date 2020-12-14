var _region = {
	"radar": "met,13,34,30,31,33,69,42,38,73,74,05,67,76,59,75,pc,gc,idf",
	"paca": "04,05,06,13,83,84",
	"rhone-alpes": "69,42,07,01,26,38,73,74",
	"auvergne": "03,15,43,63",
	"bretagne": "22,29,35,56",
	"normandie": "14,27,50,61,76",
	"limousin": "19,23,87",
	"aquitaine": "24,33,40,47,64",
	"poitou-charentes": "16,17,79,86",
	"nouvelle-aquitaine": "16,17,19,23,24,33,40,47,64,79,86,87",
	"midi-pyrenees": "09,12,31,32,46,65,81,82",
	"languedoc-roussillon": "11,30,34,48,66",
	"occitanie": "09,11,12,30,31,32,34,46,48,65,66,81,82",
	"grand-est": "08,10,51,52,54,55,57,67,68,88",
	"centre-val-de-loire": "18,28,36,37,41,45",
	"pays-de-la-loire": "44,49,53,72,85",
	"bourgogne": "21,58,71,89",
	"franche-comte": "25,39,70,90",
	"hauts-de-france": "02,59,60,62,80",
	"ile-de-france": "75,77,78,91,92,93,94,95,pc,gc,idf",
	"sud": "34,30,13,83,06,2A,2B",
}

var base = "https://github.com/coviiid/coviiid.github.io/raw/master~0/fig/"


function onload() {

	var query = document.location.search.substring(1)
	var region = get_region(query).split(",")

	load_images(region)
	set_loop()
	add_img_areas()
	add_home_img()
	add_regions()
	add_help()

	document.onkeydown = onkeypress

	if (query)
		show_query(query)
	else
		show_home()
}

function load_images(region) {
	var images = []
	for (var i=0; i < region.length; i++) {
		var img = document.createElement("img")
		img.setAttribute("usemap", "#fig")
		img.src = base + region[i] + ".png"
		images[region[i]] = img
	}
	images.first = images[region[0]]
	images.index = region

	document.img = images
}

function show_query(query) {
	var img = document.img
	if (query in _region) {
		show(img.first)
		toggle_regions()
	}
	else {
		query = query.split(",")[0]
		show(img[query] || img.first)
	}
}

function get_region(query) {
	var region = _region[query || "radar"]
	return region ? region : region_of_dep(query)
}

function region_of_dep(query) {
	for (var r in _region)
		if (_region[r].includes(query))
			return _region[r]
	return query
}

function set_loop() {
	var images = document.img,
		idx = images.index,
		len = images.index.length
	for (var img, i=0; i < len; i++) {
		img = images[idx[i]]
		img.next = images[idx[(i+1) % len]]
		img.prev = images[idx[(i-1+len) % len]]
	}
}

function add_img_areas() {
	document.img.first.onload = create_areas
}

function add_home_img() {
	var home = document.createElement("img")
	home.src = base + "../full/met-full.png"
	home.setAttribute("class", "full")
	home.onclick = show_next
	home.next = home.prev = document.img.first

	document.img.home = home
	document.img.curr = home
	document.body.appendChild(home)
}

function add_regions() {
	var regions = document.createElement("div")
	regions.setAttribute("class", "buttons")
	regions.style.display = "none"

	for (var r in _region) {
		var butt = document.createElement("div")
		butt.innerHTML = r
		butt.onclick = region_button_onclick
		butt.id = r
		regions.appendChild(butt)
	}

	var icon = document.createElement("div")
	icon.setAttribute("class", "icon")
	icon.innerHTML = "R"

	var container = document.createElement("div")
	container.setAttribute("class", "regions")
	container.appendChild(regions)
	container.appendChild(icon)
	regions.onclick = icon.onclick = toggle_regions

	document.body.appendChild(container)
}

function region_button_onclick(ev) {
	ev.stopPropagation()
	document.location.replace(
		document.location.pathname + "?" + this.id
	)
}

function toggle_regions() {
	var style = document.querySelector(".regions .buttons").style
	style.display = (style.display ? "" : "none")
}

function add_help() {
	var help = document.createElement("div")
	help.setAttribute("class", "help")
	help.innerHTML = (
	'<div class="icon">?</div>' +
	'<p class="text" style="display:none">' +
	'<iframe src="help.fr.md.html" onload="move_to_parent(this)"/>' +
	'</p>'
	)
	help.firstChild.onclick = toggle_help
	help.lastChild.onclick = toggle_help

	document.body.appendChild(help)
}

function toggle_help() {
	var style = document.querySelector(".help .text").style
	style.display = (style.display ? "" : "none")
}

function move_to_parent(e) {
	e.parentNode.appendChild(e.contentDocument.body)
	e.parentNode.removeChild(e)
}

function create_areas() {
	var img = this
	img.onload = null
	var width = img.width
	var height = img.height

	var map = document.createElement("map")
	map.name = "fig"
	map.innerHTML = (
	"<area shape='rect' coords='" +
		"0,0," + width + ",69'>" +
	"<area shape='rect' coords='" +
		"0,70," + (width/2) + "," + height + "'>" +
	"<area shape='rect' coords='" +
		(width/2 +1) + ",70," + width + "," + height + "'>"
	)
	map.children[0].onclick = show_home
	map.children[1].onclick = show_prev
	map.children[2].onclick = show_next
	document.body.appendChild(map)
}

var time_offset = 0

function time_fwd() {
	time_set_images(++time_offset)
}

function time_back() {
	time_set_images(time_offset ? --time_offset : 0)
}

function time_reset() {
	time_set_images(time_offset=0)
}

function time_set_images(offset) {
	var img = document.img.curr
	img.src = img.src.replace(/~[0-9]+/, "~"+offset)
}

function show_prev() {
	show(document.img.curr.prev)
}

function show_next() {
	show(document.img.curr.next)
}

function show_home() {
	show(document.img.home)
}

function show(image) {
	var images = document.img

	images.curr.parentNode.replaceChild(image, images.curr)
	images.curr = image
}

function onkeypress(ev) {
	switch (ev.keyCode) {
		case 37: show_prev(); break;
		case 39: show_next(); break;
		case 27: show_home(); break;
		case 38: time_fwd(); break;
		case 40: time_back(); break
		case 48: time_reset(); break
		case 188:
		case 72: return toggle_help()
		case 82: return toggle_regions()
	}
}
