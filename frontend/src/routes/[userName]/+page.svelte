<script lang="ts">
  import ProfileItemCard from "./components/ProfileItemCard.svelte";
  import type { ProfileItem } from "$lib/types";
  import type { PageData } from "./$types";
  import { updateProfileItem } from "$lib/api-client/profile";
  import { withOptimisticUpdate, createOptimisticDataManager, createOperationId } from "$lib/utils/optimisticUI";

  type Props = {
    data: PageData;
  };

  const { data }: Props = $props();
  const isOwner = $derived(data.isOwner);

  // 楽観的UI管理
  const sortedInitialItems = [...(data.profileItems || [])].sort((a, b) => a.displayOrder - b.displayOrder);
  const dataManager = createOptimisticDataManager(sortedInitialItems);
  let profileItems = $state(dataManager.data);

  const createSaveHandler = (item: ProfileItem) => {
    return async (newValue: string): Promise<boolean> => {
      const operationId = createOperationId('profile-update', item.profileItemId);
      const originalValue = item.value;

      try {
        const result = await withOptimisticUpdate(
          {
            operationId,
            invalidateKey: `user:${data.profile.userName}:profile`,
            apiCall: () => updateProfileItem(data.profile.userId, item.profileItemId, { value: newValue }),
            onSuccess: () => {
              // サーバーからの最新データでコミット
              dataManager.commit();
            },
            onError: (error) => {
              console.error("プロフィールの更新に失敗しました:", error);
            },
          },
          { value: newValue },
          // 楽観的UI更新
          () => {
            dataManager.optimisticUpdate(
              (i) => i.profileItemId === item.profileItemId,
              (i) => ({ ...i, value: newValue })
            );
            profileItems = dataManager.data;
          },
          // ロールバック処理
          () => {
            dataManager.optimisticUpdate(
              (i) => i.profileItemId === item.profileItemId,
              (i) => ({ ...i, value: originalValue })
            );
            profileItems = dataManager.data;
          }
        );

        return !!result;
      } catch {
        return false;
      }
    };
  };

  // データの同期（親からのpropsが更新された時）
  $effect(() => {
    if (data.profileItems) {
      const newSortedItems = [...data.profileItems].sort((a, b) => a.displayOrder - b.displayOrder);
      dataManager.commit(); // 現在の楽観的状態をコミット
      profileItems = newSortedItems;
    }
  });
</script>

<div class="mt-8 space-y-4 md:space-y-8">
  {#if profileItems.length > 0}
    <!-- 自己紹介 -->
    {@const introItem = profileItems.find(p => p.label === '自己紹介')}
    {#if introItem}
      <ProfileItemCard
        label={introItem.label}
        value={introItem.value}
        {isOwner}
        onSave={createSaveHandler(introItem)}
        inputType="textarea"
        validationType="profileValue"
        placeholder="自己紹介を書いてみましょう..."
      >
        {#if isOwner}
          <p class="theme-text-muted text-base leading-relaxed whitespace-pre-wrap italic opacity-50">
            例： hito Q太郎です！普段は会社員をしています。 趣味はゲームと料理です。最近は〇〇というゲームにハマッています！
            気軽に話しかけてください！よろしくお願いします！
          </p>
        {:else}
          <p class="theme-text-muted italic">まだ自己紹介が登録されていません</p>
        {/if}
      </ProfileItemCard>
    {/if}

    <!-- モバイルでの区切り線 -->
    <hr class="theme-border md:hidden" />

    <!-- その他のプロフィール項目 -->
    <div class="grid grid-cols-1 gap-4 md:grid-cols-2 md:gap-8">
      {#each profileItems.filter(p => p.label !== '自己紹介') as item, index (item.profileItemId)}
        <ProfileItemCard
          label={item.label}
          value={item.value}
          {isOwner}
          onSave={createSaveHandler(item)}
          showDivider={index < profileItems.length - 2}
        >
          <span class="theme-text-muted text-base italic">ー</span>
        </ProfileItemCard>
      {/each}
    </div>
  {:else}
    <div class="col-span-1 py-8 text-center md:col-span-2">
      <p class="theme-text-muted">プロフィール情報がまだ登録されていません。</p>
    </div>
  {/if}
</div>
