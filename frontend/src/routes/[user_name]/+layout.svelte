<script lang="ts">
  import ProfileHeader from '$lib/components/ProfileHeader.svelte';
  import TabNavigation from '$lib/components/TabNavigation.svelte';
  import type { Snippet } from 'svelte';
  import type { BasePageData } from '$lib/types/page';
  import { recordVisit } from '$lib/api-client/visits';

  type Props = {
    data: BasePageData;
    children?: Snippet;
  };
  let { data, children }: Props = $props();

  // Record visit when page loads
  $effect(() => {
    if (data.profile) {
      recordVisit(data.profile.userId).catch((error) => {
        // Silently fail - visit recording is not critical
        console.debug('Failed to record visit:', error);
      });
    }
  });
</script>

<main class="flex min-h-screen justify-center bg-gray-100 p-4 md:p-6">
  <div class="card w-full max-w-4xl space-y-4 p-4 md:space-y-6 md:p-6">
    {#if data.profile}
      <ProfileHeader
        displayName={data.profile.displayName}
        iconUrl={data.profile.iconUrl}
        bio={data.profile.bio}
        userName={data.profile.userName}
        isOwner={data.isOwner}
      />
      <TabNavigation userName={data.profile.userName} />
    {/if}
    {#if children}
      {@render children()}
    {/if}
  </div>
</main>
