<script lang="ts">
  import ProfileHeader from "./components/ProfileHeader.svelte";
  import TabNavigation from "./components/TabNavigation.svelte";
  import BlockedUserMessage from "./components/BlockedUserMessage.svelte";
  import LoadingSpinner from "$lib/components/feedback/LoadingSpinner.svelte";
  import type { Snippet } from "svelte";
  import { checkBlockStatus } from "$lib/utils/userVisitTracking";
  import type { LayoutData } from "./$types";

  interface Props {
    data: LayoutData;
    children?: Snippet;
  }
  let { data, children }: Props = $props();

  let isBlockedByCurrentUser = $state(false);
  let isTabLoading = $state(false);

  async function refreshBlockStatus() {
    if (!data?.profile?.userId || data?.isOwner || !data?.isLoggedIn) {
      isBlockedByCurrentUser = false;
      return;
    }
    try {
      const blocked = await checkBlockStatus(data.profile.userId);
      isBlockedByCurrentUser = blocked;
    } catch (e) {
      console.error("Failed to refresh block status", e);
    }
  }

  $effect(() => {
    refreshBlockStatus();
  });

  function handleLoadingChange(loading: boolean) {
    isTabLoading = loading;
  }
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
        isLoggedIn={data.isLoggedIn ?? false}
        onBlockStatusChange={refreshBlockStatus}
      />

      {#if isBlockedByCurrentUser}
        <BlockedUserMessage
          userName={data.profile.userName}
          userId={data.profile.userId}
          onUnblock={refreshBlockStatus}
        />
      {:else}
        <TabNavigation 
          userName={data.profile.userName} 
          isOwner={data.isOwner ?? false} 
          onLoadingChange={handleLoadingChange}
        />
        {#if isTabLoading}
          <div class="flex justify-center py-12">
            <LoadingSpinner size="medium" text="読み込み中..." />
          </div>
        {:else}
          {@render children?.()}
        {/if}
      {/if}
    {/if}
  </div>
</main>