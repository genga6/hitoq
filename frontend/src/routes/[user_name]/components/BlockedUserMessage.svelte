<script lang="ts">
  interface Props {
    userName: string;
    userId: string;
    onUnblock?: () => void;
  }
  let { userName, userId, onUnblock }: Props = $props();

  async function handleUnblock() {
    try {
      const { blocksApi } = await import("$lib/api-client");
      await blocksApi.removeBlock(userId);
      onUnblock?.();
    } catch (error) {
      console.error("Failed to unblock user:", error);
    }
  }
</script>

<div class="py-12 text-center">
  <div
    class="theme-bg-elevated mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full"
  >
    <svg class="theme-text-muted h-8 w-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path
        stroke-linecap="round"
        stroke-linejoin="round"
        stroke-width="2"
        d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728L5.636 5.636m12.728 12.728L18.364 5.636M5.636 18.364l12.728-12.728"
      ></path>
    </svg>
  </div>
  <h2 class="theme-text-primary mb-2 text-xl font-bold">
    @{userName}さんをブロックしています
  </h2>
  <p class="theme-text-secondary mx-auto mb-6 max-w-md">
    ブロックしているため、このユーザーのコンテンツを表示できません。
  </p>
  <button onclick={handleUnblock} class="btn-primary rounded-full px-6 py-2">
    ブロックを解除
  </button>
</div>
