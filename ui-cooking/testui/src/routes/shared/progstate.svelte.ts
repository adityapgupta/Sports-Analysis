import { writable, get, type Writable } from "svelte/store"
import type { screenData, box, minimapData, possessionT } from "./types"

export enum pages {
    MAIN_HOME = "landing",
    HOME = "page-1",
    ANALYTICS = "page-3",
    TEAM = "team",
    SETTINGS = "settings",
}

export let currentPage = writable(pages.MAIN_HOME)
export let frameRate = $state(writable(25))
export let currentFile = $state(writable(""))
export let currentFrame = $state(writable(0))
export let cvideo = writable("")
export let vid_prefix = writable("")
export let port = writable(8000)
export let video_duration = $state(writable(0));
export let dataStore = writable<screenData>({})
export let allBoxes = writable<box[]>([])
export let activeBox = writable<number>(0)
export let validVideo = writable(0)
export let posession: Writable<possessionT> = writable([])
export let identifications = $state(writable({
    player_ids: [-2],
    ball_ids: [-2],
    left_team: [-2],
    right_team: [-2],
    referee: [-2]
}))
export let dataStore_2d: Writable<minimapData> = $state(writable([]))

const leeway = 20;
export const isBoxClicked = function(inbox: box, svgelt: SVGElement, clickx: number, clicky: number, vidx: number, vidy: number) {
    let [svgw, svgh] = [svgelt.clientWidth, svgelt.clientHeight]
    let [t_clickx, t_clicky] = [clickx*vidx/svgw, clicky*vidy/svgh]
    return t_clickx >= inbox.x-leeway && t_clickx <= inbox.x + inbox.w+leeway && t_clicky >= inbox.y-leeway && t_clicky <= inbox.y + inbox.h+leeway
}

export const getAppropriateColor = function(tracking_id: number) {
    if (tracking_id == get(activeBox)) {
        return "yellow"
    } else if (get(identifications).ball_ids.includes(tracking_id)) {
        return "white"
    } else if (get(identifications).left_team.includes(tracking_id)) {
        return "#FF1493"
    } else if (get(identifications).right_team.includes(tracking_id)) {
        return "#00BFFF"
    } else if (get(identifications).referee.includes(tracking_id)) {
        return "#bfb"
    } else {
        return "black"
    }
}

export const configuration = $state(writable({
    drawVoronoi: false
}))