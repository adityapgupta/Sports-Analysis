<script lang="ts">
    let expanded = $state(true);
    import { fade } from 'svelte/transition';
    import { currentPage, pages } from '../shared/progstate.svelte.ts'
    import ico1 from '$lib/sidebar-icons/ico1.jpg'
    import ico2 from '$lib/sidebar-icons/ico2.jpg'
    import ico3 from '$lib/sidebar-icons/ico3.png'

    const fadeOpt = {duration: 150}
    const icons = [ico1, ico2, ico3]
    const descriptions = ["Video", "Players", "Insights", "Team"]

    let changePage = function(idx: number) {
        $currentPage = Object.values(pages)[idx]
    }
</script>

<svelte:head>
    <link rel="stylesheet" href="https://fonts.googleapis.com/icon?family=Material+Icons" />
</svelte:head>

<div class="sidebardiv flex flex-col flex-grow-0 px-1 pt-1 bg-slate-800 items-stretch min-w-fit">
    {#if expanded}
        <h2 class="text-center p-2 px-3 m-1 text-xl font-bold buttons" onclick={() => $currentPage = pages.MAIN_HOME}>Sigma.Ball</h2>
    {/if}
    <button id="expbutton" onclick={() => expanded = !expanded} class="inline-flex items-center buttons mt-2">
        <i class="material-icons text-center pl-1.5">menu</i>
        {#if expanded}
            <span class="pr-2 pl-3 text-center self-stretch content-center" transition:fade={fadeOpt}>Modules</span>
        {/if}
    </button>
    {#each descriptions as description, i}
    <button class="inline-flex items-center w-auto h-auto p-1 buttons" onclick={() => changePage(i+1)}>
        {#if expanded}
            <span class="text-center pl-2 pr-3" transition:fade={fadeOpt}>{description}</span>
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
        padding-right: 15px;
    }
    .buttons:hover {
        background-color: #434a55;
    }
    #expbutton {
        min-width: 32px;
        min-height: 32px;
        padding: auto;
    }
    .sidebardiv {
        color: white;
    }
    .text-center {
        text-align: center;
        font-size: large;
    }
</style>
