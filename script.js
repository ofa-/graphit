var _region = {
	"radar": "13,34,30,31,33,69,42,38,73,74,05,67,76,59,75,pc,gc,idf,met",
	"paca": "04,05,06,13,83,84",
	"rhone-alpes": "69,42,07,01,26,38,73,74",
	"auvergne": "03,15,43,63",
	"bretagne": "22,29,35,56",
	"normandie": "14,27,50,61,76",
	"aquitaine": "16,17,19,23,24,33,40,47,64,79,86,87",
	"occitanie": "09,11,12,30,31,32,34,46,48,65,66,81,82",
	"grand-est": "08,10,51,52,54,55,57,67,68,88",
	"centre-loire": "18,28,36,37,41,45",
	"pays-loire": "44,49,53,72,85",
	"bourgogne": "21,58,71,89",
	"franche-comte": "25,39,70,90",
	"hauts-france": "02,59,60,62,80",
	"ile-de-france": "75,77,78,91,92,93,94,95",
	"sud": "34,30,13,83,06,2A,2B",
}

var base = "https://coviiid.github.io/fig/"


function onload() {

	var query = document.location.search.substring(1)
	var region = get_region(query).split(",")

	for (var i=0; i < region.length; i++) {
		var img = document.createElement("img")
		img.style.display = "none"
		img.setAttribute("usemap", "#fig")
		img.src = base + region[i] + ".png"
		document.body.appendChild(img)
	}
	set_loop(document.images)
	add_img_areas()
	add_home_img()
	add_help()

	document.onkeydown = onkeypress

	if (query)
		show_query(query)
	else
		show_home()
}

function show_query(query) {
	query = query.split(",")[0] + ".png"

	var images = document.images
	for (var i=0; i < images.length; i++) {
		var img = images[i]
		if (img.src.replace(/.*\//, "") != query)
			continue
		show(img)
		break
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

function set_loop(images) {
	var img, len = images.length
	for (var i=0; i < len; i++) {
		img = images[i]
		img.next = images[(i+1) % len]
		img.prev = images[(i-1+len) % len]
	}
}

function add_img_areas() {
	document.images[0].onload = create_areas
}

function add_home_img() {
	var home = document.createElement("img")
	home.src = base + "../full/met-full.png"
	home.setAttribute("class", "full")
	home.onclick = show_next
	home.next = document.images[0]
	home.prev = home.next.prev

	document.body.append(home)
	document.images.home = home
	document.images.curr = home
}

function add_help() {
	var help = document.createElement("div")
	help.innerHTML = (
	'<img class="help icon" src="img/help_icon.png">' +
	'<p class="help text" style="display:none">' +
	'<iframe src="help.fr.md.html" onload="move_to_parent(this)"/>' +
	'</p>'
	)
	help.firstChild.onclick = toggle_help
	help.lastChild.onclick = toggle_help

	document.body.appendChild(help)
}

function toggle_help() {
	var style = document.querySelector(".help.text").style
	style.display = (style.display ? "" : "none")
}

function move_to_parent(e) {
	e.parentNode.appendChild(e.contentDocument.body)
	e.parentNode.removeChild(e)
}

function create_areas() {
	var img = this
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

function show_prev() {
	show(document.images.curr.prev)
}

function show_next() {
	show(document.images.curr.next)
}

function show_home() {
	show(document.images.home)
}

function show(image) {
	var images = document.images

	images.curr.style.display = "none"
	image.style.display = ""
	images.curr = image
}

function onkeypress(ev) {
	switch (ev.keyCode) {
		case 37: show_prev(); break;
		case 39: show_next(); break;
		case 27: show_home(); break;
		case 72: return toggle_help()
	}
}
