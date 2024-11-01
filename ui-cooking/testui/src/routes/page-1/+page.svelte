<script lang="ts">
	import Counter from '../Counter.svelte';
	import Canvasimg from '../canvasimg.svelte';
	import Sidebar from '../sidebar.svelte';
    export const prerender=true
</script>

<svelte:head>
	<title>Page 2</title>
	<meta name="description" content="Svelte demo app" />
</svelte:head>

<div class="flex flex-row flex-grow">
    <Sidebar />
    <div class="flex flex-col flex-grow">
        <Counter />
    </div>
</div>

<style>
</style>