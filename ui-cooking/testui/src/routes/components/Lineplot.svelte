<script lang="ts">
    import * as d3 from 'd3'
    const { line_data, header }: { line_data: [number, number][], header: string} = $props()
    let linePlot: SVGElement

    
</script>

<h2>{header}</h2>
<div class="svg_container">
    <svg viewBox="0 0 200 100" bind:this={linePlot}>

    </svg>
</div>