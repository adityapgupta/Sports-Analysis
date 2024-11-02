<script lang="ts">
    import { cvideo, boxesData, box, dataStore } from "../shared/progstate.svelte"
    import { get } from "svelte/store"
    const { socket }: { socket: WebSocket } = $props()
    let videos = $state(['vid1', 'vid2'])
    let bval = $state('');

    function getFiles() {
        socket.send(JSON.stringify({
            type:'getFiles'
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
            console.log(get(dataStore))
        }
    })

    function loadFrameData() {
        socket.send(JSON.stringify({
            type: 'bufVid',
            min: 0,
            max: 750
        }))
        console.log('sending')
    }

    $inspect(bval)
</script>


<div class="m-1 p-1 flex flex-col">
    <button name="getVideoButton" id="get_videos"
        class="bg-slate-400" onclick={getFiles}>Get videos</button>
    <select name="optsel" bind:value={bval} onchange={updateVideo}>
        {#each videos as vid}
            <option value={vid}>{vid}</option>
        {/each}
    </select>
    <button onclick={loadFrameData}>load frame data</button>
</div>