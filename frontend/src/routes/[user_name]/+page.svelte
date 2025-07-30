<script lang="ts">
  import Editable from '$lib/components/Editable.svelte';

  import type { ProfileCardPageData } from '$lib/types/page';
  import type { ProfileItem } from '$lib/types/profile';

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

  async function handleItemSave(index: number, field: 'label' | 'value', newValue: string): Promise<boolean> {
    const item = profileItems[index];
    if (!item) return false;

    try {
      const { updateProfileItem } = await import('$lib/api-client/profile');
      const updatedItem = await updateProfileItem(data.profile.userId, item.profileItemId, {
        [field]: newValue
      });

      const newItems = [...profileItems];
      newItems[index] = updatedItem;
      profileItems = newItems;
      return true;
    } catch (error) {
      console.error('プロフィール項目の更新に失敗しました:', error);
      // エラーの場合は元の値に戻す
      return false;
    }
  }
</script>

<div class="mt-8 grid grid-cols-1 gap-8 md:grid-cols-2">
  {#if profileItems && profileItems.length > 0}
    {#each profileItems as item, index (item.profileItemId)}
      <div
        class="group relative rounded-3xl border-b border-orange-400 bg-white p-6 transition-all duration-300 {isOwner
          ? 'hover:border-orange-300 hover:shadow-lg'
          : ''}"
      >
        <Editable
          {isOwner}
          value={item.label}
          onSave={(newLabel) => handleItemSave(index, 'label', newLabel)}
          inputType="input"
          validationType="profileLabel"
        >
          <div
            class="relative {isOwner
              ? 'cursor-pointer transition-all duration-200 hover:-mx-2 hover:-my-1 hover:rounded-md hover:bg-orange-50 hover:px-2 hover:py-1'
              : ''}"
          >
            <p class="mb-1 text-sm font-medium tracking-wide text-gray-700">{item.label}</p>
          </div>
        </Editable>

        <Editable
          {isOwner}
          value={item.value}
          onSave={(newValue) => handleItemSave(index, 'value', newValue)}
          inputType="input"
          validationType="profileValue"
        >
          <div
            class="relative {isOwner
              ? 'cursor-pointer transition-all duration-200 hover:-mx-2 hover:-my-1 hover:rounded-md hover:bg-gray-50 hover:px-2 hover:py-1'
              : ''}"
          >
            <p class="text-lg font-semibold break-words text-gray-700">
              {#if item.value}
                {item.value}
              {:else}
                <span class="text-base text-gray-400 italic">ー</span>
              {/if}
            </p>
          </div>
        </Editable>

        {#if isOwner}
          <div
            class="pointer-events-none absolute top-4 right-4 text-gray-400 opacity-0 transition-opacity duration-300 group-hover:opacity-100"
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
    {/each}
  {:else}
    <div class="col-span-1 py-8 text-center md:col-span-2">
      <p class="text-gray-500">プロフィール情報がまだ登録されていません。</p>
    </div>
  {/if}
</div>
