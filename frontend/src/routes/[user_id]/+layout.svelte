<script lang="ts">
  import ProfileHeader from '$lib/components/ProfileHeader.svelte';
  import TabNavigation from '$lib/components/TabNavigation.svelte';
  import type { Snippet } from 'svelte';

  type Props = {
    data: {
      userId: string;
      userName: string;
      userIconUrl?: string;
      isOwner: boolean;
      bio?: string;
    },
    children?: Snippet;
  };
  let { data, children }: Props = $props();
</script>

<main class="min-h-screen bg-gray-100 p-4 flex justify-center">
  <div class="bg-white shadow-lg rounded-2xl p-6 max-w-3xl w-full space-y-6">
    <ProfileHeader userName={data.userName} userIconUrl={data.userIconUrl} bio={data.bio} />
    <TabNavigation userId={data.userId} />
    {@render children?.()}
  </div>
</main>
