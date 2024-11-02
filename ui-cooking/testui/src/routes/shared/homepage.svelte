<script lang='ts'>
    import Counter from "../components/Counter.svelte";
    import Canvasimg from "../components/canvasimg.svelte";
    import Videopicker from "../components/videopicker.svelte";
    let { socket } : { socket: WebSocket } = $props();
</script>

<div style="width: 100%;" class="px-3 py-3">
    <Videopicker {socket} />
    <Canvasimg />
    <Counter />
</div>