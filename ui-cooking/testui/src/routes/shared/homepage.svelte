<script lang='ts'>
    import Canvasimg from "../components/canvasimg.svelte";
    import Videopicker from "../components/videopicker.svelte";
    import Analytics from "./analytics.svelte";
    let { socket, visibility } : { socket: WebSocket, visibility:boolean } = $props();
    import ico1 from '$lib/images/1156910.jpg' 
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
        transition: opacity 5s;
    }
/* 
    add picture to the background */
    .homepagecontainer {
        /* background-image: add it from the assets folder; */
        background-image: image('/home/sahilc/Desktop/Soccer Analysis Project/Sports-Analysis/ui-cooking/testui/src/assets/1156910.jpg');
        background-size: cover;
        background-repeat: no-repeat;
        background-position: center;
    }

</style>