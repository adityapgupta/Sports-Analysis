<script lang="ts">
    let expanded = $state(true);
    import { fade } from 'svelte/transition';
    import { currentPage, pages } from '../shared/progstate.svelte.ts'
    import ico1 from '$lib/sidebar-icons/ico1.svg'
    import ico2 from '$lib/sidebar-icons/ico2.svg'
    import ico3 from '$lib/sidebar-icons/ico3.svg'
    import ico4 from '$lib/sidebar-icons/ico4.svg'
    import ico5 from '$lib/sidebar-icons/ico5.svg'
    import menuicon from '$lib/sidebar-icons/menu.svg'

    const fadeOpt = {duration: 150}
    const icons = [ico2, ico4, ico5]
    const descriptions = ["Video", "Insights", "Team"]

    let changePage = function(idx: number) {
        $currentPage = Object.values(pages)[idx]
    }
</script>

<svelte:head>
    <link rel="stylesheet" href="https://fonts.googleapis.com/icon?family=Material+Icons" />
</svelte:head>

<div class="sidebardiv flex flex-col flex-grow-0 px-1 pt-1 bg-slate-800 items-stretch min-w-fit">
    <button class="inline-flex items-center w-auto h-auto p-1 buttons" onclick={() => $currentPage = pages.MAIN_HOME}>
            <img src={ico1} alt="icon" id="icon1" style:width={expanded ? "2rem" : "1.5rem"} style:height={expanded ? "2rem" : "1.5rem"} />
        {#if expanded}
            <h2 class="text-center p-2 px-3 m-1 text-5xl font-bold" transition:fade={fadeOpt}>Sigma.Ball</h2>
        {/if}
    </button>
    <button id="expbutton" onclick={() => expanded = !expanded} class="inline-flex items-center buttons mt-2">
        <img src={menuicon} alt="open menu" class="w-6 h-6"/>
        {#if expanded}
            <span class="pr-2 pl-3 text-center self-stretch content-center" transition:fade={fadeOpt}>Modules</span>
        {/if}
    </button>
    {#each icons as icon, i}
    <button class="inline-flex items-center w-auto h-auto p-1 buttons" onclick={() => changePage(i+1)}>
        <img src={icon} alt="icon" class="w-6 h-6" />
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
        padding-inline: 7px;
    }
    .buttons:hover {
        background-color: #434a55;
    }
    #expbutton {
        min-width: 32px;
        min-height: 32px;
    }
    .sidebardiv {
        color: white;
    }
    .text-center {
        text-align: center;
        font-size: large;
    }
    #icon1 {
        transition: all 0.5s;
    }
</style>