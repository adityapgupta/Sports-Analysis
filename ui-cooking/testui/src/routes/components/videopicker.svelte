<script lang="ts">
    import { cvideo, box, dataStore, video_duration, vid_prefix, identifications, frameRate, dataStore_2d } from "../shared/progstate.svelte"
    const { socket }: { socket: WebSocket } = $props()

    let videos = $state([])
    let bval = $state('');
    let fileInput: HTMLInputElement
    async function getFiles() {
        await socket.send(JSON.stringify({
            type:'getFiles',
        }))
    }
    
    function updateVideo() {
        cvideo.set(bval)
        setTimeout(loadFrameData, 150)
    }
    
    socket.addEventListener('message', msg => {
        const data = JSON.parse(msg.data)
        if (data.type == 'vidList') {
            videos = data.data
            $vid_prefix = data.prefix
        } else if (data.type == 'playerMap') {
            $identifications = {
                ball_ids: [],
                player_ids: [],
                left_team: [],
                right_team: [],
                referee: []
            }
            const indata = data.data as {[key: number]: "ball" | "referee" | "left_player" | "right_player"}
            for (const key in indata) {
                if (Object.prototype.hasOwnProperty.call(indata, key)) {
                    const elt = indata[key];
                    switch (elt) {
                        case "ball":
                            $identifications.ball_ids.push(Number(key))
                            break;
                        case "referee":
                            $identifications.referee.push(Number(key))
                            break;
                        case "left_player":
                            $identifications.left_team.push(Number(key))
                            $identifications.player_ids.push(Number(key))
                            break;
                        case "right_player":
                            $identifications.right_team.push(Number(key))
                            $identifications.player_ids.push(Number(key))
                            break;
                        default:
                            break;
                    }
                }
            }
        } else if (data.type == "2dMap") {
            $dataStore_2d = data.data
        }
    })
    socket.addEventListener('message', msg => {
        const data = JSON.parse(msg.data)
        if (data.type == 'bufferedFrames') {
            const recvdata = data.data as {[key: number] : Array<{ user: number, x: number, w: number, h: number, y: number }>}
            $dataStore = {}
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
        if (isNaN(d)) {
            return
        }
        socket.send(JSON.stringify({
            type: 'bufVid',
            min: 0,
            max: Math.floor($frameRate*d),
            video: bval
        }))

        socket.send(JSON.stringify({
            type: 'get2dMap',
            video: bval
        }))
        socket.send(JSON.stringify({
            type: 'getPlayerMap',
            video: bval
        }))
    }

    async function copyFileInternal() {
        await socket.send(JSON.stringify({
            type: 'loadFile',
            file: fileInput.value
        }))
    }
</script>

<div class="maingrid m-2 p-2 grid">
    <button name="selectFileButton" class="bg-slate-400 p-2" onclick={copyFileInternal}>Copy to field</button>
    <input bind:this={fileInput} class="m-1 rounded" placeholder="Enter a full filepath here"/>
    <button name="getVideoButton" id="get_videos"
    class="bg-slate-400 p-2" onclick={getFiles}>Get videos</button>
    <select name="optsel" bind:value={bval} onchange={updateVideo} class="p-1" title="Get video">
        {#each videos as vid}
        <option value={vid}>{vid}</option>
        {/each}
    </select>
</div>

<style>
    button, select {
        margin: 2px;
        border-radius: 3px;
    }
    .maingrid {
        grid-template-columns: auto;
    }
    @media (min-width: 800px) {
        .maingrid {
            grid-template-columns: auto 1fr;
        }
    }
</style>