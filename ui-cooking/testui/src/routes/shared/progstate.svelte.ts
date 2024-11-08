import { writable, get } from "svelte/store"
enum pages {
    HOME = "page-1",
    PLAYERS_LIST = "page-2"
}

export let currentPage = writable(pages.HOME)
export let currentFile = writable("")
export let cvideo = writable("")
export let vid_prefix = writable("")
export let port = writable(8000)
export let player_data = $state(writable<Array<[string, string, string]>>([]))
export let video_duration = $state(writable(0));
export let dataStore = writable<boxesData>({})
export let allBoxes = writable<box[]>([])
export let activeBox = writable<number>(0)
export let activeBoxFrames = writable(0)
export let validVideo = writable(0)
export let balls= writable<number[]>([])

interface boxesData {
    [key: number]: box[]
}
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

const leeway = 20;
export const isBoxClicked = function(inbox: box, svgelt: SVGElement, clickx: number, clicky: number, vidx: number, vidy: number) {
    let [svgw, svgh] = [svgelt.clientWidth, svgelt.clientHeight]
    let [t_clickx, t_clicky] = [clickx*vidx/svgw, clicky*vidy/svgh]
    return t_clickx >= inbox.x-leeway && t_clickx <= inbox.x + inbox.w+leeway && t_clicky >= inbox.y-leeway && t_clicky <= inbox.y + inbox.h+leeway
}

export { pages, type boxesData, box }
