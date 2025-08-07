<script lang="ts">
  import Editable from "$lib/components/form/Editable.svelte";
  import ProfileItemCard from "./components/ProfileItemCard.svelte";
  import type { ProfileItem } from "$lib/types";
  import type { PageData } from "./$types";
  import { updateProfileItemValue, updateUserSelfIntroduction } from "$lib/utils/profileUpdates";

  type Props = {
    data: PageData;
  };

  const { data }: Props = $props();

  const isOwner = data.isOwner;
  const initialProfileItems = data.profileItems;

  let profileItems = $state<ProfileItem[]>(
    Array.isArray(initialProfileItems)
      ? [...initialProfileItems].sort((a, b) => a.displayOrder - b.displayOrder)
      : []
  );

  let selfIntroduction = $state(data.profile.selfIntroduction || "");

  const createItemSaveHandler =
    (index: number) =>
    async (newValue: string): Promise<boolean> => {
      const item = profileItems[index];
      if (!item) return false;

      try {
        const updatedItem = await updateProfileItemValue(
          data.profile.userId,
          item.profileItemId,
          newValue
        );

        const newItems = [...profileItems];
        newItems[index] = updatedItem;
        profileItems = newItems;
        return true;
      } catch (error) {
        console.error("プロフィール項目の更新に失敗しました:", error);
        return false;
      }
    };

  const handleSelfIntroductionSave = async (newValue: string): Promise<boolean> => {
    try {
      await updateUserSelfIntroduction(data.profile.userId, newValue);
      selfIntroduction = newValue;
      return true;
    } catch (error) {
      console.error("自己紹介の更新に失敗しました:", error);
      return false;
    }
  };
</script>

<!-- 自己紹介セクション -->
<div class="mt-8">
  <div
    class="group theme-bg-surface relative rounded-2xl border border-gray-300 p-6 transition-all duration-300 dark:border-gray-600 {isOwner
      ? 'theme-visitor-hover cursor-pointer hover:border-orange-300'
      : ''}"
  >
    <div class="mb-4">
      <p class="theme-text-secondary mb-1 text-sm font-medium tracking-wide">自己紹介</p>
    </div>

    <Editable
      {isOwner}
      value={selfIntroduction}
      onSave={handleSelfIntroductionSave}
      inputType="textarea"
      validationType="selfIntroduction"
      placeholder="自己紹介を書いてみましょう..."
    >
      <div class="relative">
        {#if selfIntroduction}
          <p
            class="theme-text-primary text-base leading-relaxed font-semibold break-words whitespace-pre-wrap"
          >
            {selfIntroduction}
          </p>
        {:else if isOwner}
          <p
            class="theme-text-muted text-base leading-relaxed font-semibold whitespace-pre-wrap italic"
          >
            {`例： hito Q太郎です！普段は会社員をしています。
        趣味はゲームと料理です。最近は〇〇というゲームにハマっています！
        気軽に話しかけてください！よろしくお願いします！`}
          </p>
        {:else}
          <p class="theme-text-muted italic">まだ自己紹介が登録されていません</p>
        {/if}
      </div>
    </Editable>

    {#if isOwner}
      <div
        class="theme-text-muted pointer-events-none absolute top-4 right-4 opacity-0 transition-opacity duration-300 group-hover:opacity-100"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          class="h-5 w-5"
          viewBox="0 0 20 20"
          fill="currentColor"
        >
          <path d="M17.414 2.586a2 2 0 00-2.828 0L7 10.172V13h2.828l7.586-7.586a2 2 0 000-2.828z" />
          <path
            fill-rule="evenodd"
            d="M2 6a2 2 0 012-2h4a1 1 0 010 2H4v10h10v-4a1 1 0 112 0v4a2 2 0 01-2 2H4a2 2 0 01-2-2V6z"
            clip-rule="evenodd"
          />
        </svg>
      </div>
    {/if}
  </div>
</div>

<!-- プロフィール項目 -->
<div class="mt-8 grid grid-cols-1 md:grid-cols-2 md:gap-8">
  {#if profileItems && profileItems.length > 0}
    {#each profileItems as item, index (item.profileItemId)}
      <ProfileItemCard
        {item}
        {isOwner}
        showDivider={index < profileItems.length - 1}
        onSave={createItemSaveHandler(index)}
      />
    {/each}
  {:else}
    <div class="col-span-1 py-8 text-center md:col-span-2">
      <p class="theme-text-muted">プロフィール情報がまだ登録されていません。</p>
    </div>
  {/if}
</div>
