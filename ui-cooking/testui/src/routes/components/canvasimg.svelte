<script lang="ts">
    import { cvideo, port, dataStore, video_duration, activeBox, activeBoxFrames, validVideo } from "../shared/progstate.svelte";
    let { children }: { children: () => any } = $props();
    let vidobj: HTMLVideoElement;
    let getVidUrl = function() {
        return `http://localhost:${$port}/${$cvideo}`
    }
    let vidurl = $state(getVidUrl())
    let ctime = $state(0)
    let portion = $derived(ctime/$video_duration*100)
    let frame = $derived(Math.floor(ctime*25))
    let p_frame = 0
    let isPaused = $state(false)
    let canvas: HTMLCanvasElement;
    let vwidth = $state(0)
    let vheight = $state(0)
    let vnatw = $state(0)
    let vnath = $state(0)

    function formatTime(time: number): string {
        return time.toFixed(2);
    }

    cvideo.subscribe(() => {
        console.log("video was changed", $cvideo)
        if (vidobj == undefined) {
            return 
        }
        vidurl = getVidUrl()
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
        redrawCanvas()
    }

    $inspect(vidurl)
</script>
<div class="flex flex-col flex-grow xl:flex-grow-0">
    <div id="vid-container" class="relative">
        <video bind:this={vidobj} src={vidurl}
            bind:currentTime={ctime} bind:duration={$video_duration} bind:paused={isPaused}
            bind:clientHeight={vheight} bind:clientWidth={vwidth} bind:readyState={$validVideo}
            bind:videoHeight={vnath} bind:videoWidth={vnatw} onclick={check_boxes}>
            <track kind="captions" srclang="en" label="English captions" default>
        </video>
        <canvas bind:this={canvas} class="absolute top-0 left-0 pointer-events-none"></canvas>
    </div>
    {#if $validVideo == 0}
        <button onclick={playVideo} class="bg-orange-300 w-fit  px-3 pb-1 rounded-sm">{isPaused ? "play" : "pause"} video</button>
        <p>Please load a video to get started</p>
    {:else}
        <p>the video is {formatTime(ctime)} out of {formatTime($video_duration)} seconds. also {Math.floor(portion)}%. frame {Math.floor(frame)}</p>
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