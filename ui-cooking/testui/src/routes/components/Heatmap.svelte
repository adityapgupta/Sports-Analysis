<script lang="ts">
    import * as d3 from "d3";
    import { getContext, onMount } from "svelte";
    const { heatmap_data, header }: { heatmap_data: number[][], header: string } = $props()

    let heatmapView: SVGElement
    const ROWS = $derived(heatmap_data[0]?.length || 15)
    const COLUMNS = $derived(heatmap_data.length || 10)
    const anim_delay = 80
    let rectw = $derived(105/ROWS)
    let recth = $derived(68/COLUMNS)
    onMount(() => {
        $effect(() => {
            d3.select(heatmapView).selectAll("g").data(heatmap_data)
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
        background-color: #0a0;
        padding: 4px;
    }
    :global(rect.heatmap_rects) {
        fill: red;
        mix-blend-mode: color;
    }
</style>