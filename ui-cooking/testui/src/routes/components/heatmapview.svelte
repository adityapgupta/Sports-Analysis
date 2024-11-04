<script lang="ts">
    import { activeBox, activeBoxFrames } from "../shared/progstate.svelte";
    let heatmapContainer:HTMLDivElement;
</script>


<div bind:this={heatmapContainer} class="flex-grow xl:flex-grow-0" style="width: 600px; height:400px">
    The current active player is {$activeBox}, appears in {$activeBoxFrames} frames
</div>
