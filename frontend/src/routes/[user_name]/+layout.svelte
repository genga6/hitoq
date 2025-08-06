<script lang="ts">
  import ProfileHeader from "$lib/components/ProfileHeader.svelte";
  import TabNavigation from "$lib/components/TabNavigation.svelte";
  import type { Snippet } from "svelte";
  import type { BasePageData } from "$lib/types";
  import { recordVisit } from "$lib/api-client/visits";
  import { blocksApi } from "$lib/api-client";

  type Props = {
    data: BasePageData;
    children?: Snippet;
  };
  let { data, children }: Props = $props();

  let isBlockedByCurrentUser = $state(false);

  // Record visit and check block status when page loads
  $effect(() => {
    if (data.profile) {
      // Record visit
      recordVisit(data.profile.userId).catch((error) => {
        // Silently fail - visit recording is not critical
        console.debug("Failed to record visit:", error);
      });

      // Check if current user has blocked this user
      if (!data.isOwner && data.isLoggedIn) {
        blocksApi.checkIsBlocked(data.profile.userId)
          .then((result) => {
            isBlockedByCurrentUser = result.is_blocked;
          })
          .catch((error) => {
            console.debug("Failed to check block status:", error);
            isBlockedByCurrentUser = false;
          });
      } else {
        // オーナーまたはログアウト時は必ずfalse
        isBlockedByCurrentUser = false;
      }
    }
  });
</script>

<main class="flex min-h-screen justify-center bg-gray-100 p-4 md:p-6">
  <div class="card w-full max-w-4xl space-y-3 p-3 sm:space-y-4 sm:p-4 md:space-y-6 md:p-6">
    {#if data.profile}
      <!-- プロフィールヘッダーは常に表示 -->
      <ProfileHeader
        displayName={data.profile.displayName}
        iconUrl={data.profile.iconUrl}
        bio={data.profile.bio}
        userName={data.profile.userName}
        userId={data.profile.userId}
        isOwner={data.isOwner}
        onBlockStatusChange={(blocked) => isBlockedByCurrentUser = blocked}
      />
      
      {#if isBlockedByCurrentUser}
        <!-- ブロック中の表示 (タブ以下のコンテンツ部分のみ) -->
        <div class="text-center py-12">
          <div class="mx-auto w-16 h-16 bg-gray-200 rounded-full flex items-center justify-center mb-4">
            <svg class="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728L5.636 5.636m12.728 12.728L18.364 5.636M5.636 18.364l12.728-12.728"></path>
            </svg>
          </div>
          <h2 class="text-xl font-bold text-gray-900 mb-2">@{data.profile.userName}さんをブロックしています</h2>
          <p class="text-gray-600 mb-6 max-w-md mx-auto">
            ブロックしているため、このユーザーのコンテンツを表示できません。
          </p>
          <button
            onclick={async () => {
              try {
                await blocksApi.removeBlock(data.profile.userId);
                isBlockedByCurrentUser = false;
              } catch (error) {
                console.error("Failed to unblock user:", error);
              }
            }}
            class="px-6 py-2 bg-orange-500 text-white rounded-full hover:bg-orange-600 transition-colors"
          >
            ブロックを解除
          </button>
        </div>
      {:else}
        <!-- 通常のタブ・コンテンツ表示 -->
        <TabNavigation userName={data.profile.userName} isOwner={data.isOwner} />
        {#if children}
          {@render children()}
        {/if}
      {/if}
    {/if}
  </div>
</main>
