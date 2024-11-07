<script lang="ts">
    import { cvideo, port, dataStore, video_duration, activeBox, activeBoxFrames, validVideo, vid_prefix, balls, drawObjects, isBoxClicked } from "../shared/progstate.svelte";
    let { children }: { children: () => any } = $props();
    let vidobj: HTMLVideoElement;
    let vidurl = $derived(`http://localhost:${$port}/${$vid_prefix}${$cvideo}`)
    let ctime = $state(0)
    let frame = $derived(Math.floor(ctime*25))
    let p_frame = 0
    let isPaused = $state(false)
    let vwidth = $state(0)
    let vheight = $state(0)
    let vnatw = $state(0)
    let vnath = $state(0)
    let bWidth = $state(0)
    let drawSVG: SVGElement
    let ballsSVG: SVGElement
    let peopleSVG: SVGElement

    // svelte-ignore non_reactive_update
        let play_button:HTMLButtonElement;

    function formatTime(time: number): string {
        return time.toFixed(2);
    }

    cvideo.subscribe(() => {
        if ($cvideo == vidurl || vidobj == undefined) return
        vidobj.load()
        redrawCanvas()
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
        if(frame != p_frame) {
            p_frame = frame
            redrawCanvas()
        }
        if (drawSVG.clientHeight != vheight) {
            drawSVG.setAttribute('width', vwidth.toString())
            drawSVG.setAttribute('height', vheight.toString())
            redrawCanvas()
        }
    })

    function redrawCanvas() {
        const current_frame_boxes = $dataStore[frame + 2]
        if (current_frame_boxes == undefined) return
        peopleSVG.innerHTML = ""
        ballsSVG.innerHTML = ""
        for (const box of current_frame_boxes) {
            const b = $balls.includes(box.owner)
            drawObjects(box, b ? ballsSVG : peopleSVG, b, $activeBox == box.owner)
        }

    }

    function check_boxes(e: MouseEvent) {
        const current_frame_boxes = $dataStore[frame + 2];
        if (current_frame_boxes) {
            let b = current_frame_boxes.findLast(box => isBoxClicked(box, drawSVG, e.layerX, e.layerY, vnatw, vnath) && box.owner != $activeBox)
            if (b) { 
                $activeBox = b.owner
                $activeBoxFrames = b.appearedFrames
            }
        }
        play_button.focus()
        redrawCanvas()
    }

    $inspect(vidurl)
</script>
<div class="flex flex-col flex-grow xl:flex-grow-0">
    <div id="vid-container" class="relative w-fit">
        <video bind:this={vidobj} src={vidurl}
            bind:currentTime={ctime} bind:duration={$video_duration} bind:paused={isPaused}
            bind:clientHeight={vheight} bind:clientWidth={vwidth} bind:readyState={$validVideo}
            bind:videoHeight={vnath} bind:videoWidth={vnatw} onclick={check_boxes} oncanplay={redrawCanvas}>
            <track kind="captions" srclang="en" label="English captions" default>
            </video>
            <svg bind:this={drawSVG} viewBox="0 0 {vnatw} {vnath}" class="absolute top-0 left-0 pointer-events-none">
                <g id="balls" bind:this={ballsSVG} style="--val: {-vnath*0.02-5}px"></g>
                <g id="players" bind:this={peopleSVG}></g>
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

{#if $validVideo}
    {@render children?.()}
{/if}

<style>
    video {
        max-height: 50vh;
    }

    #balls {
        transform: translatey(var(--val));
    }
</style>