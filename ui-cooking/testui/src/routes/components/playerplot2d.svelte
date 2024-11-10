<script lang="ts">
    import footballimg from '$lib/images/Football_field.svg';
    import { onMount } from 'svelte';
    import { validVideo, dataStore_2d, currentFrame, getAppropriateColor, identifications, activeBox } from '../shared/progstate.svelte';
    import * as d3 from 'd3'
    // svelte-ignore non_reactive_update
        let svgelt: SVGElement
    const data = $derived($dataStore_2d[$currentFrame])
    let d3svg: d3.Selection<SVGElement, unknown, null, undefined>
    onMount(() => {
        $effect(() => {
            d3svg = d3.select(svgelt)
            if (data) {
                d3svg.selectAll('circle').remove()
                d3svg.selectAll('circle').data(data).join('circle')
                    .attr('cx', d => d[2][0])
                    .attr('cy', d => d[2][1])
                    .attr('r', d => $identifications.ball_ids.includes(d[0]) ? 2 : 1)
                    .attr('fill', d => getAppropriateColor(d[0]))
                console.log(d3svg.selectAll('circle'))
            }
        })
    })

</script>

{#if $validVideo}
<div class="mapcontainer">
    <img class="fieldimg" src={footballimg} alt="2d map view"/>
    <svg bind:this={svgelt} class="absolute width-full height-full top-0 left-0" viewBox="0 0 105 68">

    </svg>
</div>
{/if}
<input bind:value={$activeBox} type="text" id="activeBox" />

<style>
    .fieldimg {
        background-color: #0a0;
        width: 100%;
        height: 100%;
    }
    .mapcontainer {
        position: relative;
        align-self: center;
        padding: 20px;
        aspect-ratio: 105/68;
        /* height: min(100%, 400px); */
        width: min(100%, 800px);
        flex-shrink: 1;
        background-color: #0a0;
        padding: 4px;
    }
</style>