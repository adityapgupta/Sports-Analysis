<script lang="ts">
    let { visibility } : { visibility:boolean } = $props();

</script>

<div class="flex-col flex-grow" style:display={visibility ? "flex" : "none"}>
    <table class="p-1 m-2">
        <thead>
            <tr>
                <th class="width-fit">ID</th>
                <th>Jersey number</th>
                <th>Player name</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>1</td>
                <td>10</td>
                <td>Messi</td>
            </tr>
        </tbody>
    </table>
</div>

<style>
    table {
        border-collapse: collapse;
        min-width: 500px;
        max-width: 800px;
        text-align: center;
    }
    @media (max-width: 650px) {
        table {
            min-width: 90%;
            transition: width linear 0.5s;
        }
    }
    th, td {
        border: 1.5px solid black;
        padding: 3px;
    }
</style>