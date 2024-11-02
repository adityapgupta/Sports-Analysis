<script lang="ts">
    import { get } from "svelte/store";
    import { counterVal } from "./progstate.svelte";
    let cval = $state(get(counterVal))

    counterVal.subscribe(v => {
        cval = v;
        console.log("the counter updated to", cval)
    })


</script>

<p>The counter value in the prev page is {cval}</p>