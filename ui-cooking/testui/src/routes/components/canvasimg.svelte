<script lang="ts">
    import { cvideo, port, dataStore, video_duration, activeBox, activeBoxFrames, validVideo, vid_prefix, balls, isBoxClicked } from "../shared/progstate.svelte";
    let vidobj: HTMLVideoElement;
    let vidurl = $derived(`http://localhost:${$port}/${$vid_prefix}${$cvideo}`)
    let ctime = $state(0)
    let frame = $derived(Math.floor(ctime*25))
    let isPaused = $state(false)
    let canvas: HTMLCanvasElement;
    let vwidth = $state(0)
    let vheight = $state(0)
    let vnatw = $state(0)
    let vnath = $state(0)
    let bWidth = $state(0)
    let drawSVG: SVGElement
    let ballsSVG: SVGElement
    let peopleSVG: SVGElement
    let flr=Math.floor

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
        if (current_frame_boxes) {
            let b = current_frame_boxes.findLast(inbox => isBoxClicked(inbox, drawSVG, e.layerX, e.layerY, vnatw, vnath))
            if (b) { 
                $activeBox = b.owner
                $activeBoxFrames = b.appearedFrames
            }
        }
        play_button.focus()
    }

    $inspect(vidurl)
</script>
<div class="flex flex-col flex-grow xl:flex-grow-0">
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
                    {#if $balls.includes(f.owner)}
                        <polygon fill={f.owner == $activeBox ? "skyblue" : "yellow"}
                        points="0,0 {-flr(vnatw/80)},{-flr(vnath/40)} {flr(vnatw/80)},{-flr(vnath/40)}"
                        transform="translate({f.x+f.w/2},{f.y-5-vnatw/40})"/>
                    {:else}
                        <ellipse stroke="{f.owner == $activeBox ? "lightpink": "red"}" mask="url(#mask1)" vector-effect="non-scaling-stroke"
                            stroke-width="3px" cx=0 cy=0 ry=25 rx=45 fill="none"
                            transform="translate({f.x + f.w/2},{f.y+f.h-5}) scale({f.w/60})"/>
                    {/if}
                {/each}
            </svg>
            {#if $validVideo}
                <div class="flex flex-row w-auto mt-1">
                    <button bind:clientWidth={bWidth} onclick={playVideo} class="bg-orange-300 w-fit px-2 pb-0.5 pt-1 rounded-md" bind:this={play_button}>
                        <i class="material-icons">{isPaused ? "play_arrow" : "pause"}</i> </button>
                    <input type='range' max={$video_duration} step="any" bind:value={ctime} onkeydown={playVideo} class="flex-grow h-auto mx-2"/>
                </div>
            {/if}
    </div>
    {#if $validVideo == 0}
        <p>Please load a video to get started</p>
    {/if}
</div>

<style>
    video {
        max-height: 50vh;
    }
</style>