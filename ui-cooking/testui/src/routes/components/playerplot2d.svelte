<script lang="ts">
    import footballimg from '$lib/images/Football_field.svg';
    import type { displayQuads, PassingOppurtunity } from '../shared/types';
    import { onMount } from 'svelte';
    import { validVideo, dataStore_2d, configuration, currentFrame, getAppropriateColor, identifications, activeBox } from '../shared/progstate.svelte';
    import * as d3 from 'd3'
    let { socket }: { socket: WebSocket } = $props()
    // svelte-ignore non_reactive_update
    let svgelt: SVGElement
    const data = $derived($dataStore_2d[$currentFrame])
    const drawVoronoi = $derived($configuration.drawVoronoi)
    let passes: PassingOppurtunity[] = $state([])
    let bestPass: PassingOppurtunity | null = $state(null)
    let quads: displayQuads = $state([])

    // socket.addEventListener('message', (event) => {
    //     const data = JSON.parse(event.data)
    //     if (data.type === 'passData') {
    //         console.log(data)
    //         const d = data.data as [PassingOppurtunity[], PassingOppurtunity | null]
    //         passes = d[0]
    //         bestPass = d[1]
    //     }
    // })

    socket.addEventListener('message', msg => {
        const data = JSON.parse(msg.data)
        if (data.type === '2dMap') {
            console.log(data)
            quads = data.quad
            console.log($state.snapshot(quads))
        }
    })

    let d3svg: d3.Selection<SVGElement, unknown, null, undefined>
    const lplayers = $derived.by(() => {
        return data?.filter(d => $identifications.left_team.includes(d[0])) ?? []
    })
    const rplayers = $derived.by(() => {
        return data?.filter(d => $identifications.right_team.includes(d[0])) ?? []
    })
    const allplayers = $derived([...lplayers, ...rplayers])
    const delaunay = $derived(d3.Delaunay.from([...lplayers, ...rplayers], d => d[2][0], d => d[2][1]))
    const voronoi = $derived(delaunay.voronoi([0, 0, 105, 68]))
    const xaxis = d3.scaleLinear().domain([0, 1]).range([0, 105])
    const yaxis = d3.scaleLinear().domain([0, 1]).range([0, 68])
    let tmp = $derived($activeBox)
    onMount(() => {
        $effect(() => {
            if (tmp) {
                let x = tmp
            }
            d3svg = d3.select(svgelt)
            if (data) {
                d3svg.selectAll('path').remove()
                d3svg.selectAll('circle').remove()

                if (drawVoronoi){
                    d3svg.selectAll('path').data(voronoi.cellPolygons()).join('path')
                        .attr('d', d => d ? `M${d.join('L')}Z` : null)
                        .attr('fill', 'none').attr('transform', 'scale(105, 68)')
                        .attr('stroke', 'black')
                        .attr('stroke-width', 0.5)
                        .data(allplayers).attr('opacity', 0.3)
                        .attr('mix-blend-mode', 'color')
                        .attr('stroke', 'none')
                        .attr('fill', d => lplayers.includes(d) ? 'red' : 'blue')
                }
                d3svg.selectAll('circle').data(data).join('circle')
                    .attr('cx', d => xaxis(d[2][0]))
                    .attr('cy', d => yaxis(d[2][1]))
                    .attr('r', d => $identifications.ball_ids.includes(d[0]) ? 0.8 : 1)
                    .attr('stroke', d => $identifications.ball_ids.includes(d[0]) ? "black" : "none")
                    .attr('stroke-width', 0.2)
                    .attr('fill', d => getAppropriateColor(d[0]))
            }
        })
    })

</script>

{#if $validVideo}
<div class="mapcontainer">
    <img class="fieldimg" src={footballimg} alt="2d map view"/>
    <svg bind:this={svgelt} class="absolute width-full height-full top-0 left-0" viewBox="0 0 105 68">
        {#if quads[$currentFrame]}
            <polygon points={quads[$currentFrame].map(d => `${d[0]*105},${d[1]*68}`).join(' ')}
                fill = "white" opacity=0.3 style="mix-blend-mode: lighten"/>
        {/if}
    </svg>
</div>
{/if}

<style>
    .fieldimg {
        /* background-color: #ac7; */
        width: 100%;
        height: 100%;
    }
    .mapcontainer {
        position: relative;
        align-self: center;
        padding: 20px;
        aspect-ratio: 105/68;
        width: min(100%, 800px);
        flex-shrink: 1;
        background-color: #371;
        padding: 4px;
    }
</style>