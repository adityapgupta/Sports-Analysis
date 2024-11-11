<script lang="ts">
    import { cvideo, port, dataStore, video_duration, activeBox, activeBoxFrames, validVideo, vid_prefix, posession, isBoxClicked, identifications, frameRate, currentFrame, getAppropriateColor } from "../shared/progstate.svelte";
    import * as d3 from 'd3'
    let vidobj: HTMLVideoElement;
    let vidurl = $derived(`http://localhost:${$port}/${$vid_prefix}${$cvideo}`)
    let ctime = $state(0)
    let frame = $derived(Math.floor(ctime*$frameRate))
    let isPaused = $state(false)
    let vwidth = $state(0)
    let vheight = $state(0)
    let vnatw = $state(0)
    let vnath = $state(0)
    let bWidth = $state(0)
    let drawSVG: SVGElement
    // svelte-ignore non_reactive_update
        let vidBar: HTMLInputElement
    let flr=Math.floor
    let ownershipSVG: SVGElement
    $effect(() => {
        $currentFrame = frame
        if (ctime) {
            redrawsvgelt()
        }
    })
    // svelte-ignore non_reactive_update
        let play_button:HTMLButtonElement;
    cvideo.subscribe(() => {
        if ($cvideo == vidurl || vidobj == undefined) return
        vidobj.load()
        ctime = 0
    })
    function playVideo() {
        if (vidobj) {
            if (isPaused) {
                vidobj.play()
            } else {
                vidobj.pause()
            }
        }
    }

    $effect(() => {
        if (drawSVG.clientHeight != vheight) {
            drawSVG.setAttribute('width', vwidth.toString())
            drawSVG.setAttribute('height', vheight.toString())
        }
    })

    function check_boxes(e: MouseEvent) {
        const current_frame_boxes = $dataStore[frame + 2];
        $activeBox = -2
        if (current_frame_boxes) {
            let b = current_frame_boxes.findLast(inbox => isBoxClicked(inbox, drawSVG, e.layerX, e.layerY, vnatw, vnath))
            if (b) { 
                $activeBox = b.owner
                $activeBoxFrames = b.appearedFrames
                setTimeout(redrawsvgelt, 100)
            }
        }
        play_button.focus()
        $currentFrame = frame
    }

    function redrawsvgelt() {
        const d3elt = d3.select(ownershipSVG)
            const d3xaxis = d3.scaleLinear().domain([0, $video_duration]).range([0, vidBar.clientWidth]).nice(2)
            const d3yaxis = d3.scaleLinear().domain([0, 2]).range([0, vidBar.clientHeight]).nice(2)
            d3elt.selectAll('rect').remove()
            d3elt.selectAll('rect').data($posession).join('rect')
                .attr('x', d => d3xaxis(d.start))
                .attr('width', d => d3xaxis(d.end - d.start))
                .attr('height', d3yaxis(1)).attr('y', d => d.team == "left" ? d3yaxis(0) : d3yaxis(1))
                .attr('fill', d => d.team == "left" ? "red" : "blue")

    }
</script>

{#if $validVideo == 0}
    <h2 class="text-xl self-center text-center width-full" id="video-missing-message">Please load a video to get started</h2>
{/if}
<div id="vid-container" class="relative w-fit">
    <video bind:this={vidobj} src={vidurl}
        bind:currentTime={ctime} bind:duration={$video_duration} bind:paused={isPaused}
        bind:clientHeight={vheight} bind:clientWidth={vwidth} bind:readyState={$validVideo}
        bind:videoHeight={vnath} bind:videoWidth={vnatw} onclick={check_boxes}>
        <track kind="captions" srclang="en" label="English captions" default>
        </video>
        <svg bind:this={drawSVG} viewBox="0 0 {vnatw} {vnath}" class="absolute top-0 left-0 pointer-events-none">
            <mask id="mask1">
                <rect x="-50" y="-50" width="100" height="100" fill="white" />
                <rect x="-25" y="-50" width="50" height="50" fill="black" />
            </mask>
            {#each $dataStore[frame+2] as f}
                {#if $identifications.ball_ids.includes(f.owner)}
                    <polygon fill={getAppropriateColor(f.owner)} mask="url(#mask1)" vector-effect="non-scaling-stroke"
                    points="0,0 {-flr(vnatw/80)},{-flr(vnath/40)} {flr(vnatw/80)},{-flr(vnath/40)}"
                    transform="translate({f.x+f.w/2},{f.y-5-vnatw/40})"/>
                {:else}
                    <ellipse stroke="{getAppropriateColor(f.owner)}" mask="url(#mask1)" vector-effect="non-scaling-stroke"
                        stroke-width="3px" cx=0 cy=0 ry=25 rx=45 fill="none"
                        transform="translate({f.x + f.w/2},{f.y+f.h-5}) scale({f.w/60})"/>
                {/if}
            {/each}
        </svg>
        {#if $validVideo}
            <div class="flex flex-row w-auto mt-1">
                <button bind:clientWidth={bWidth} onclick={playVideo} class="bg-orange-300 w-fit px-2 pb-0.5 pt-1 rounded-md" bind:this={play_button}>
                    <i class="material-icons">{isPaused ? "play_arrow" : "pause"}</i> </button>
                <div class="flex-grow h-auto mx-2 relative">
                    <input type='range' max={$video_duration} step="any" bind:value={ctime} bind:this={vidBar} onkeydown={playVideo} class="h-full w-full"/>
                    <svg class="absolute top-0 left-0 width-full height-full pointer-events-none -z-10"
                    viewBox="0 0 {vidBar?.clientWidth ?? 200} {vidBar?.clientHeight ?? 20}" bind:this={ownershipSVG}></svg>
                </div>
            </div>
        {/if}
    </div>

<style>
    video {
        max-height: 50vh;
    }
    #video-missing-message {
        grid-column: 1/3;
        grid-row: 2/3;
    }
</style>