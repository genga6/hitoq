<script lang="ts">
  type Props = {
    src?: string;
    alt?: string;
    size?: "xs" | "sm" | "md" | "lg" | "xl";
    clickable?: boolean;
    onclick?: () => void;
  };

  const { src, alt = "User Avatar", size = "md", clickable = false, onclick }: Props = $props();

  const sizeClasses = {
    xs: "h-4 w-4",
    sm: "h-6 w-6",
    md: "h-8 w-8",
    lg: "h-12 w-12",
    xl: "h-16 w-16"
  };

  let imageClass = `rounded-full object-cover w-full h-full`;
</script>

{#if clickable}
  <button
    type="button"
    class="rounded-full border border-gray-300 p-0 transition-colors hover:border-orange-400 focus:ring-2 focus:ring-orange-400 focus:ring-offset-2 focus:outline-none {sizeClasses[
      size
    ]}"
    {onclick}
    aria-label={alt}
  >
    <img src={src || "/default-avatar.svg"} {alt} class={imageClass} />
  </button>
{:else}
  <img
    src={src || "/default-avatar.svg"}
    {alt}
    class="rounded-full border border-gray-300 {sizeClasses[size]}"
  />
{/if}
