<script lang="ts">
    import { get } from "svelte/store";
    import { onMount } from "svelte";
    import { cvideo, port, boxesData, dataStore } from "../shared/progstate.svelte";
    let vidobj: HTMLVideoElement;
    let getVidUrl = function() {
        return `http://localhost:${get(port)}/${get(cvideo)}`
    }
    let vidurl = $state(getVidUrl())
    let ctime = $state(0)
    let dur = $state(0)
    let portion = $derived(ctime/dur*100)
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
        console.log("video was changed", get(cvideo))
        if (vidobj == undefined) {
            return 
        }
        vidurl = getVidUrl()
        vidobj.load()
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
    })

    function redrawCanvas() {
        const current_frame_boxes = get(dataStore)[frame + 2]
        console.log(frame)
        const ctx = canvas.getContext('2d') as CanvasRenderingContext2D
        canvas.height = vheight
        canvas.width = vwidth
        ctx.clearRect(0, 0, vwidth, vheight)
        if (frame > 700) console.log(get(dataStore))
        if (current_frame_boxes == undefined) return
        ctx.strokeStyle = "red"
        ctx.lineWidth = 2
        for (const box of current_frame_boxes) {
            box.draw(ctx, canvas, vnatw, vnath)
        }
    }

    $inspect(vidurl)
</script>
<div id="vid-container" class="primaryvid relative">
    <video bind:this={vidobj} src={vidurl} controls
        bind:currentTime={ctime} bind:duration={dur} bind:paused={isPaused}
        bind:clientHeight={vheight} bind:clientWidth={vwidth}
        bind:videoHeight={vnath} bind:videoWidth={vnatw}>
        <track kind="captions" srclang="en" label="English captions" default>
    </video>
    <canvas bind:this={canvas} class="absolute top-0 left-0 pointer-events-none"></canvas>
</div>
<button onclick={playVideo}>{isPaused ? "play" : "pause"} video</button>
<p>the video is {formatTime(ctime)} out of {formatTime(dur)} seconds. also {Math.floor(portion)}%. frame {Math.floor(frame)}</p>
<style>
    .primaryvid {
        width: 100%;
    }
    @media (min-width: 1300px) {
        .primaryvid {
            width: 50%;
        }
    }
</style>