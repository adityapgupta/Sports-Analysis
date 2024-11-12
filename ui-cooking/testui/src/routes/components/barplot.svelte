<script lang="ts">
    const { bardata }: { bardata: { "attacking": number, "defenasive": number, "middle": number }} = $props()
    import * as d3 from 'd3'
    import { onMount } from 'svelte';
    let svgelt: SVGElement;

    onMount(() => {
        $effect(() => {
            const margin = { top: 20, right: 30, bottom: 40, left: 90 };
            const width = 460 - margin.left - margin.right;
            const height = 400 - margin.top - margin.bottom;

            const svg = d3.select(svgelt)
                .attr("width", width + margin.left + margin.right)
                .attr("height", height + margin.top + margin.bottom)
                .append("g")
                .attr("transform", `translate(${margin.left},${margin.top})`);

            const data = [
                { category: "attacking", value: bardata.attacking },
                { category: "defenasive", value: bardata.defenasive },
                { category: "middle", value: bardata.middle }
            ];

            const x = d3.scaleLinear()
                .domain([0, d3.max(data, d => d.value) ?? 10])
                .range([0, width]);

            const y = d3.scaleBand()
                .range([0, height])
                .domain(data.map(d => d.category))
                .padding(0.1);

            svg.append("g")
                .call(d3.axisLeft(y));

            svg.selectAll("myRect")
                .data(data)
                .enter()
                .append("rect")
                .attr("x", x(0))
                .attr("y", (d, i) => i*200)
                .attr("width", d => x(d.value))
                .attr("height", y.bandwidth())
                .attr("fill", "#69b3a2");
        })
    })
</script>

<div class="w-ful h-full flex-col items-center">
    <h2 class="text-2xl text-center">Posession data</h2>
    <svg bind:this={svgelt} viewBox="0 0 400 400"></svg>
</div>