<script lang="ts">
  type Props = {
    variant?: "text" | "circular" | "rectangular" | "card";
    width?: string | number;
    height?: string | number;
    lines?: number; // For text variant
    className?: string;
  };

  const { variant = "text", width, height, lines = 1, className = "" }: Props = $props();

  function getVariantClasses(variant: string) {
    switch (variant) {
      case "circular":
        return "rounded-full";
      case "rectangular":
        return "rounded-md";
      case "card":
        return "rounded-lg";
      default:
        return "rounded";
    }
  }

  function getDimensions(variant: string) {
    if (width || height) {
      return {
        width: typeof width === "number" ? `${width}px` : width,
        height: typeof height === "number" ? `${height}px` : height
      };
    }

    switch (variant) {
      case "circular":
        return { width: "40px", height: "40px" };
      case "rectangular":
        return { width: "100%", height: "20px" };
      case "card":
        return { width: "100%", height: "200px" };
      default:
        return { width: "100%", height: "16px" };
    }
  }

  const dimensions = getDimensions(variant);
  const variantClasses = getVariantClasses(variant);
</script>

{#if variant === "text" && lines > 1}
  <div class="space-y-2 {className}">
    {#each Array(lines) as i (i)}
      <div
        class="animate-pulse bg-gray-200 {variantClasses} dark:bg-gray-700"
        style="width: {i === lines - 1 ? '75%' : '100%'}; height: {dimensions.height};"
      ></div>
    {/each}
  </div>
{:else}
  <div
    class="animate-pulse bg-gray-200 {variantClasses} {className} dark:bg-gray-700"
    style="width: {dimensions.width}; height: {dimensions.height};"
    role="status"
    aria-label="読み込み中"
  ></div>
{/if}
