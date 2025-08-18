<script lang="ts">
  import { blocksApi } from "$lib/api-client";
  import type { BlockCreate } from "$lib/types";
  import ReportModal from "./ReportModal.svelte";

  let {
    userId,
    initialIsBlocked = false,
    class: className = "",
    onBlockStatusChange = () => {}
  } = $props<{
    userId: string;
    initialIsBlocked?: boolean;
    class?: string;
    onBlockStatusChange?: (blocked: boolean) => void;
  }>();

  let localBlockedState = $state<boolean | null>(null);
  let isBlocked = $derived(localBlockedState !== null ? localBlockedState : initialIsBlocked);
  let showReportModal = $state(false);
  let showDropdown = $state(false);
  let blockLoading = $state(false);
  let error = $state<string | null>(null);

  async function handleBlock() {
    blockLoading = true;
    error = null;

    try {
      const blockData: BlockCreate = { blockedUserId: userId };
      await blocksApi.createBlock(blockData);
      localBlockedState = true;
      onBlockStatusChange(true);
    } catch (err) {
      error = err instanceof Error ? err.message : "ブロックに失敗しました";
      console.error("Block error:", err);
    } finally {
      blockLoading = false;
    }
  }

  async function handleUnblock() {
    blockLoading = true;
    error = null;

    try {
      await blocksApi.removeBlock(userId);
      localBlockedState = false;
      onBlockStatusChange(false);
    } catch (err) {
      error = err instanceof Error ? err.message : "ブロック解除に失敗しました";
      console.error("Unblock error:", err);
    } finally {
      blockLoading = false;
    }
  }

  function handleReportSubmitted() {
    showDropdown = false;
  }
</script>

<div class="relative {className}">
  <button
    onclick={() => (showDropdown = !showDropdown)}
    class="theme-text-muted theme-hover-bg rounded-full p-2 transition-colors hover:theme-text-secondary"
    aria-label="ユーザーアクション"
  >
    <!-- 横方向の3点アイコン -->
    <svg class="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
      <path
        d="M6 10a2 2 0 11-4 0 2 2 0 014 0zM12 10a2 2 0 11-4 0 2 2 0 014 0zM16 12a2 2 0 100-4 2 2 0 000 4z"
      ></path>
    </svg>
  </button>

  {#if showDropdown}
    <div
      class="theme-dropdown absolute right-0 z-50 mt-2 w-40 rounded-lg shadow-lg"
    >
      {#if isBlocked}
        <div class="theme-text-muted px-4 py-2 text-sm">ブロック中</div>
        <button
          onclick={async () => {
            await handleUnblock();
            showDropdown = false;
          }}
          disabled={blockLoading}
          class="theme-hover-bg theme-text-primary block w-full px-4 py-2 text-left disabled:cursor-not-allowed disabled:opacity-50"
        >
          {blockLoading ? "解除中..." : "ブロック解除"}
        </button>
      {:else}
        <button
          onclick={async () => {
            await handleBlock();
            showDropdown = false;
          }}
          disabled={blockLoading}
          class="theme-hover-bg theme-text-primary block w-full px-4 py-2 text-left disabled:cursor-not-allowed disabled:opacity-50"
        >
          {blockLoading ? "ブロック中..." : "ブロック"}
        </button>
      {/if}
      <button
        type="button"
        onclick={() => {
          showReportModal = true;
          showDropdown = false;
        }}
        class="theme-hover-bg theme-text-primary block w-full px-4 py-2 text-left"
      >
        通報する
      </button>
    </div>
  {/if}

  <!-- Close dropdown when clicking outside -->
  {#if showDropdown}
    <div
      class="fixed inset-0 z-40"
      onclick={() => (showDropdown = false)}
      role="button"
      tabindex="-1"
      onkeydown={(e: KeyboardEvent) => e.key === "Escape" && (showDropdown = false)}
    ></div>
  {/if}

  {#if error}
    <div class="absolute top-full right-0 mt-1 w-40 rounded bg-red-100 p-2 text-xs text-red-600 dark:bg-red-900/30 dark:text-red-300">
      {error}
    </div>
  {/if}
</div>

<ReportModal bind:isOpen={showReportModal} {userId} onReportSubmitted={handleReportSubmitted} />
