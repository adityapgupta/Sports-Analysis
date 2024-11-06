<script lang="ts">
    import { activeBox, activeBoxFrames, player_data } from "../shared/progstate.svelte";
    let heatmapContainer:HTMLDivElement;
    let pd = $derived.by(() => get_player($activeBox))
    function get_player(val: string | number) {
        for (let i of $player_data) {
            if (val == i[0]) {
                return [i[1], i[2]]
            } 
        }
        return ["", ""]
    }
</script>


<div bind:this={heatmapContainer} class="flex-grow xl:flex-grow-0">
    The current active player is {$activeBox}, appears in {$activeBoxFrames} frames. Their name is {pd[0]} and jersey number is {pd[1]}
</div>
