<script lang="ts">
    const { piedata }: { piedata: { "home": number, "away": number }} = $props()
    import * as d3 from 'd3'
    import { onMount } from 'svelte';
    let svgelt: SVGElement;

    const parsedData = $derived([piedata.home, piedata.away])
    onMount(() => {
        $effect(() => {
            let d3svg = d3.select(svgelt)
            const r = 10
            const px = 15
            const pie = d3.pie()
            const arc = pie(parsedData)
            d3svg.selectAll('path')
                .data(arc).join('path')
                .attr('d', (d: any) => d3.arc().innerRadius(0).outerRadius(r)(d))
                .attr('fill', (d, i) => i == 0 ? "#a00000": "#0000a0")
                .attr('stroke', 'black').attr('transform', `translate(${px}, ${px})`)
                .attr('stroke-width', 0.4)

        })
    })
</script>

<div class="w-ful h-full flex-col items-center">
    <h2 class="text-xl text-center">Posession data</h2>
    <svg bind:this={svgelt} viewBox="0 0 30 30"></svg>
</div>