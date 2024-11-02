import { writable } from "svelte/store"
enum pages {
    HOME = "home",
    PAGE1 = "page-1"
}

const currentPage = writable(pages.HOME)
let counterVal = writable(0)
const currentFile = writable("")
let cvideo = writable("")
let port = writable(8000)
const boxesData = writable<box[]>([])
const dataStore = writable<{ [key: number]: box[] }>({})

class box {
    x: number
    y: number
    w: number
    h: number
    owner: number

    constructor(owner: number, x: number, y: number, w: number, h: number) {
        this.x = x
        this.y = y
        this.w = w
        this.h = h
        this.owner = owner
    }

    // transform image coordinates because the video is a different size to actual coordinates
    transformedCoords(rw: any, rh: number, aw: number, ah: number) { 
        const vmult = ah/rh
        const hmult = aw/rw
        return [this.x*hmult, this.y*vmult, this.w*hmult, this.h*vmult].map(Math.floor)
    }

    draw(ctx:CanvasRenderingContext2D, cvs: HTMLCanvasElement, realw: number, realh: number) {
        const w = cvs.width
        const h = cvs.height
        const [tx, ty, tw, th] = this.transformedCoords(realw, realh, w, h)
        ctx.beginPath()
        ctx.rect(tx, ty, tw, th)
        ctx.stroke()
    }
}

export { currentPage, pages, counterVal, currentFile, cvideo, port, boxesData, box, dataStore }
