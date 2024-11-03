import { writable, get } from "svelte/store"
enum pages {
    HOME = "home",
    PAGE1 = "page-1"
}

const currentPage = writable(pages.HOME)
let counterVal = writable(0)
const currentFile = writable("")
let cvideo = writable("")
let port = writable(8000)
interface boxesData {
    [key: number]: box[]
}

const dataStore = writable<boxesData>({})
const allBoxes = writable<box[]>([])
const activeBox = writable<number>(0)
const activeBoxFrames = writable(0)

class box {
    x: number
    y: number
    w: number
    h: number
    owner: number
    appearedFrames = 0

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
        if (this.owner == get(activeBox)) {
            ctx.strokeStyle = "#55f"
            ctx.rect(tx, ty, tw, th)
            ctx.stroke()
            ctx.strokeStyle = "red"
        } else {
            ctx.rect(tx, ty, tw, th)
            ctx.stroke()
        }
    }

    isClicked(mouseX: number, mouseY: number, cvs: HTMLCanvasElement, realw: number, realh: number  ): boolean {
        const w = cvs.width
        const h = cvs.height
        const [tx, ty, tw, th] = this.transformedCoords(realw, realh, w, h)
        return mouseX >= tx && mouseX <= tx + tw && mouseY >= ty && mouseY <= ty + th
    }

    evaluateAppearedFrames() {
        this.appearedFrames = 0
        const storeData = get(dataStore);
        for (const key in storeData) {
            if (storeData.hasOwnProperty(key)) {
                const items = storeData[key];
                for (const item of items) {
                    if (item.owner == this.owner) {
                        this.appearedFrames++
                    }
                }
            }
        }
    }
}
const video_duration = $state(writable(0));

export { currentPage, pages, counterVal, currentFile, cvideo, port, type boxesData, box, dataStore, video_duration, activeBox, allBoxes, activeBoxFrames }
