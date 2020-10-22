
function onload() {
	document.body.innerHTML = document
		.querySelector("noscript").textContent

	var images = document.images

	for (var i=0; i < images.length; i++) {
		var img = images[i]
		img.style.display = "none"
		img.onclick = onclick_img
		img.next = images[(i+1) % images.length]
		img.prev = images[(i-1+images.length) % images.length]
	}
	images.curr = images[images.length-1]
	images.map = create_map()
	show(images.curr)

	document.onkeydown = onkeypress
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

function onclick_img(ev) {
	show(ev.shiftKey ? this.prev : this.next)
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
	var image = document.images.curr
	switch (ev.keyCode) {
		case 37: show(image.prev); break;
		case 39: show(image.next); break;
	}
}
