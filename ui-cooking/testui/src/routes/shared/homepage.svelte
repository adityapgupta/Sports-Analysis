<script lang='ts'>
    import Counter from "../components/Counter.svelte";
    import Canvasimg from "../components/canvasimg.svelte";
    import Videopicker from "../components/videopicker.svelte";
    import Heatmapview from "../components/heatmapview.svelte";
    let { socket } : { socket: WebSocket } = $props();
</script>

<div style="width: 100%;" class="px-3 py-3 flex-grow">
    <Videopicker {socket} />
    <div class="flex flex-col xl:flex-row">
        <Canvasimg> <Heatmapview /> </Canvasimg>
    </div>
    <Counter />
</div>

<style>
    /* @media (min-width: 1200px) {
        .canvasheatmap {
            flex-direction: column;
        }
    } */
</style>