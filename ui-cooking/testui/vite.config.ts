import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';
import svgr from 'vite-plugin-svgr'

export default defineConfig({
	plugins: [sveltekit(), svgr()]
});
