const canvas = document.getElementById('drawcanvas')
const img = document.getElementById('srcimg')
const ctx = canvas.getContext("2d")
ctx.lineWidth = 3
const fmt = new Intl.NumberFormat()
let socket = new WebSocket('ws://localhost:8001/');
let frame = 1

let boxes = []

class playerbox {
    constructor(x, y, w, h) {
        this.x = x
        this.y = y
        this.w = w
        this.h = h
        this.color = "#ff0000"
    }
    setbounds(x, y, w, h) {
        this.x = x
        this.y = y
        this.w = w
        this.h = h
    }
    map_coords() {
        let w = img.clientWidth
        let h = img.clientHeight
        let wn = img.naturalWidth
        let hn = img.naturalHeight
        let wr = w/wn
        let wv = h/hn
        return [this.x * wr, this.y * wv, this.w * wr, this.h * wv]
    }
    draw(ctx_handle) {
        ctx_handle.beginPath();
        ctx_handle.rect(...this.map_coords())
        ctx_handle.stroke()
    }
    retstr() {
        return `${this.x} ${this.y} ${this.w} ${this.h}`
    }
}

let b = new playerbox(0, 0, 0, 0)

img.addEventListener("load",  (e) => {
    canvas.width = img.width
    canvas.height = img.height
})

const handler = function (e) {
    socket.send(JSON.stringify({
        "text": textinp.value,
        "num": parseFloat(numinp.value)
    }))
}

function draw(e) {
    canvas.width = img.clientWidth
    canvas.height = img.clientHeight
    ctx.clearRect(0, 0, canvas.clientWidth, canvas.clientHeight)
    boxes.map(box => {
        box.draw(ctx)
    })
}
const receiver = function ({ data }) {
    pdata = JSON.parse(data)
    console.log(pdata)
    boxes = pdata.map(v => new playerbox(v.x, v.y, v.w, v.h))
    ctx.clearRect(0, 0, canvas.width, canvas.height)
    draw()
}

const id = setInterval(() => {
    socket = new WebSocket('ws://localhost:8001/')
}, 5000)
socket.addEventListener('open', e => {
    clearInterval(id)
    socket.send(JSON.stringify({data: "boxes"}))
})
socket.addEventListener('message', receiver)
socket.addEventListener('error', er => console.error("couldn't connect."))

let observer = new ResizeObserver(draw)
observer.observe(img)