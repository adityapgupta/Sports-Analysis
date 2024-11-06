<script lang="ts">
    let { visibility, socket } : { visibility:boolean, socket: WebSocket } = $props();
    import { player_data } from "./progstate.svelte";

    function sendUpdatedPlayers() {
        socket.send(JSON.stringify({
            type: 'update-players',
            data: $player_data
        }))
    }
</script>

<div class="flex-col flex-grow" style:display={visibility ? "flex" : "none"}>
    <table class="p-1 m-2">
        <thead>
            <tr>
                <th class="width-fit">ID</th>
                <th>Jersey number</th>
                <th>Player name</th>
            </tr>
        </thead>
        <tbody>
            {#each $player_data as val, idx}
                {#if val[1] != "ball"}
                <tr>
                    <td>{val[0]}</td>
                    <td>{val[2]}</td>
                    <td><input class="player_input" type="text" bind:value="{val[1]}"></td>
                </tr>
                {/if}
            {/each}
        </tbody>
    </table>
    <button onclick={sendUpdatedPlayers}> Update players to the file </button>
</div>

<style>
    table {
        border-collapse: collapse;
        min-width: 500px;
        max-width: 700px;
        text-align: center;
        align-self: center;
    }
    @media (max-width: 650px) {
        table {
            min-width: 90%;
            transition: width linear 0.5s;
        }
    }
    th, td {
        border: 1.5px solid black;
        padding: 3px;
    }
    .player_input {
        all: inherit;
        border: none;
        margin: none;
        padding: none;
    }
</style>