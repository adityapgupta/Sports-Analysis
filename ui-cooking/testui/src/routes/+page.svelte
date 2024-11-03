<script lang="ts">
	import Sidebar from './components/sidebar.svelte';
	import { get } from 'svelte/store';
	import Homepage from './shared/homepage.svelte';
	import Page2 from './shared/page2.svelte';
	import { currentPage, pages } from './shared/progstate.svelte.ts';

	let socket:WebSocket;
	let cpage = get(currentPage)
	currentPage.subscribe(pg => cpage = pg)

	socket = new WebSocket("ws://localhost:8001/")
	socket.addEventListener('open',() => socket.send(JSON.stringify({data: 'boxes'})))
	socket.addEventListener('message', (e) => {
		const data = e.data as string
		console.log(JSON.parse(data))
	})

	socket.addEventListener('close', () => console.log("The connection was closed"))

</script>

<svelte:head>
	<title>Home</title>
	<meta name="description" content="Svelte demo app" />
</svelte:head>

<div class="flex flex-row flex-grow items-stretch">
	<Sidebar />
	<div class="flex flex-col flex-grow" style="width: 100%;">
		{#if cpage==pages.HOME}
			<Homepage {socket} />
		{:else if cpage==pages.PAGE1}
			<Page2 />
		{/if}
	</div>
</div>

<style>
</style>
