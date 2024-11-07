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
export let balls = $state(writable<Array<number>>([]))
export let video_duration = $state(writable(0));
export let dataStore = writable<boxesData>({})
export let allBoxes = writable<box[]>([])
export let activeBox = writable<number>(0)
export let activeBoxFrames = writable(0)
export let validVideo = writable(0)

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


export const drawObjects = function(inbox: box, svgelt: SVGElement, isBall: boolean, isSelected = false) {
    let { x, y, w, h } = inbox
    if (isBall) {
        let ballMarker = document.createElementNS("http://www.w3.org/2000/svg", 'polygon')
        ballMarker.setAttribute("points", `${x+w/2},${y} ${x+w/2-15},${y-15} ${x+w/2 + 15},${y-15}`)
        isSelected ? ballMarker.setAttribute("fill", "skyblue"): ballMarker.setAttribute("fill", "yellow")
        ballMarker.setAttribute("stroke", "none")
        svgelt.appendChild(ballMarker)
    } else {
        let playerMarker = document.createElementNS('http://www.w3.org/2000/svg', 'path')
        playerMarker.setAttribute('d', `M ${x+w/2} ${y+h} m ${-w/2} ${-w/2} q ${-w/3} ${w/6} ${-w/3} ${w/2}
            q ${w/6} ${w/3} ${5*w/6} ${w/3} q ${2*w/3} 0 ${5*w/6} ${-w/3} q 0 ${-w/3} ${-w/3} ${-w/2}`)
        playerMarker.setAttribute("fill", "none")
        isSelected ? playerMarker.setAttribute("stroke", "lightpink") : playerMarker.setAttribute("stroke", "red")
        playerMarker.setAttribute("stroke-width", "3px")
        svgelt.appendChild(playerMarker)
        // the curve goes like
        //       _      _
        //      /         \
        //     |     .     |
        //      \         /
        //        ‾‾‾‾‾‾‾
        // where the . is the bottom middle
    }
}

export { pages, type boxesData, box }
