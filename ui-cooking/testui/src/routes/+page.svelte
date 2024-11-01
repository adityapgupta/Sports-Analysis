<script lang="ts">
	import Counter from './Counter.svelte';
	import Canvasimg from './canvasimg.svelte';
	import Sidebar from './sidebar.svelte';
</script>

<svelte:head>
	<title>Home</title>
	<meta name="description" content="Svelte demo app" />
</svelte:head>

<div class="flex flex-row flex-grow">
	<Sidebar />
	<div class="flex flex-col flex-grow">
		<Counter />
		<Canvasimg />
	</div>
</div>

<style>
</style>
