<script lang="ts">
    import { configuration } from "./progstate.svelte";
    const { visibility } = $props()
</script>
<div class="m-3 p-3" style:display={visibility ? "block" : "none"}>
    <label for="draw_voronoi">Draw voronoi on 2d chart</label>
    <input type="checkbox" bind:checked={$configuration.drawVoronoi} class="m-2" name="draw_voronoi"/>
</div>