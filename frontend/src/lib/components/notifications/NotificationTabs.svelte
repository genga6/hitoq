<script lang="ts">
  import type { Message } from "$lib/types";
  import TabGroup from "../ui/TabGroup.svelte";

  export type NotificationTabId = "all" | "likes" | "comments";

  type Props = {
    notifications: Message[];
    activeTab: NotificationTabId;
    onTabChange: (tabId: NotificationTabId) => void;
  };

  const { notifications, activeTab, onTabChange }: Props = $props();

  function handleTabChange(tabId: string) {
    onTabChange(tabId as NotificationTabId);
  }

  const tabs = $derived([
    { 
      id: "all" as const, 
      label: "すべて", 
      count: notifications.length 
    },
    { 
      id: "likes" as const, 
      label: "いいね", 
      count: notifications.filter(n => n.messageType === "like").length 
    },
    { 
      id: "comments" as const, 
      label: "コメント", 
      count: notifications.filter(n => n.messageType === "comment").length 
    }
  ]);
</script>

<div class="border-b border-gray-200 dark:border-gray-700">
  <TabGroup
    {tabs}
    activeTab={activeTab}
    onTabChange={handleTabChange}
  />
</div>