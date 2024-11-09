<script lang="ts">
    import { select, transition } from "d3";
    import { getContext, onMount } from "svelte";
    const { heatmap_data, header }: { heatmap_data: number[][], header: string } = $props()
    const NUM_BOXES = [40, 30]
    let heatmapView: SVGElement
    const ROWS = 15
    const COLUMNS = 10
    const anim_delay = 80
    let rectw = 105/ROWS
    let recth = 68/COLUMNS
    onMount(() => {
        $effect(() => {
            select(heatmapView).selectAll("g").data(heatmap_data)
                .join("g").attr("transform", (d, i) => `translate(0, ${i*recth})`)
                .selectAll('rect').data(d => d).join('rect').attr('opacity', 0)
                .attr('width', rectw).attr('height', recth)
                .attr("x", (d, i) => (i-1)*rectw).transition().delay((d, i) => anim_delay*i).duration(anim_delay)
                .attr("x", (d, i) => i*rectw)
                .attr('opacity', d => d).attr('class', 'heatmap_rects')
        })
    })
</script>

<div class="analytics-content flex flex-col flex-grow items-center m-2 p-1">
    <h2>{header}</h2>
    <div class="svg-container">
        <svg viewBox="0 0 105 68" class="heatmap-svg" bind:this={heatmapView}>
        </svg>
    </div>
</div>

<style>
    .heatmap-svg {
        background-image: url($lib/images/Football_field.svg);
        background-size: 100% 100%;
    }
    .svg-container {
        width: min(100%, 600px);
        flex-shrink: 1;
        background-color: #00b000;
        padding: 4px;
    }
    :global(rect.heatmap_rects) {
        fill: red;
        mix-blend-mode: color;
    }
</style>