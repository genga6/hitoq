<script lang="ts">
  import GachaPage from './GachaPage.svelte';
  import type { PageData } from './$types';

  const { data }: { data: PageData } = $props();
</script>

<GachaPage
  categories={data.categories}
  isOwner={data.isOwner}
  userId={data.profile.userId}
  profile={data.profile}
  currentUser={data.currentUser}
  isLoggedIn={data.isLoggedIn}
/>
