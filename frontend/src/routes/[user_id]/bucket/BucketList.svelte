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
  };

  let { buckets: initialBuckets } = $props();
  let buckets = $state<Bucket[]>(initialBuckets || []);

  let nextId = $derived(() => 
    Math.max(0, ...buckets.map(b => b.id)) + 1
  );

  async function addItem() {
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
      b.id === id ? { ...b, content: newContent } : b
    );
  }

  function deleteItem(id: number) {
    const item = buckets.find(b => b.id === id);
    if (!item) return;
    const confirmed = confirm(`「${item.content}」を削除してもよろしいですか？`);
    if (confirmed) {
      buckets = buckets.filter(b => b.id !== id);
    }
  }
</script>

<div class="space-y-2">
  {#each buckets as bucket (bucket.id)}
    <BucketListItem
      content={bucket.content}
      checked={bucket.checked}
      isNew={bucket.isNew}
      onToggle={() => toggleItem(bucket.id)}
      onEdit={(newContent) => editItem(bucket.id, newContent)}
      onDelete={() => deleteItem(bucket.id)}
    />
  {/each}

  <div class="flex justify-center mt-4">
    <button
      onclick={addItem}
      class="w-1/2 mt-4 py-2 px-4 rounded-xl bg-orange-100 text-orange-500 font-semibold hover:bg-orange-200 active:bg-orange-300 transition duration-200"
    >
      ＋ 新しいバケットを追加
    </button>
  </div>
</div>