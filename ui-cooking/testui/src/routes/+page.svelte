<script lang="ts">
	import Sidebar from './components/sidebar.svelte';
	import Homepage from './shared/homepage.svelte';
	import PlayerList from './shared/player_list.svelte';
	import { currentPage, pages } from './shared/progstate.svelte.ts';

	let socket:WebSocket;

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
		<Homepage {socket} visibility={$currentPage == pages.HOME} />
		<PlayerList {socket} visibility={$currentPage == pages.PLAYERS_LIST}/>
	</div>
</div>

<style>
</style>
