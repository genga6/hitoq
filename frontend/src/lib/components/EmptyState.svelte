<script lang="ts">
  import type { Snippet } from "svelte";

  type Props = {
    title: string;
    description?: string;
    icon?: "message" | "visit" | "question" | "search" | "custom";
    actionLabel?: string;
    onAction?: () => void;
    children?: Snippet;
  };

  const {
    title,
    description = "",
    icon = "message",
    actionLabel = "",
    onAction,
    children
  }: Props = $props();

  const iconPaths = {
    message:
      "M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z",
    visit:
      "M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z",
    question:
      "M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z",
    search: "M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z",
    custom: ""
  };
</script>

<div class="py-12 text-center">
  <div class="theme-bg-subtle mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full">
    {#if icon !== "custom"}
      <svg class="theme-text-muted h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d={iconPaths[icon]} />
      </svg>
    {:else if children}
      {@render children()}
    {/if}
  </div>

  <h3 class="theme-text-primary mb-2 text-lg font-medium">{title}</h3>

  {#if description}
    <p class="theme-text-muted mb-4">{description}</p>
  {/if}

  {#if actionLabel && onAction}
    <button
      onclick={onAction}
      class="inline-flex items-center rounded-md bg-orange-500 px-4 py-2 text-sm font-medium text-white hover:bg-orange-600"
    >
      {actionLabel}
    </button>
  {/if}
</div>
