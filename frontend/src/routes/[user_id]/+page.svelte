<script lang="ts">
  import Editable from "$lib/components/Editable.svelte";

  type ProfileItems = {
    label: string;
    value: string;
  }[];

  type Props = {
    data: {
      profileItems: ProfileItems;
      isOwner: boolean;
    }
  };

  const { data }: Props = $props();
  const { isOwner, profileItems: initialProfileItems } = data;

  let profileItems = $state(initialProfileItems);

  function handleItemSave(index: number, field: 'label' | 'value', newValue: string) {
    // Replace API call
    console.log(`Saving item ${index}, field ${field} to ${newValue}`);

    const newItems = [...profileItems];
    newItems[index] = { ...newItems[index], [field]: newValue };
    profileItems = newItems;
  }
</script>

<div class="grid grid-cols-1 md:grid-cols-2 gap-8 mt-8">
  {#each profileItems as item, index (index)}
    <div
      class="group relative rounded-3xl border border-orange-200 bg-white p-6 transition-all duration-300 {isOwner ? 'hover:shadow-lg hover:border-orange-300' : ''}"
    >
      <Editable
        isOwner={isOwner}
        value={item.label}
        onSave={(newLabel) => handleItemSave(index, 'label', newLabel)}
        input_type="input"
      >
        <p class="text-sm text-orange-600 font-medium mb-1 tracking-wide">{item.label}</p>
      </Editable>
      
      <Editable
        isOwner={isOwner}
        value={item.value}
        onSave={(newValue) => handleItemSave(index, 'value', newValue)}
        input_type="input"
      >
        <p class="text-lg font-semibold text-gray-700 break-words">{item.value}</p>
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
</div>
