<script lang="ts">
    const { visibility }: { visibility: boolean } = $props();
</script>

<div style:display={visibility ? "flex" : "none"} class="relative w-full h-full">
    <div class = "background absolute inset-0 z-0 w-full h-full">
    </div>  

    <div class="overlay absolute inset-0 z-10 flex flex-col items-center justify-center">
        <div class="text-container">
            <h1 class="text-7xl font-bold text-white">Analyze.</h1>
            <h1 class="text-7xl font-bold text-white">Strategize.</h1>
            <h1 class="text-7xl font-bold text-white">Win.</h1>
        </div>
    </div>
</div>

<style>
    h1 {
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
        font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;

    }
    .overlay {
        background-image: url('$lib/images/1156910.png');
        background-repeat: no-repeat;
        background-size: 100% 100%;
        background-color: rgba(255, 255, 255, 0.5);
    }
    .text-container{
        display: flex;
        flex-direction: column;
        align-items: flex-start;
    }
</style>