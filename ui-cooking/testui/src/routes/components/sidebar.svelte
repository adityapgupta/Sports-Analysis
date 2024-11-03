<script lang="ts">
    import { get } from "svelte/store";
    import { onMount } from "svelte";
    let expanded = $state(true);
    import { slide, fly } from 'svelte/transition'
    import { currentPage, pages } from '../shared/progstate.svelte.ts'
    import ico1 from '$lib/sidebar-icons/ico1.jpg'
    import ico2 from '$lib/sidebar-icons/ico2.jpg'

    const icons = [ico1, ico2]

    const descriptions = ["Hello there", "Second icon"]

    let changePage = function(idx: number) {
        currentPage.set(Object.values(pages)[idx])
        console.log("something is happening?", idx)
    }
</script>

<svelte:head>
    <link rel="stylesheet" href="https://fonts.googleapis.com/icon?family=Material+Icons" />
</svelte:head>

<div class="sidebardiv flex flex-col flex-grow-0 mx-4 px-1 pt-1 bg-amber-600 rounded-sm items-stretch min-w-fit">
    <button id="expbutton" onclick={() => expanded = !expanded} class="inline-flex items-center buttons mt-2">
        <i class="material-icons text-center pl-1.5">menu</i>
        {#if expanded}
            <span class="pr-2 pl-3 text-center self-stretch content-center">Modules</span>
        {/if}
    </button>
    {#each icons as icon, i}
    <button class="inline-flex items-center w-auto h-auto p-1 buttons" onclick={() => changePage(i)}>
        {#if i == 0}
            <img src={icon} alt="icon" class="rounded-sm" width="24px"/>
        {:else}
            <img src={icon} alt="icon" class="rounded-sm" width="24px"/>
        {/if}
        {#if expanded}
            <span class="text-center pl-2 pr-3">{descriptions[i]}</span>
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
</style>
