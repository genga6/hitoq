<script lang="ts">
  import { createLazyLoader } from "$lib/utils/lazyLoader";
  import type { Snippet } from "svelte";

  type Props = {
    threshold?: number;
    rootMargin?: string;
    placeholder?: Snippet;
    children?: Snippet;
    onLoad?: () => void;
  };

  const { threshold = 0.1, rootMargin = "50px", placeholder, children, onLoad }: Props = $props();

  let loaded = $state(false);
  let containerElement: HTMLDivElement | null = $state(null);

  $effect(() => {
    if (containerElement) {
      const lazyLoad = createLazyLoader(
        () => {
          loaded = true;
          onLoad?.();
        },
        { threshold, rootMargin }
      );

      const disconnect = lazyLoad(containerElement);
      return disconnect;
    }
  });
</script>

<div bind:this={containerElement}>
  {#if loaded}
    {#if children}
      {@render children()}
    {/if}
  {:else if placeholder}
    {@render placeholder()}
  {:else}
    <!-- Default placeholder -->
    <div class="flex items-center justify-center py-8">
      <div class="h-8 w-8 animate-pulse rounded bg-gray-200"></div>
    </div>
  {/if}
</div>
