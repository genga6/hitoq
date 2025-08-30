<script lang="ts">
  interface Tab {
    id: string;
    label: string;
    count?: number;
    href?: string;
    icon?: string;
  }

  type Props = {
    tabs: Tab[];
    activeTab: string;
    onTabChange?: (tabId: string) => void;
    variant?: "navigation" | "filter";
    size?: "sm" | "md";
  };

  const { tabs, activeTab, onTabChange, variant = "filter", size = "md" }: Props = $props();

  function handleTabClick(tab: Tab) {
    onTabChange?.(tab.id);
  }

  const containerClasses = {
    navigation: "theme-border flex justify-around border-b",
    filter: "theme-border flex border-b"
  };

  const tabClasses = {
    navigation: {
      sm: "theme-visitor-hover min-w-0 flex-1 px-2 py-2 text-center text-xs font-semibold",
      md: "theme-visitor-hover min-w-0 flex-1 px-2 py-3 text-center text-xs font-semibold sm:text-sm"
    },
    filter: {
      sm: "flex-1 px-3 py-1.5 text-sm font-medium",
      md: "flex-1 px-4 py-2 text-sm font-medium"
    }
  };
</script>

<div class={containerClasses[variant]} role="tablist" aria-label="タブナビゲーション">
  {#each tabs as tab (tab.id)}
    {#if variant === "navigation"}
      <button
        onclick={() => handleTabClick(tab)}
        data-sveltekit-preload-data="hover"
        class="{tabClasses[variant][size]} {activeTab === tab.id
          ? 'theme-tab-active'
          : 'theme-tab-inactive'}"
        role="tab"
        aria-selected={activeTab === tab.id}
        aria-controls="tabpanel-{tab.id}"
      >
        <span class="block truncate">
          {tab.icon ? `${tab.icon} ` : ""}{tab.label}
          {tab.count !== undefined ? ` (${tab.count})` : ""}
        </span>
      </button>
    {:else}
      <button
        onclick={() => handleTabClick(tab)}
        data-sveltekit-preload-data="hover"
        class="{tabClasses[variant][size]} {activeTab === tab.id
          ? 'theme-tab-active'
          : 'theme-tab-inactive'}"
        role="tab"
        aria-selected={activeTab === tab.id}
        aria-controls="tabpanel-{tab.id}"
      >
        {tab.icon ? `${tab.icon} ` : ""}{tab.label}
        {tab.count !== undefined ? ` (${tab.count})` : ""}
      </button>
    {/if}
  {/each}
</div>
