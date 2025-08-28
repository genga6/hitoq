<script lang="ts">
  import ProfileItemCard from "./components/ProfileItemCard.svelte";
  import type { ProfileItem } from "$lib/types";
  import type { PageData } from "./$types";
  import { invalidate } from "$app/navigation";
  import { updateProfileItem } from "$lib/api-client/profile";

  type Props = {
    data: PageData;
  };

  const { data }: Props = $props();
  const isOwner = $derived(data.isOwner);

  let profileItems = $derived([...(data.profileItems || [])].sort((a, b) => a.displayOrder - b.displayOrder));

  const updateProfileItemValue = async (
    userId: string,
    profileItemId: string,
    newValue: string
  ): Promise<ProfileItem> => {
    return updateProfileItem(userId, profileItemId, { value: newValue });
  };

  const createSaveHandler = (item: ProfileItem) => {
    return async (newValue: string): Promise<boolean> => {
      try {
        await updateProfileItemValue(data.profile.userId, item.profileItemId, newValue);

        // Wait for the data to be re-fetched and the prop to be updated
        await invalidate(`user:${data.profile.userName}:profile`);

        return true;
      } catch (error) {
        console.error("プロフィールの更新に失敗しました:", error);
        return false;
      }
    };
  };
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
