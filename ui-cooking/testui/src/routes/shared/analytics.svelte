<script lang="ts" >
    import { setContext } from "svelte";
    let { socket, visibility }: { socket: WebSocket, visibility: Boolean } = $props()
    import { posession as posstate } from "../shared/progstate.svelte";
    import Heatmap from "../components/Heatmap.svelte";
    import Lineplot from "../components/Lineplot.svelte";
    import Pieplot from "../components/pieplot.svelte";
    import Boxgraph from "../components/boxgraph.svelte";
    import Barplot from "../components/barplot.svelte";
    import type { HeatmapData } from "./types";

    let heatmapdata: HeatmapData = $state({
        'left': [],
        'right': [],
        'ball': []
    })

    let posession: {start: number, duration: number, color: "left-team" | "right-team"}[] = $state([])
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
            posession = data.data
            $posstate = posession
        } else if (data.type == "otherPosessionData") {
            otherPosessionData = data.data
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

<div class="analytics-page items-center grid-cols-1 xl:grid-cols-2" style:display={visibility ? "grid":"none"}>
    <Heatmap header="Left team heatmap" heatmap_data={heatmapdata["left-team"]}/>
    <Heatmap header="Right team heatmap" heatmap_data={heatmapdata["right-team"]}/>
    <Heatmap header="Ball heatmap" heatmap_data={heatmapdata["ball"]}/>
    <Boxgraph {posession} />
    <Pieplot piedata={otherPosessionData.team_posession} />
    <!-- <Barplot bardata={otherPosessionData.zone_posession} /> -->
    <button onclick={() => {setlinedata(); getGraphsData()}} class="p-1 border-2 m-2 flex-shrink xl:col-span-2">Refresh data</button>
</div>

<style>
</style>