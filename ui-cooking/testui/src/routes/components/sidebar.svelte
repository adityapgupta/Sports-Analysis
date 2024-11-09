<script lang="ts">
    let expanded = $state(true);
    import { fade } from 'svelte/transition';
    import { currentPage, pages } from '../shared/progstate.svelte.ts'
    import ico1 from '$lib/sidebar-icons/ico1.jpg'
    import ico2 from '$lib/sidebar-icons/ico2.jpg'
    import ico3 from '$lib/sidebar-icons/ico3.png'

    const fadeOpt = {duration: 150}
    const icons = [ico1, ico2, ico3]
    const descriptions = ["Homepage", "Player list", "Analytics"]

    let changePage = function(idx: number) {
        $currentPage = Object.values(pages)[idx]
    }
</script>

<svelte:head>
    <link rel="stylesheet" href="https://fonts.googleapis.com/icon?family=Material+Icons" />
</svelte:head>

<div class="sidebardiv flex flex-col flex-grow-0 mx-4 px-1 pt-1 bg-amber-600 rounded-sm items-stretch min-w-fit">
    <button id="expbutton" onclick={() => expanded = !expanded} class="inline-flex items-center buttons mt-2">
        <i class="material-icons text-center pl-1.5">menu</i>
        {#if expanded}
            <span class="pr-2 pl-3 text-center self-stretch content-center" transition:fade={fadeOpt}>Modules</span>
        {/if}
    </button>
    {#each icons as icon, i}
    <button class="inline-flex items-center w-auto h-auto p-1 buttons" onclick={() => changePage(i)}>
        <img src={icon} alt="icon" class="rounded-sm icons" width="24px"/>
        {#if expanded}
            <span class="text-center pl-2 pr-3" transition:fade={fadeOpt}>{descriptions[i]}</span>
        {/if}
    </button>
    {/each}
</div>

{#if expanded}{/if}

<style>
    .buttons {
        transition: background-color 0.5s;
        margin: 2px;
        width: auto;
        white-space: nowrap;
    }
    .buttons:hover {
        background-color: #c58843;
    }
    #expbutton {
        min-width: 32px;
        min-height: 32px;
        padding: auto;
    }
    .icons {
        background-color: white;
    }
</style>
