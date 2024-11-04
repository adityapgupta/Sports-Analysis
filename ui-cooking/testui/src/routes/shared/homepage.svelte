<script lang='ts'>
    import Canvasimg from "../components/canvasimg.svelte";
    import Videopicker from "../components/videopicker.svelte";
    import Heatmapview from "../components/heatmapview.svelte";
    let { socket, visibility } : { socket: WebSocket, visibility:boolean } = $props();
</script>

<div id="maindiv" style="width: 100%;" class="px-3 py-3 flex-grow" style:display={visibility ? "unset" : "none"}>
    <Videopicker {socket} />
    <div class="flex flex-col xl:flex-row">
        <Canvasimg> <Heatmapview /> </Canvasimg>
    </div>
</div>

<style>
</style>