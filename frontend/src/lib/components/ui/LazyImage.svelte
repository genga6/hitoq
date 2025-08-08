<script lang="ts">
  import { createLazyLoader } from "$lib/utils/lazyLoader";

  type Props = {
    src: string;
    alt: string;
    class?: string;
    placeholder?: string;
    fallback?: string;
  };

  const { 
    src, 
    alt, 
    class: className = "", 
    placeholder = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 24 24'%3E%3Cpath stroke='%23d1d5db' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='M12 6v6m0 0v6m0-6h6m-6 0H6'/%3E%3C/svg%3E",
    fallback = "/default-avatar.svg"
  }: Props = $props();

  let loaded = $state(false);
  let imageElement: HTMLImageElement | null = $state(null);

  $effect(() => {
    if (imageElement) {
      const lazyLoad = createLazyLoader(() => {
        if (imageElement) {
          imageElement.src = src;
        }
      });

      const disconnect = lazyLoad(imageElement);
      return disconnect;
    }
  });

  function handleLoad() {
    loaded = true;
  }

  function handleError() {
    if (imageElement && fallback) {
      imageElement.src = fallback;
    }
  }
</script>

<img
  bind:this={imageElement}
  src={loaded ? src : placeholder}
  {alt}
  class={className}
  onload={handleLoad}
  onerror={handleError}
  loading="lazy"
  decoding="async"
/>