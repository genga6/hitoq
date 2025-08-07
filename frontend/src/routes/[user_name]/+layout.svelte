<script lang="ts">
  import ProfileHeader from "./ProfileHeader.svelte";
  import TabNavigation from "./TabNavigation.svelte";
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
        <div class="py-12 text-center">
          <div
            class="theme-bg-elevated mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full"
          >
            <svg
              class="theme-text-muted h-8 w-8"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728L5.636 5.636m12.728 12.728L18.364 5.636M5.636 18.364l12.728-12.728"
              ></path>
            </svg>
          </div>
          <h2 class="theme-text-primary mb-2 text-xl font-bold">
            @{data.profile.userName}さんをブロックしています
          </h2>
          <p class="theme-text-secondary mx-auto mb-6 max-w-md">
            ブロックしているため、このユーザーのコンテンツを表示できません。
          </p>
          <button
            onclick={async () => {
              try {
                const { blocksApi } = await import("$lib/api-client");
                await blocksApi.removeBlock(data.profile.userId);
                isBlockedByCurrentUser = false;
              } catch (error) {
                console.error("Failed to unblock user:", error);
              }
            }}
            class="btn-primary rounded-full px-6 py-2"
          >
            ブロックを解除
          </button>
        </div>
      {:else}
        <TabNavigation userName={data.profile.userName} isOwner={data.isOwner ?? false} />
        {@render children?.()}
      {/if}
    {/if}
  </div>
</main>
