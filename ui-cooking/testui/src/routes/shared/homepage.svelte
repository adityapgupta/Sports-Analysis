<script lang='ts'>
    import Videodrawing from "../components/Videodrawing.svelte";
    import Videopicker from "../components/videopicker.svelte";
    import Playerplot2d from "../components/playerplot2d.svelte";

    let { socket, visibility } : { socket: WebSocket, visibility:boolean } = $props();
</script>

<div style="width: 100%;" class="homepagecontainer px-3 py-3 flex-grow"
    style:display={visibility ? "block" : "none"} style:opacity={visibility ? 1 : 0}>
    <Videopicker {socket} />
    <div class="grid grid-cols-1 justify-items-center flex-grow gap-4 p-2 xl:grid-cols-2">
        <Videodrawing {socket}/>
        <Playerplot2d {socket} />
    </div>
</div>

<style>
    .homepagecontainer {
        transition: opacity 5s;
    }
</style>