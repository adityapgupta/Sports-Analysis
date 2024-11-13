export type HeatmapData = {
    "left": number[][],
    "right": number[][],
    "ball": number[][]
}

export type possessionT = {start: number, duration: number, team: "left" | "right"}[]
export type possessionTeam = {home: number, away: number}
export type possessionZone = {defense: number, attack: number, middle: number}
export type minimapData = [number, number, [number, number]][][]
export type screenData = { [key:number] : box[] }
export type box = {
    x: number,
    y: number,
    w: number,
    h: number,
    id: number
}
