
function onload() {
	document.body.innerHTML = document
		.querySelector("noscript").textContent

	var images = document.images

	for (var i=0; i < images.length; i++) {
		var img = images[i]
		img.style.display = "none"
		img.onload = create_areas
		img.next = images[(i+1) % images.length]
		img.prev = images[(i-1+images.length) % images.length]
	}
	images.curr = images[images.length-1]
	images.curr.next = images.curr.prev
	images.curr.prev.next = images[0]
	images[0].prev = images.curr.next
	images.home = images.curr
	images.map = create_map()
	show(images.curr)

	document.onkeydown = onkeypress
}

function create_areas() {
	var img = this
	var width = img.width
	var height = img.height
	var map = document.createElement("map")
	map.name = img.src.replace(/.*\//, "")
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
	img.setAttribute("usemap", "#" + map.name)
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

function create_map() {
	var map = document.createElement("img")
	map.src = "img/curfew-plain.png"
	map.setAttribute("class", "map")
	map.onclick = onclick_map
	document.body.appendChild(map)
	return map
}

function onclick_map() {
	this.style.opacity = this.style.opacity ? "" : "0"
}

function show(image) {
	var images = document.images

	images.curr.style.display = "none"
	image.style.display = ""
	images.curr = image
	images.map.src = "img/curfew-" + image.src
		.replace(/.*\//, "")
		.replace(/met-full/, "plain")
}

function onkeypress(ev) {
	switch (ev.keyCode) {
		case 37: show_prev(); break;
		case 39: show_next(); break;
		case 27: show_home(); break;
	}
}
