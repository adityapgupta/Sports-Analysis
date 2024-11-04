import { writable, get } from "svelte/store"
enum pages {
    HOME = "home",
    PAGE1 = "page-1"
}

export let currentPage = writable(pages.HOME)
export let currentFile = writable("")
export let cvideo = writable("")
export let port = writable(8000)
interface boxesData {
    [key: number]: box[]
}

export const video_duration = $state(writable(0));
export const dataStore = writable<boxesData>({})
export const allBoxes = writable<box[]>([])
export const activeBox = writable<number>(0)
export const activeBoxFrames = writable(0)
export const validVideo = writable(0)

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

export { pages, type boxesData, box }
