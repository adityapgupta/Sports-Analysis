<script lang="ts" >
    import { setContext } from "svelte";
    let { socket, visibility }: { socket: WebSocket, visibility: Boolean } = $props()

    import Heatmap from "../components/Heatmap.svelte";
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
        }
    })

    $inspect(heatmapdata)
</script>

<div class="analytics-page grid-cols-1 xl:grid-cols-2" style:display={visibility ? "grid":"none"}>
    <Heatmap header="Left team heatmap" heatmap_data={heatmapdata["left-team"]}/>
    <Heatmap header="Right team heatmap" heatmap_data={heatmapdata["right-team"]}/>
    <Heatmap header="Ball heatmap" heatmap_data={heatmapdata["ball"]}/>
</div>

<!-- <button onclick={getHeatmapData} class="p-1 border-2 m-2 flex-shrink">Get heatmap data</button> -->

<style>
</style>