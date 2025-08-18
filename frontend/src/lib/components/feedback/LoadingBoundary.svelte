<script lang="ts">
  import { loadingStore } from "$lib/stores/loadingStore";
  import type { Snippet } from "svelte";

  type Props = {
    children: Snippet;
    operationId?: string;
    fallback?: Snippet;
    showGlobalLoading?: boolean;
  };

  const { children, operationId, fallback, showGlobalLoading = false }: Props = $props();

  const loadingState = $derived($loadingStore);

  const isLoading = $derived(() => {
    if (showGlobalLoading && loadingState.globalLoading) return true;
    if (operationId && loadingState.operations[operationId]) return true;
    return false;
  });
</script>

{#if isLoading()}
  {#if fallback}
    {@render fallback()}
  {:else}
    <!-- Default loading display -->
    <div class="flex items-center justify-center p-8">
      <div class="flex items-center space-x-2">
        <div
          class="h-4 w-4 animate-spin rounded-full border-2 border-orange-500 border-t-transparent"
        ></div>
        <span class="theme-text-secondary text-sm">読み込み中...</span>
      </div>
    </div>
  {/if}
{:else}
  {@render children()}
{/if}
