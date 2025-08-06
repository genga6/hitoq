<script lang="ts">
  import Editable from "$lib/components/Editable.svelte";
  import type { ProfileCardPageData, ProfileItem } from "$lib/types";

  type Props = {
    data: ProfileCardPageData;
  };

  const { data }: Props = $props();

  // レイアウトとページの両方からデータを取得
  const isOwner = data.isOwner;
  const initialProfileItems = data.profileItems;

  let profileItems = $state<ProfileItem[]>(
    Array.isArray(initialProfileItems)
      ? [...initialProfileItems].sort((a, b) => a.displayOrder - b.displayOrder)
      : []
  );

  let selfIntroduction = $state(data.profile.selfIntroduction || "");

  async function handleItemSave(index: number, field: "value", newValue: string): Promise<boolean> {
    const item = profileItems[index];
    if (!item) return false;

    try {
      const { updateProfileItem } = await import("$lib/api-client/profile");
      const updatedItem = await updateProfileItem(data.profile.userId, item.profileItemId, {
        [field]: newValue
      });

      const newItems = [...profileItems];
      newItems[index] = updatedItem;
      profileItems = newItems;
      return true;
    } catch (error) {
      console.error("プロフィール項目の更新に失敗しました:", error);
      // エラーの場合は元の値に戻す
      return false;
    }
  }

  async function handleSelfIntroductionSave(newValue: string): Promise<boolean> {
    try {
      console.log("🔄 自己紹介を保存中:", {
        userId: data.profile.userId,
        selfIntroduction: newValue
      });
      const { updateUser } = await import("$lib/api-client/profile");
      const result = await updateUser(data.profile.userId, {
        selfIntroduction: newValue
      });
      console.log("✅ 自己紹介の更新成功:", result);

      selfIntroduction = newValue;
      return true;
    } catch (error) {
      console.error("❌ 自己紹介の更新に失敗しました:", error);
      return false;
    }
  }
</script>

<!-- 自己紹介セクション -->
<div class="mt-8">
  <div
    class="group relative rounded-2xl border border-gray-300 dark:border-gray-600 theme-bg-surface p-6 transition-all duration-300 {isOwner
      ? 'cursor-pointer theme-visitor-hover hover:border-orange-300'
      : ''}"
  >
    <div class="mb-4">
      <p class="mb-1 text-sm font-medium tracking-wide theme-text-secondary">自己紹介</p>
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
            class="text-base leading-relaxed font-semibold break-words whitespace-pre-wrap theme-text-primary"
          >
            {selfIntroduction}
          </p>
        {:else if isOwner}
          <p
            class="text-base leading-relaxed font-semibold whitespace-pre-wrap theme-text-muted italic"
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
        class="pointer-events-none absolute top-4 right-4 theme-text-muted opacity-0 transition-opacity duration-300 group-hover:opacity-100"
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
      <div
        class="group relative rounded-2xl border border-gray-300 dark:border-gray-600 theme-bg-surface transition-all duration-300 md:border md:p-6 {isOwner
          ? 'cursor-pointer theme-visitor-hover hover:border-orange-300'
          : ''}"
      >
        <div class="p-6 md:p-0">
          <div class="relative">
            <p class="mb-2 text-sm font-medium tracking-wide theme-text-secondary">{item.label}</p>
          </div>

          <Editable
            {isOwner}
            value={item.value}
            onSave={(newValue) => handleItemSave(index, "value", newValue)}
            inputType="input"
            validationType="profileValue"
          >
            <div
              class="relative"
            >
              <p class="text-base font-semibold break-words theme-text-primary">
                {#if item.value}
                  {item.value}
                {:else}
                  <span class="text-base theme-text-muted italic">ー</span>
                {/if}
              </p>
            </div>
          </Editable>

          {#if isOwner}
            <div
              class="pointer-events-none absolute top-4 right-4 theme-text-muted opacity-0 transition-opacity duration-300 group-hover:opacity-100"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                class="h-5 w-5"
                viewBox="0 0 20 20"
                fill="currentColor"
              >
                <path
                  d="M17.414 2.586a2 2 0 00-2.828 0L7 10.172V13h2.828l7.586-7.586a2 2 0 000-2.828z"
                />
                <path
                  fill-rule="evenodd"
                  d="M2 6a2 2 0 012-2h4a1 1 0 010 2H4v10h10v-4a1 1 0 112 0v4a2 2 0 01-2 2H4a2 2 0 01-2-2V6z"
                  clip-rule="evenodd"
                />
              </svg>
            </div>
          {/if}
        </div>
        {#if index < profileItems.length - 1}
          <hr class="theme-border md:hidden" />
        {/if}
      </div>
    {/each}
  {:else}
    <div class="col-span-1 py-8 text-center md:col-span-2">
      <p class="theme-text-muted">プロフィール情報がまだ登録されていません。</p>
    </div>
  {/if}
</div>
