<script lang="ts">
  import ProfileHeader from "./components/ProfileHeader.svelte";
  import TabNavigation from "./components/TabNavigation.svelte";
  import BlockedUserMessage from "./components/BlockedUserMessage.svelte";
  import type { Snippet } from "svelte";
  import { trackUserVisit, checkBlockStatus } from "$lib/utils/userVisitTracking";
  import type { LayoutData } from "./$types";

  interface Props {
    data: LayoutData;
    children?: Snippet;
  }
  let { data, children }: Props = $props();

  let isBlockedByCurrentUser = $state(false);

  // Record visit when profile is available
  $effect(() => {
    if (data?.profile?.userId) {
      trackUserVisit(data.profile.userId);
    }
  });

  // Check block status when needed
  $effect(() => {
    if (!data?.profile?.userId || data?.isOwner || !data?.isLoggedIn) {
      isBlockedByCurrentUser = false;
      return;
    }

    checkBlockStatus(data.profile.userId).then((blocked) => {
      isBlockedByCurrentUser = blocked;
    });
  });
</script>

<main class="flex min-h-screen justify-center p-4 md:p-6">
  <div class="card w-full max-w-4xl space-y-3 p-3 sm:space-y-4 sm:p-4 md:space-y-6 md:p-6">
    {#if data?.profile}
      <!-- プロフィールヘッダーは常に表示 -->
      <ProfileHeader
        displayName={data.profile.displayName}
        iconUrl={data.profile.iconUrl}
        bio={data.profile.bio}
        userName={data.profile.userName}
        userId={data.profile.userId}
        isOwner={data.isOwner ?? false}
        onBlockStatusChange={(blocked) => (isBlockedByCurrentUser = blocked)}
      />

      {#if isBlockedByCurrentUser}
        <BlockedUserMessage
          userName={data.profile.userName}
          userId={data.profile.userId}
          onUnblock={() => (isBlockedByCurrentUser = false)}
        />
      {:else}
        <TabNavigation userName={data.profile.userName} isOwner={data.isOwner ?? false} />
        {@render children?.()}
      {/if}
    {/if}
  </div>
</main>
