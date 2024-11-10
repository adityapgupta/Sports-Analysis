<script lang="ts">
    let { visibility, socket } : { visibility:boolean, socket: WebSocket } = $props();
    import { player_data } from "./progstate.svelte";

    function sendUpdatedPlayers() {
        socket.send(JSON.stringify({
            type: 'updatePlayers',
            data: $player_data
        }))
    }
</script>

<div class="flex-col flex-grow" style:display={visibility ? "flex" : "none"}>
    <div class="main-grid">
        <div class="g1 font-bold">ID</div>
        <div class="g2 font-bold">Jersey Number</div>
        <div class="g3 font-bold">Name</div>
        {#each $player_data as val, idx}
            {#if val[1] != "ball"}
                <div class="g1">{val[0]}</div>
                <div class="g2">{val[2]}</div>
                <div class="g3"><input class="player_input" type="text" bind:value="{val[1]}"></div>
            {/if}
        {/each}

    </div>
    <button onclick={sendUpdatedPlayers} class="text-lg p-2 py-1 m-auto mt-2 rounded border-black border-2"> Update players to the file </button>
</div>

<style>
    .player_input {
        all: inherit;
        border: 0px;
        margin: auto;
        padding: 0px;
        width: 100%;
    }
    
    .main-grid {
        display: grid;
        grid-template-columns: fit-content(50px) 1fr 1fr;
        align-content: center;
        justify-content: center;
        text-align: center;
        width: min(80%, 800px);
        align-self: center;
        border: 0.5px solid;
        div {
            padding: 5px;
            padding-inline: 20px;
            border: 0.5px solid;
            
        }
        .g3 {
            padding-block: 0px;
            input {
                padding: 5px;
            }
        }
    }


</style>