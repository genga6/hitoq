<script lang="ts">
  import { page } from "$app/state";
  import { goto } from "$app/navigation";
  import type { Profile } from "$lib/types";
  import TabGroup from "$lib/components/ui/TabGroup.svelte";

  type Props = {
    userName: Profile["userName"];
    isOwner: boolean;
    onLoadingChange?: (loading: boolean) => void;
  };
  const { userName, isOwner, onLoadingChange }: Props = $props();

  // UI即座更新用のローカル状態
   
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

  async function handleTabChange(tabId: string) {
    // 既に同じタブの場合は何もしない
    if (localActiveTab === tabId) return;

    // UI即座更新（オレンジバーをすぐに移動）
    localActiveTab = tabId;
    
    // ローディング開始
    onLoadingChange?.(true);
    
    try {
      // 非同期でページ遷移
      await goto(tabId as `/${string}`, { 
        replaceState: false,
        noScroll: false,
        keepFocus: false,
        invalidateAll: false  // キャッシュを活用して高速化
      });
    } finally {
      // ローディング終了（URL変更完了後に$effectでも呼ばれる）
      onLoadingChange?.(false);
    }
  }

  // URL変更時にローカル状態を同期
  $effect(() => {
    localActiveTab = page.url.pathname;
    // URL変更完了時にローディング終了を確実にする
    onLoadingChange?.(false);
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
