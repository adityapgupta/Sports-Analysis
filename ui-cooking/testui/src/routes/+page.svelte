<script lang="ts">
	import Sidebar from './components/sidebar.svelte';
    import Analytics from './shared/analytics.svelte';
	import Homepage from './shared/homepage.svelte';
	import PlayerList from './shared/player_list.svelte';
	import Landing from './components/Landing.svelte';
	import { currentPage, pages } from './shared/progstate.svelte.ts';

	let socket:WebSocket;

	socket = new WebSocket("ws://localhost:8001/")
	socket.addEventListener('open',() => console.log("The websocket connection is successful"))
</script>

<svelte:head>
	<title>Home</title>
	<meta name="description" content="Svelte demo app" />
</svelte:head>

<div class="flex flex-row flex-grow items-stretch">
	<Sidebar />
	<div class="flex flex-col flex-grow" style="width: 100%;">
		<Landing visibility={$currentPage == pages.MAIN_HOME} />
		<Homepage {socket} visibility={$currentPage == pages.HOME} />
		<PlayerList {socket} visibility={$currentPage == pages.PLAYERS_LIST}/>
		<Analytics {socket} visibility={$currentPage == pages.ANALYTICS} />
	</div>
</div>

<style>
</style>
