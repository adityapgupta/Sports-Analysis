<script lang="ts">
    import { cvideo, port, dataStore, video_duration, activeBox, activeBoxFrames, validVideo, vid_prefix } from "../shared/progstate.svelte";
    let { children }: { children: () => any } = $props();
    let vidobj: HTMLVideoElement;
    let vidurl = $derived(`http://localhost:${$port}/${$vid_prefix}${$cvideo}`)
    let ctime = $state(0)
    let portion = $derived(ctime/$video_duration*100)
    let frame = $derived(Math.floor(ctime*25))
    let p_frame = 0
    let isPaused = $state(false)
    let canvas: HTMLCanvasElement;
    let vwidth = $state(0)
    let vheight = $state(0)
    let vnatw = $state(0)
    let optWidth = $state(0)
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

    function barClicked(e: MouseEvent) {
        const t = e.target as HTMLElement
        const frac = (e.layerX-bWidth)/t.clientWidth // The button width is included in layerX
        vidobj.currentTime = frac * $video_duration
        play_button.focus()
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
                <div class="flex flex-row w-auto">
                    <button bind:clientWidth={bWidth} onclick={playVideo} class="bg-orange-300 w-fit  px-2 py-1 rounded-sm" bind:this={play_button}>
                        <i class="material-icons">{isPaused ? "play_arrow" : "pause"}</i> </button>

                    <!-- svelte-ignore a11y_no_noninteractive_element_interactions -->
                    <!-- svelte-ignore a11y_click_events_have_key_events -->
                    <progress max={$video_duration} value={ctime} class="flex-grow"
                        bind:clientWidth={optWidth} onclick={barClicked}></progress>
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