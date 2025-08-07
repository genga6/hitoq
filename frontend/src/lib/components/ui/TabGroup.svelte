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
    if (variant === "filter") {
      onTabChange?.(tab.id);
    }
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

<div class={containerClasses[variant]}>
  {#each tabs as tab (tab.id)}
    {#if variant === "navigation" && tab.href}
      <a
        href={tab.href}
        class="{tabClasses[variant][size]} {activeTab === tab.id
          ? 'theme-tab-active'
          : 'theme-tab-inactive'}"
      >
        <span class="block truncate">
          {tab.icon ? `${tab.icon} ` : ""}{tab.label}
          {tab.count !== undefined ? ` (${tab.count})` : ""}
        </span>
      </a>
    {:else}
      <button
        onclick={() => handleTabClick(tab)}
        class="{tabClasses[variant][size]} {activeTab === tab.id
          ? 'theme-tab-active'
          : 'theme-tab-inactive'}"
      >
        {tab.icon ? `${tab.icon} ` : ""}{tab.label}
        {tab.count !== undefined ? ` (${tab.count})` : ""}
      </button>
    {/if}
  {/each}
</div>
