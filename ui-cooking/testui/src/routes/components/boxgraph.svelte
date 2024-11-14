<script lang="ts">
    import type { possessionT } from '../shared/types';
    const { posession }: { posession: possessionT } = $props()
    import * as d3 from 'd3'
    import { video_duration } from '../shared/progstate.svelte';
    import { onMount } from 'svelte';
    let svgElt: SVGElement

    
    const xmax = $derived($video_duration ?? 10)
    const xaxis = $derived(d3.scaleLinear().domain([0, xmax]).range([0, 200]))
    const evaluatedxmax = $derived(xaxis.domain().at(-1) || 10)

    onMount(() => {
        $effect(() => {
            const svg = d3.select(svgElt)
            svg.selectChildren().remove()
            svg.selectChildren('rect')
                .data(posession)
                .join('rect').attr('height', 20).attr('x', d => xaxis(d.start))
                .attr('width', d => xaxis(d.duration))
                .attr('fill', d => d.team == "right" ? "red" : "blue")
                .attr('mask', 'url(#mask1)')

            svg.append("text").text(`${evaluatedxmax}s`).attr('x', 200).attr('fill', 'black')
                .attr("y", 30)
                .attr('font-size', 6).attr('text-anchor', 'end')
            
            svg.append("text").text(`0s`).attr('x', 0).attr('fill', 'black')
                .attr("y", 30).attr('font-size', 6)
            svg.append('rect').attr('x', 0).attr('y', 0).attr('width', 200).attr('height', 20)
                .attr('fill', 'none').attr('stroke', 'black')
        })
    })
</script>

<div class="w-full flex flex-col items-center p-3 px-6">
    <h2 class="text-xl text-center p-2">Posession over time</h2>
    <div class="svg-container">
        <svg viewBox="0 0 200 40" bind:this={svgElt}>
            
        </svg>
    </div>
</div>

<style>
    .svg-container {
        width: min(100%, 600px);
    }
</style>