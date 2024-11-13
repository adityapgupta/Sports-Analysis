<script lang="ts">
    import type { possessionZone, possessionTeam } from '../shared/types';
    const { bardata, header }: { bardata: possessionZone | possessionTeam, header: string } = $props()
    import * as d3 from 'd3'
    import { onMount } from 'svelte';
    let svgelt: SVGElement;

    onMount(() => {
        $effect(() => {
            const margin = { top: 20, right: 30, bottom: 40, left: 90 };
            const width = 400 - margin.left - margin.right;
            const height = 300 - margin.top - margin.bottom;

            const svg = d3.select(svgelt)
            svg.selectChildren().remove()

            const x = d3.scaleLinear()
                .domain([0, d3.max(Object.values(bardata)) as number])
                .range([0, width]);

            const y = d3.scaleBand()
                .domain(Object.keys(bardata))
                .range([0, height])
                .padding(0.1);
            
            const g = svg.append("g")
                .attr("transform", `translate(${margin.left},${margin.top})`);
            
            g.append("g")
                .attr("class", "x-axis")
                .call(d3.axisBottom(x))
                .attr("transform", `translate(0,${height})`);
            g.append("g")
                .attr("class", "y-axis")
                .call(d3.axisLeft(y));
            
            svg.selectAll("rect").data(Object.entries(bardata))
                .join("rect")
                .attr("x", margin.left)
                .attr("y", d => margin.top + (y(d[0]) ?? 10))
                .attr("width", d => (x(d[1]) ?? 10))
                .attr("height", y.bandwidth())
                .attr("fill", "steelblue");

        })
    })
</script>

<div class="w-ful h-full flex-col items-center">
    <h2 class="text-xl text-center">{header}</h2>
    <svg bind:this={svgelt} viewBox="0 0 400 300"></svg>
</div>