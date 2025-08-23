<script lang="ts">
  import Editable from "$lib/components/form/Editable.svelte";
  import ProfileItemCard from "./components/ProfileItemCard.svelte";
  import type { ProfileItem } from "$lib/types";
  import type { PageData } from "./$types";
  import { updateProfileItemValue, updateUserSelfIntroduction } from "$lib/utils/profileUpdates";
import { invalidate } from "$app/navigation";

  type Props = {
    data: PageData;
  };

  const { data }: Props = $props();

  const isOwner = $derived(data.isOwner);

  let profileItems = $state<ProfileItem[]>([]);
  let selfIntroduction = $state("");

  // データが変更されたときに状態をリセット
  $effect(() => {
    profileItems = Array.isArray(data.profileItems)
      ? [...data.profileItems].sort((a, b) => a.displayOrder - b.displayOrder)
      : [];
    selfIntroduction = data.profile.selfIntroduction || "";
  });

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
        await invalidate(`user:${data.profile.userName}:profile`);
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
      await invalidate(`user:${data.profile.userName}:profile`);
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
    class="group theme-bg-surface relative rounded-2xl p-6 transition-all duration-300 md:border md:border-gray-300 md:dark:border-gray-600 {isOwner
      ? 'theme-visitor-hover cursor-pointer'
      : ''}"
  >
    <div class="mb-4">
      <p class="theme-text-secondary mb-1 text-sm font-semibold tracking-wide">自己紹介</p>
    </div>

    {#if isOwner}
      <Editable
        value={selfIntroduction}
        onSave={handleSelfIntroductionSave}
        inputType="textarea"
        validationType="selfIntroduction"
        placeholder="自己紹介を書いてみましょう..."
      >
        <div class="relative">
          {#if selfIntroduction}
            <p
              class="theme-text-primary text-base leading-relaxed break-words whitespace-pre-wrap"
            >
              {selfIntroduction}
            </p>
          {:else}
            <p
              class="theme-text-muted text-base leading-relaxed whitespace-pre-wrap italic opacity-50"
            >
例： hito Q太郎です！普段は会社員をしています。
趣味はゲームと料理です。最近は〇〇というゲームにハマッています！
気軽に話しかけてください！よろしくお願いします！
            </p>
          {/if}
        </div>
      </Editable>
    {:else}
      <div class="relative">
        {#if selfIntroduction}
          <p
            class="theme-text-primary text-base leading-relaxed break-words whitespace-pre-wrap"
          >
            {selfIntroduction}
          </p>
        {:else}
          <p class="theme-text-muted italic">まだ自己紹介が登録されていません</p>
        {/if}
      </div>
    {/if}

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
  
  <!-- モバイルでの区切り線 -->
  <hr class="theme-border mt-6 md:hidden" />
</div>

<!-- プロフィール項目 -->
<div class="mt-4 grid grid-cols-1 gap-4 md:grid-cols-2 md:gap-8">
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
