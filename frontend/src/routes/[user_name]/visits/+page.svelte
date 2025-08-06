<script lang="ts">
  import VisitorsList from "$lib/components/VisitorsList.svelte";
  import type { PageData } from "./$types";

  type Props = {
    data: PageData;
  };

  let { data }: Props = $props();
</script>

<svelte:head>
  <title>訪問者 - {data.profile.displayName}</title>
</svelte:head>

<VisitorsList userId={data.profile.userId} />
