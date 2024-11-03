<script lang="ts">
    import { getContext } from "svelte";
    import { cvideo, type boxesData, box, dataStore, video_duration, allBoxes } from "../shared/progstate.svelte"
    import { get } from "svelte/store"
    const { socket }: { socket: WebSocket } = $props()

    let videos = $state([])
    let bval = $state('');
    let vidstart: number;
    let vidend: number;
    function getFiles() {
        socket.send(JSON.stringify({
            type:'getFiles',
        }))
    }
    
    function updateVideo() {
        cvideo.set(bval)
    }
    
    socket.addEventListener('message', msg => {
        const data = JSON.parse(msg.data)
        if (data.type == 'vidList') {
            videos = data.data
        }
    })
    
    socket.addEventListener('message', msg => {
        const data = JSON.parse(msg.data)
        if (data.type == 'bufferedFrames') {
            const recvdata = data.data as {[key: number] : Array<{ user: number, x: number, w: number, h: number, y: number }>}
            
            for (const key in recvdata) {
                dataStore.update(currentData => {
                    const boxedData = recvdata[key].map(v => new box(v.user, v.x, v.y, v.w, v.h))
                    return { ...currentData, [key]: boxedData };
                });
            }
            const evaledobjs: { [key: number]: number } = {}
            Object.values($dataStore).forEach((bs, idx, arr) => makeBoxesReevaluate(bs, evaledobjs))
        }
    })
    
    function makeBoxesReevaluate(indata: box[], alrEvaled: {[key: number]: number}) {
        for (const boxval of indata) {
            if (Object.keys(alrEvaled).find(d => Math.floor(Number(d)) == Math.floor(boxval.owner))) {
                boxval.appearedFrames = alrEvaled[boxval.owner]
            } else {
                boxval.evaluateAppearedFrames()
                alrEvaled[boxval.owner] = boxval.appearedFrames
            }
        }
    }

    function loadFrameData() {
        const d = $video_duration
        console.log(d)
        if (isNaN(d)) {
            return
        }
        socket.send(JSON.stringify({
            type: 'bufVid',
            min: 0,
            max: Math.floor(25*d),
            video: bval
        }))
        console.log('sending')
    }

    $inspect(bval)
</script>


<div class="m-2 p-2 flex flex-col lg:flex-row">
    <button name="getVideoButton" id="get_videos"
        class="bg-slate-400 p-2" onclick={getFiles}>Get videos</button>
    <select name="optsel" bind:value={bval} onchange={updateVideo} class="flex-grow p-1">
        {#each videos as vid}
            <option value={vid}>{vid}</option>
        {/each}
    </select>
    <button onclick={loadFrameData} class="bg-slate-400 p-2">Load frame data</button>
</div>

<style>
    button, select {
        margin: 2px;
        border-radius: 3px;
    }
</style>