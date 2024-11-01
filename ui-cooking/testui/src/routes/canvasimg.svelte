

<div id="img-container" class="relative">
    <img src={githublogo} id="srcimg" width=500px alt="current frame">
    <canvas id="drawcanvas" class="absolute top-0 left-0 z-10" width={cwidth} height={cheight}></canvas>
</div>

<script lang="ts">
    import { onMount } from 'svelte';
    import { draw } from './canvasutils.svelte.ts'
    import githublogo from '$lib/media-videos/SNMOT-060/img1/000001.jpg'
    let imgframe = $state(1)
    let imgurl = $derived(`img?frame=${imgframe}`)
    let image: Blob;
    let cwidth:number = $state(0), cheight:number = $state(0);
    let img:HTMLImageElement;
    let canvas:HTMLCanvasElement
    let ctx:CanvasRenderingContext2D

    onMount(() => {
        if (!canvas) {
            canvas = document.getElementById('drawcanvas') as HTMLCanvasElement
            ctx = canvas.getContext('2d') as CanvasRenderingContext2D
        }
        img = document.getElementById('srcimg') as HTMLImageElement
        const resizehandle = new ResizeObserver(entries => {
            cwidth = img.clientWidth
            cheight = img.clientHeight
        })

        const canvasresize = new ResizeObserver(e => {
            draw(canvas, ctx)
        })
        canvasresize.observe(canvas)
        resizehandle.observe(img)
        draw(canvas, ctx)
    })

    $effect(() => {
        cwidth = img.clientWidth
        cheight = img.clientHeight
    })
</script>

<style>
</style>