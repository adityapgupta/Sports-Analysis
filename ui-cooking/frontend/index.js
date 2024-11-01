const button1 = document.getElementById('submitbutton')
const textinp = document.getElementById('textinp')
const numinp = document.getElementById('numinp')
const numout = document.getElementById('numout')
const textout = document.getElementById('textout')
let socket;

const id = setInterval(() => {
    socket = new WebSocket('ws://')
})
socket.addEventListener('open')

const handler = function (e) {
    socket.send(JSON.stringify({
        "text": textinp.value,
        "num": parseFloat(numinp.value)
    }))
}

const receiver = function ({ data }) {
    let eventdata = JSON.parse(data)
    numout.textContent = eventdata.num
    textout.textContent = eventdata.text
}

socket.addEventListener('message', receiver)
button1.addEventListener('click', handler)