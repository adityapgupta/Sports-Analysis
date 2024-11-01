<script lang="ts">
    import { onMount } from "svelte";
    let expanded = $state(false);
    import { slide, fly } from 'svelte/transition'
    import ico1 from '$lib/sidebar-icons/ico1.jpg'
    import ico2 from '$lib/sidebar-icons/ico2.jpg'

    const icons = [ico1, ico2]

    const descriptions = ["Hello there", "Second icon"]
    const pages = ["", "page-1"]
</script>

<svelte:head>
    <link rel="stylesheet" href="https://fonts.googleapis.com/icon?family=Material+Icons" />
</svelte:head>

<div class="flex flex-col flex-grow-0 mx-4 px-1 bg-amber-600 rounded-sm">
    <img src={ico1} alt="desc-img"/>
    <button id="expbutton" onclick={() => expanded = !expanded} class="p-1">
        <i class="material-icons text-center">menu</i>
    </button>
    {#each icons as icon, i}
    <span class="inline-flex items-center cspan w-fit">
        {#if i == 0}
            <a href="/"><img src={icon} alt="icon" class="p-1 rounded-md" width="32px"/></a>
        {:else}
            <a href="/{pages[i]}"><img src={icon} alt="icon" class="p-1 rounded-md" width="32px"/></a>
        {/if}
        {#if expanded}
            <span class="text-center pl-2 pr-1">{descriptions[i]}</span>
        {/if}
    </span>
    {/each}
</div>

{#if expanded}{/if}

<style>
    .cspan {
        transition: width 0.5s;
    }
</style>
