<script lang="ts" >
    import { setContext } from "svelte";
    let { socket, visibility }: { socket: WebSocket, visibility: Boolean } = $props()

    import Heatmap from "../components/Heatmap.svelte";
    import Lineplot from "../components/Lineplot.svelte";
    let heatmapdata: {"left-team": number[][], "right-team": number[][], "ball": number[][]} = $state({
        'left-team': [],
        'right-team': [],
        'ball': []
    })
    let getHeatmapData = async function() {
        heatmapdata = {'left-team': [], 'right-team': [], 'ball': []}
        await socket.send(JSON.stringify({
            type: "getHeatmapData"
        }))
    }

    socket.addEventListener('message', m => {
        const data = JSON.parse(m.data)
        if (data.type == "heatmapData") {
            console.log(data)
            heatmapdata = data.data
        }
    })

    $effect(() => {
        if (visibility) {
            getHeatmapData()
            // setlinedata()
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
    $inspect(heatmapdata)
</script>

<div class="analytics-page grid-cols-1 xl:grid-cols-2" style:display={visibility ? "grid":"none"}>
    <Heatmap header="Left team heatmap" heatmap_data={heatmapdata["left-team"]}/>
    <Heatmap header="Right team heatmap" heatmap_data={heatmapdata["right-team"]}/>
    <Heatmap header="Ball heatmap" heatmap_data={heatmapdata["ball"]}/>
    <Lineplot header="Lineplot" {line_data} /> 
</div>

<button onclick={() => {setlinedata(); getHeatmapData()}} class="p-1 border-2 m-2 flex-shrink">Get data</button>

<style>
</style>