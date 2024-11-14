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

export type PassingLane = {
    start_pos: [number, number],
    end_pos: [number, number],
    distance: number
    interceptors: [number, number][] // (player id: int, distance: float)
    success_probability: number
    risk_score: number
    reward_score: number
    total_score: number
}

export type PassingOppurtunity = {
    passer_id: number
    receiver_id: number
    lane: PassingLane
    defensive_pressure: number
    horizontal_progress: number
    space_gained: number
    timestamp: number
}

export type displayQuads = [[number, number], [number, number], [number, number], [number, number]][]