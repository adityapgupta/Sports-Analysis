<script lang='ts'>
    import Canvasimg from "../components/canvasimg.svelte";
    import Videopicker from "../components/videopicker.svelte";
    import Analytics from "./analytics.svelte";
    let { socket, visibility } : { socket: WebSocket, visibility:boolean } = $props();
</script>

<div style="width: 100%;" class="homepagecontainer px-3 py-3 flex-grow"
    style:display={visibility ? "block" : "none"} style:opacity={visibility ? 1 : 0}>
    <Videopicker {socket} />
    <div class="flex flex-col transition-opacity xl:flex-row">
        <Canvasimg />
    </div>
</div>

<style>
    .homepagecontainer {
        transition: opacity 1s;
    }
</style>