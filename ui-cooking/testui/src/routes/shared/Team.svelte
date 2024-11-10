<script lang="ts">
    const { visibility }: { visibility: boolean } = $props();

    import sinImage from '$lib/images/people/sin.jpg';
    
    const contributors = [
        { 
            id: 1, 
            name: 'Sharath S', 
            image: sinImage,  // Note the leading slash
            github: 'https://github.com/sharaths21312'
        },
        { 
            id: 2, 
            name: 'Sahil Chaudhary', 
            image: sinImage,
            github: 'https://github.com/sahil-chaudhary'
        },
        { 
            id: 3, 
            name: 'Aditya Gupta', 
            image: sinImage,
            github: 'https://github.com/adityapgupta'
        },
        { 
            id: 4, 
            name: 'Armaan Khetarpaul', 
            image: sinImage,
            github: 'https://github.com/Armxyz1'
        },
        { 
            id: 5, 
            name: 'Umang Majummdar', 
            image: sinImage,
            github: 'https://github.com/ZeroDawn0D'
        },
        { 
            id: 6, 
            name: 'Rk Shishir', 
            image: sinImage,
            github: 'https://github.com/Shishir1729'
        },
    ];
</script>

<div style:display={visibility ? "flex" : "none"} class="flex flex-col w-full p-8">
    <!-- Title Section -->
    <div class="mb-12 flex justify-center">
        <h2 class="inline-block px-8 py-3 bg-[#1C1C2E] text-yellow-300 rounded-full text-3xl font-semibold">
            Contributors
        </h2>
    </div>

    <!-- Contributors Grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-12">
        {#each contributors as contributor (contributor.id)}
            <div class="flex flex-col items-center space-y-4">
                <!-- Avatar Circle -->
                <div class="w-48 h-48 rounded-full border-4 border-pink-100 bg-pink-50 overflow-hidden">
                    <img
                        src={contributor.image}
                        alt={contributor.name}
                        class="w-full h-full object-cover"
                    />
                </div>
                <!-- Name with GitHub Link -->
                <a 
                    href={contributor.github} 
                    target="_blank" 
                    rel="noopener noreferrer" 
                    class="contributor-name text-xl font-medium text-gray-800 hover:text-blue-600"
                >
                    {contributor.name}
                </a>
            </div>
        {/each}
    </div>
</div>

<style>
    .rounded-full {
        transition: transform 0.2s ease-in-out;
    }
    
    .rounded-full:hover {
        transform: scale(1.05);
    }

    .contributor-name {
        transition: all 0.2s ease-in-out;
        display: inline-block;
    }

    .contributor-name:hover {
        transform: scale(1.1);
        text-decoration: underline;
    }
</style>