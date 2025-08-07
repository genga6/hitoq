<script lang="ts">
  import GachaPage from "./GachaPage.svelte";
  import type { PageData } from "./$types";

  const { data }: { data: PageData } = $props();
</script>

<GachaPage categories={data.categories} userId={data.profile.userId} />
