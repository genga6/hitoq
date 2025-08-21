<script lang="ts">
  import { page } from "$app/state";
  import { goto } from "$app/navigation";
  import type { Profile } from "$lib/types";
  import TabGroup from "$lib/components/ui/TabGroup.svelte";

  type Props = {
    userName: Profile["userName"];
    isOwner: boolean;
  };
  const { userName, isOwner }: Props = $props();

  // UI即座更新用のローカル状態
  // eslint-disable-next-line svelte/prefer-writable-derived
  let localActiveTab: string = $state(page.url.pathname);

  // 実際に表示するアクティブタブ（UI即座更新 + URL同期）
  const activeTab = $derived(localActiveTab);

  const navigationTabs = $derived([
    { id: `/${userName}`, label: "プロフィール", href: `/${userName}` },
    ...(isOwner
      ? [
          {
            id: `/${userName}/answer-questions`,
            label: "回答する", 
            href: `/${userName}/answer-questions`
          }
        ]
      : []),
    { id: `/${userName}/qna`, label: "回答一覧", href: `/${userName}/qna` },
    { id: `/${userName}/talk`, label: "トーク", href: `/${userName}/talk` }
  ]);

  function handleTabChange(tabId: string) {
    // UI即座更新（オレンジバーをすぐに移動）
    localActiveTab = tabId;
    
    // 非同期でページ遷移（ローディングはバックグラウンドで）
    goto(tabId as `/${string}`, { 
      replaceState: false,
      noScroll: false,
      keepFocus: false,
      invalidateAll: false  // キャッシュ活用のため無効化しない
    });
  }

  // URL変更時にローカル状態を同期
  $effect(() => {
    localActiveTab = page.url.pathname;
  });
</script>

<nav>
  <TabGroup 
    tabs={navigationTabs} 
    activeTab={activeTab} 
    variant="navigation" 
    onTabChange={handleTabChange}
  />
</nav>
