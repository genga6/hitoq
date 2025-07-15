<script lang="ts">
	import { tick } from 'svelte';
  import BucketListItem from './BucketListItem.svelte';

  type Bucket = {
    id: number;
    content: string;
    checked: boolean;
    isNew?: boolean;
  };

  type Props = {
    buckets: Bucket[];
    isOwner: boolean;
  };

  let { buckets: initialBuckets, isOwner } = $props();
  let buckets = $state<Bucket[]>(initialBuckets || []);

  let nextId = $derived(() =>
    Math.max(0, ...buckets.map(b => b.id)) + 1
  );

  async function addItem() {
    if (!isOwner) return;

    buckets = buckets.filter(b => !b.isNew || b.content.trim() !== '');

    const tempItem = {
      id: nextId(),
      content: '',
      checked: false,
      isNew: true,
    };
    buckets = [...buckets, tempItem];
    await tick(); // Wait for the DOM to update
  }

  function toggleItem(id: number) {
    buckets = buckets.map(b =>
      b.id === id ? { ...b, checked: !b.checked } : b
    );
  }

  function editItem(id: number, newContent: string) {
    buckets = buckets.map(b =>
      b.id === id ? { ...b, content: newContent, isNew: false } : b
    );
  }

  function deleteItem(id: number, force: boolean = false) {
    const item = buckets.find(b => b.id === id);
    if (!item) return;

    if (force || confirm(`「${item.content || '新しいバケット'}」を削除してもよろしいですか？`)) {
      buckets = buckets.filter(b => b.id !== id);
    }
  }

  function handleSave(id: number, newContent: string) {
    const item = buckets.find(b => b.id === id);
    if (!item) return;

    if (item.isNew && newContent.trim() === '') {
      deleteItem(id, true);
    } else {
      editItem(id, newContent);
    }
  }
</script>

<div class="space-y-2">
  {#each buckets as bucket (bucket.id)}
    <BucketListItem
      {bucket}
      {isOwner}
      onToggle={() => toggleItem(bucket.id)}
      onSave={(newContent) => handleSave(bucket.id, newContent)}
      onDelete={() => deleteItem(bucket.id)}
    />
  {/each}

  {#if isOwner}
    <div class="flex justify-center mt-4">
      <button
        onclick={addItem}
        class="w-1/2 mt-4 py-2 px-4 rounded-xl bg-orange-100 text-orange-500 font-semibold hover:bg-orange-200 active:bg-orange-300 transition duration-200"
      >
        ＋ 新しいバケットを追加
      </button>
    </div>
  {/if}
</div>
