<script lang="ts">
    import { cvideo, port, dataStore, video_duration, activeBox, activeBoxFrames, validVideo, vid_prefix } from "../shared/progstate.svelte";
    let { children }: { children: () => any } = $props();
    let vidobj: HTMLVideoElement;
    let vidurl = $derived(`http://localhost:${$port}/${$vid_prefix}${$cvideo}`)
    let ctime = $state(0)
    let frame = $derived(Math.floor(ctime*25))
    let p_frame = 0
    let isPaused = $state(false)
    let canvas: HTMLCanvasElement;
    let vwidth = $state(0)
    let vheight = $state(0)
    let vnatw = $state(0)
    let vnath = $state(0)
    let bWidth = $state(0)
    let play_button:HTMLButtonElement;

    function formatTime(time: number): string {
        return time.toFixed(2);
    }

    cvideo.subscribe(() => {
        console.log("video was changed", $cvideo)
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
        if (canvas.height != vheight) {
            canvas.height = vheight
            canvas.width = vwidth
            redrawCanvas()
        }
    })



    function redrawCanvas() {
        const current_frame_boxes = $dataStore[frame + 2]
        const ctx = canvas.getContext('2d') as CanvasRenderingContext2D
        canvas.height = vheight
        canvas.width = vwidth
        ctx.clearRect(0, 0, vwidth, vheight)
        if (current_frame_boxes == undefined) return
        ctx.strokeStyle = "red"
        ctx.lineWidth = 2
        for (const box of current_frame_boxes) {
            box.draw(ctx, canvas, vnatw, vnath)
        }
    }

    function check_boxes(e: MouseEvent) {
        const current_frame_boxes = $dataStore[frame + 2];
        if (current_frame_boxes) {
            let b = current_frame_boxes.findLast(box => 
                    box.isClicked(e.layerX, e.layerY, canvas, vnatw, vnath) && box.owner != $activeBox)
            if (b) { 
                $activeBox = b.owner
                $activeBoxFrames = b.appearedFrames
            }
        }
        play_button.focus()
        redrawCanvas()
    }

    $inspect(vidurl)
    $inspect($validVideo)
</script>
<div class="flex flex-col flex-grow xl:flex-grow-0">
    <div id="vid-container" class="relative w-fit">
        <video bind:this={vidobj} src={vidurl}
            bind:currentTime={ctime} bind:duration={$video_duration} bind:paused={isPaused}
            bind:clientHeight={vheight} bind:clientWidth={vwidth} bind:readyState={$validVideo}
            bind:videoHeight={vnath} bind:videoWidth={vnatw} onclick={check_boxes} oncanplay={redrawCanvas}>
            <track kind="captions" srclang="en" label="English captions" default>
            </video>
            <canvas bind:this={canvas} class="absolute top-0 left-0 pointer-events-none"></canvas>
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
</style>