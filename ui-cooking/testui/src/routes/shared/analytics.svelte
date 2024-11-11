<script lang="ts" >
    import { setContext } from "svelte";
    let { socket, visibility }: { socket: WebSocket, visibility: Boolean } = $props()
    import { posession as posstate } from "../shared/progstate.svelte";
    import Heatmap from "../components/Heatmap.svelte";
    import Lineplot from "../components/Lineplot.svelte";
    import Boxgraph from "../components/boxgraph.svelte";

    let heatmapdata: {"left-team": number[][], "right-team": number[][], "ball": number[][]} = $state({
        'left-team': [],
        'right-team': [],
        'ball': []
    })

    let linemapdata: {"left-team": [number, number][], "right-team": [number, number][], "ball": [number, number][]} = $state({
        'left-team': [],
        'right-team': [],
        'ball': []
    })
    let posession: {start: number, end: number, team: "left" | "right"}[] = $state([])

    let getGraphsData = async function() {
        heatmapdata = {'left-team': [], 'right-team': [], 'ball': []}
        await socket.send(JSON.stringify({
            type: "getHeatmapData"
        }))
        await socket.send(JSON.stringify({
            type: "getLinemapData"
        }))
        await socket.send(JSON.stringify({
            type: "getPosessionData"
    }))}

    socket.addEventListener('message', m => {
        const data = JSON.parse(m.data)
        if (data.type == "heatmapData") {
            heatmapdata = data.data
        } else if (data.type == "linemapData") {
            linemapdata = data.data
        } else if (data.type == "posessionData") {
            posession = data.data
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

<div class="analytics-page grid-cols-1 xl:grid-cols-2" style:display={visibility ? "grid":"none"}>
    <Heatmap header="Left team heatmap" heatmap_data={heatmapdata["left-team"]}/>
    <Heatmap header="Right team heatmap" heatmap_data={heatmapdata["right-team"]}/>
    <Heatmap header="Ball heatmap" heatmap_data={heatmapdata["ball"]}/>
    <Lineplot header="Lineplot" line_data={linemapdata['ball']} /> 
    <Boxgraph {posession} />
    <button onclick={() => {setlinedata(); getGraphsData()}} class="p-1 border-2 m-2 flex-shrink xl:col-span-2">Refresh data</button>
</div>

<style>
</style>