<script lang="ts">
	import '../app.css';
	import Header from './components/Header.svelte';
	let { children } = $props();

</script>

<div class="app min-h-screen">

	<header class="flex flex-shrink">
		<Header></Header>
	</header>

	<main class="mb-none flex-grow self-stretch flex items-stretch ">
		{@render children()}
	</main>

	<footer class="flex-shrink">
		<p>
			visit <a href="https://svelte.dev/docs/kit">svelte.dev/docs/kit</a> to learn about SvelteKit
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
