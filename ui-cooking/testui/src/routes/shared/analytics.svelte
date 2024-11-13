<script lang="ts" >
    let { socket, visibility }: { socket: WebSocket, visibility: Boolean } = $props()
    import { posession as posstate } from "../shared/progstate.svelte";
    import Heatmap from "../components/Heatmap.svelte";
    import Pieplot from "../components/pieplot.svelte";
    import Boxgraph from "../components/boxgraph.svelte";
    import type { HeatmapData, possessionT, possessionTeam, possessionZone } from "./types";
    import Barplot from "../components/barplot.svelte";

    let heatmapdata: HeatmapData = $state({
        'left': [],
        'right': [],
        'ball': []
    })

    let posession: possessionT = $state([])
    let teamPosession: possessionTeam = $state({home: 10, away: 10})
    let zonePosession: possessionZone = $state({defense: 0, middle: 0, attack: 0})

    let otherPosessionData: {team_posession: any, zone_posession: any} =
        $state({team_posession: {}, zone_posession: {}})
    let getGraphsData = async function() {
        heatmapdata = {'left': [], 'right': [], 'ball': []}
        socket.send(JSON.stringify({
            type: "getHeatmapData"
        }))
        socket.send(JSON.stringify({
            type: "getLinemapData"
        }))
        socket.send(JSON.stringify({
            type: "getPosessionData"
    }))}

    socket.addEventListener('message', m => {
        const data = JSON.parse(m.data)
        if (data.type == "heatmapData") {
            heatmapdata = {
                'left': data.data['left-team'],
                'right': data.data['right-team'],
                'ball': data.data['ball']
            }
        } else if (data.type == "posessionData") {
            const indata = data.data
            console.log(indata.time_possession)
            posession = indata.time_possession.map((d: any) => {
                return {
                    start: d.start,
                    duration: d.duration,
                    team: d.color == "left-team" ? "left" : "right"
                }
            })
            teamPosession = indata.team_possession
            zonePosession = indata.zone_possession
            $posstate = posession
        }
    })

    $effect(() => {
        if (visibility) {
            getGraphsData()
        }
    })


    let line_data: [number, number][] = $state([])
    
    function setlinedata() {
        let min = 0
        let max = 30
        line_data=[]
        for (let i = 0; i < max; i++) {
            line_data.push([i, min + (Math.random()*(max-min))/2])
    
            const lastElement = line_data.at(-1);
            if (lastElement) {
                min = lastElement[1] as number;
            }
        }
    }

</script>

<div class="analytics-page items-center gap-2 grid-cols-1 xl:grid-cols-2" style:display={visibility ? "grid":"none"}>
    <Heatmap header="Left team heatmap" heatmap_data={heatmapdata["left"]}/>
    <Heatmap header="Right team heatmap" heatmap_data={heatmapdata["right"]}/>
    <Heatmap header="Ball heatmap" heatmap_data={heatmapdata["ball"]}/>
    <Boxgraph {posession} />
    <!-- <Pieplot piedata={teamPosession} /> -->
    <Barplot bardata={zonePosession} header="Zone posession"/>
    <Barplot bardata={teamPosession} header="Team posession"/>
    <button onclick={() => {setlinedata(); getGraphsData()}} class="p-1 border-2 m-2 flex-shrink xl:col-span-2">Refresh data</button>
</div>

<style>
</style>