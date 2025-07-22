<script lang="ts">
  import Editable from "$lib/components/Editable.svelte";

  import type { ProfileCardPageData } from "$lib/types/page";
  import type { ProfileItem } from "$lib/types/profile";

  type Props = {
    data: ProfileCardPageData;
  };

  const { data }: Props = $props();
  
  // レイアウトとページの両方からデータを取得
  const isOwner = data.isOwner;
  const initialProfileItems = data.profileItems;

  let profileItems = $state<ProfileItem[]>(Array.isArray(initialProfileItems) ? initialProfileItems : []);

  function handleItemSave(index: number, field: 'label' | 'value', newValue: string) {
    // Replace API call
    console.log(`Saving item ${index}, field ${field} to ${newValue}`);

    const newItems = [...profileItems];
    newItems[index] = { ...newItems[index], [field]: newValue };
    profileItems = newItems;
  }
</script>

<div class="grid grid-cols-1 md:grid-cols-2 gap-8 mt-8">
  {#if profileItems && profileItems.length > 0}
    {#each profileItems as item, index (item.profileItemId)}
    <div
      class="group relative rounded-3xl border border-orange-200 bg-white p-6 transition-all duration-300 {isOwner ? 'hover:shadow-lg hover:border-orange-300' : ''}"
    >
      <Editable
        isOwner={isOwner}
        value={item.label}
        onSave={(newLabel) => handleItemSave(index, 'label', newLabel)}
        input_type="input"
      >
        <div class="relative {isOwner ? 'cursor-pointer hover:bg-orange-50 hover:rounded-md hover:px-2 hover:py-1 hover:-mx-2 hover:-my-1 transition-all duration-200' : ''}">
          <p class="text-sm text-orange-600 font-medium mb-1 tracking-wide">{item.label}</p>
          {#if isOwner}
            <div class="absolute top-0 right-0 opacity-0 transition-opacity duration-200 group-hover:opacity-100">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3 text-orange-400" viewBox="0 0 20 20" fill="currentColor">
                <path d="M17.414 2.586a2 2 0 00-2.828 0L7 10.172V13h2.828l7.586-7.586a2 2 0 000-2.828z" />
                <path fill-rule="evenodd" d="M2 6a2 2 0 012-2h4a1 1 0 010 2H4v10h10v-4a1 1 0 112 0v4a2 2 0 01-2 2H4a2 2 0 01-2-2V6z" clip-rule="evenodd" />
              </svg>
            </div>
          {/if}
        </div>
      </Editable>
      
      <Editable
        isOwner={isOwner}
        value={item.value}
        onSave={(newValue) => handleItemSave(index, 'value', newValue)}
        input_type="input"
      >
        <div class="relative {isOwner ? 'cursor-pointer hover:bg-gray-50 hover:rounded-md hover:px-2 hover:py-1 hover:-mx-2 hover:-my-1 transition-all duration-200' : ''}">
          <p class="text-lg font-semibold text-gray-700 break-words">
            {#if item.value}
              {item.value}
            {:else}
              <span class="text-base text-gray-400 italic">ー</span>
            {/if}
          </p>
          {#if isOwner}
            <div class="absolute top-0 right-0 opacity-0 transition-opacity duration-200 group-hover:opacity-100">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3 text-gray-400" viewBox="0 0 20 20" fill="currentColor">
                <path d="M17.414 2.586a2 2 0 00-2.828 0L7 10.172V13h2.828l7.586-7.586a2 2 0 000-2.828z" />
                <path fill-rule="evenodd" d="M2 6a2 2 0 012-2h4a1 1 0 010 2H4v10h10v-4a1 1 0 112 0v4a2 2 0 01-2 2H4a2 2 0 01-2-2V6z" clip-rule="evenodd" />
              </svg>
            </div>
          {/if}
        </div>
      </Editable>

      {#if isOwner}
        <div class="absolute top-4 right-4 text-gray-400 opacity-0 transition-opacity duration-300 group-hover:opacity-100 pointer-events-none">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
            <path d="M17.414 2.586a2 2 0 00-2.828 0L7 10.172V13h2.828l7.586-7.586a2 2 0 000-2.828z" />
            <path fill-rule="evenodd" d="M2 6a2 2 0 012-2h4a1 1 0 010 2H4v10h10v-4a1 1 0 112 0v4a2 2 0 01-2 2H4a2 2 0 01-2-2V6z" clip-rule="evenodd" />
          </svg>
        </div>
      {/if}
    </div>
    {/each}
  {:else}
    <div class="col-span-1 md:col-span-2 text-center py-8">
      <p class="text-gray-500">プロフィール情報がまだ登録されていません。</p>
    </div>
  {/if}
</div>
