<script lang="ts">
	import '../app.css';
	import Header from './components/Header.svelte';
	let { children } = $props();

</script>
<link rel="stylesheet" href="https://fonts.googleapis.com/icon?family=Material+Icons"/>


<div class="app min-h-screen">

	<header class="flex flex-shrink">
		<Header></Header>
	</header>

	<main class="mb-none flex-grow self-stretch flex items-stretch ">
		{@render children()}
	</main>

	<footer class="flex-shrink">
		<p>
			UMC301 sports analysis project, <a href="https://github.com/adityapgupta/Sports-Analysis">Github</a> 
		</p>
	</footer>
</div>

<style>
	.app {
		display: flex;
		flex-direction: column;
	}

	main {
		min-height: 100%;
		padding-block: 10px;
	}

	footer {
		display: flex;
		flex-direction: column;
		justify-content: center;
		align-items: center;
		padding: 12px;
	}

	footer a {
		font-weight: bold;
	}

	@media (min-width: 480px) {
		footer {
			padding: 12px 0;
		}
	}
</style>
