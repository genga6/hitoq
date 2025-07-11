<script lang="ts">
  import ProfileHeader from '$lib/components/ProfileHeader.svelte';
  import TabNavigation from '$lib/components/TabNavigation.svelte';
  import type { Snippet } from 'svelte';
  import type { BasePageData } from '$lib/types/page';

  type Props = {
    data: BasePageData,
    children?: Snippet;
  };
  let { data, children }: Props = $props();
</script>

<main class="min-h-screen bg-gray-100 p-4 flex justify-center">
  <div class="bg-white shadow-lg rounded-2xl p-6 max-w-3xl w-full space-y-6">
    <ProfileHeader 
      userName={data.profile.userName} 
      iconUrl={data.profile.iconUrl}
      bio={data.profile.bio} />
    <TabNavigation userId={data.profile.userId} />
    {@render children?.()}
  </div>
</main>
