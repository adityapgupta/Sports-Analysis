<script lang="ts">
    import * as d3 from "d3";
    import { onMount } from "svelte";
    import { video_duration } from "../shared/progstate.svelte";
    const {
        line_data = $bindable(),
        header,
    }: { line_data: [number, number][]; header: string } = $props();
    let linePlot: SVGElement;

    const height = 200;
    const width = 300;
    const lbord = 40;
    const rbord = 20;
    const tbord = 20;
    const bbord = 40;
    const w = width - lbord - rbord;
    const h = height - tbord - bbord;
    const xaxis = $derived.by(() => {
        let range = (isNaN($video_duration) ?  d3.max(line_data, d => d[0]) : $video_duration) ?? 10
        return d3
            .scaleLinear()
            .domain([0, range])
            .range([lbord, width - rbord])
            .nice()
    });
    const yaxis = $derived.by(() => {
        let range = d3.max(line_data, d => d[1]) ?? 10
        return d3
            .scaleLinear()
            .domain([0, range])
            .range([height - bbord, tbord])
            .nice(5)
    });

    onMount(() => {
        $effect(() => {
            let d3svg = d3.select(linePlot);
            const line = d3
                .line()
                .x((d) => xaxis(d[0]))
                .y((d) => yaxis(d[1]))
                .curve(d3.curveBasis);
            d3svg.selectChildren().remove();

            const path = d3svg
                .append("path")
                .datum(line_data)
                .attr("fill", "none")
                .attr("stroke", "steelblue")
                .attr("d", line).attr("opacity", 0);
            
            
            requestAnimationFrame(() => {
                const pathNode = path.node() as SVGPathElement
                const pathLength = pathNode.getTotalLength()
                path.attr("opacity", 1)
                .attr("stroke-dasharray", pathLength)
                .attr("stroke-dashoffset", pathLength)
                .transition().ease(d3.easeCubic).duration(2000).attr('stroke-dashoffset', 0);
    
                d3svg
                    .append("g")
                    .attr("transform", `translate(0, ${height - bbord})`)
                    .call(d3.axisBottom(xaxis).ticks(7));
    
                d3svg
                    .append("g")
                    .attr("transform", `translate(${lbord}, 0)`)
                    .call(d3.axisLeft(yaxis).ticks(5));
            })
        });
    });
</script>
<div class="flex flex-grow flex-col items-center m-2 p-1">
    <h2>{header}</h2>
    <div class="svg_container">
        <svg viewBox="0 0 300 200" bind:this={linePlot}> </svg>
    </div>
</div>

<style>
    .svg_container {
        width: min(100%, 600px);
    }
</style>