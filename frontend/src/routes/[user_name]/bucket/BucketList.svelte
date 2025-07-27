<script lang="ts">
  import { tick } from 'svelte';
  import BucketListItem from './BucketListItem.svelte';

  type Bucket = {
    id: number;
    content: string;
    checked: boolean;
    displayOrder?: number;
    isNew?: boolean;
  };

  type Props = {
    buckets: Bucket[];
    isOwner: boolean;
    userId: string;
  };

  let { buckets: initialBuckets, isOwner, userId }: Props = $props();
  let buckets = $state<Bucket[]>(initialBuckets || []);

  let nextId = $derived(() => Math.max(0, ...buckets.map((b) => b.id)) + 1);

  async function addItem() {
    if (!isOwner) return;

    buckets = buckets.filter((b) => !b.isNew || b.content.trim() !== '');

    const tempItem = {
      id: nextId(),
      content: '',
      checked: false,
      isNew: true
    };
    buckets = [...buckets, tempItem];
    await tick(); // Wait for the DOM to update
  }

  async function toggleItem(id: number) {
    const item = buckets.find((b: Bucket) => b.id === id);
    if (!item || item.isNew) return;

    try {
      const { updateBucketListItem } = await import('$lib/api/client');
      await updateBucketListItem(userId, id, { isCompleted: !item.checked });

      buckets = buckets.map((b: Bucket) => (b.id === id ? { ...b, checked: !b.checked } : b));
    } catch (error) {
      console.error('バケットリスト項目の更新に失敗しました:', error);
    }
  }

  async function editItem(id: number, newContent: string) {
    const item = buckets.find((b: Bucket) => b.id === id);
    if (!item) return;

    try {
      if (item.isNew) {
        const { createBucketListItem } = await import('$lib/api/client');
        const maxDisplayOrder = Math.max(
          0,
          ...buckets.filter((b) => !b.isNew).map((b) => b.displayOrder || 0)
        );
        const createdItem = await createBucketListItem(userId, {
          content: newContent,
          displayOrder: maxDisplayOrder + 1
        });

        // 作成されたアイテムの実際のIDで更新
        buckets = buckets.map((b: Bucket) =>
          b.id === id
            ? {
                ...b,
                id: createdItem.bucketListItemId,
                content: newContent,
                displayOrder: createdItem.displayOrder,
                isNew: false
              }
            : b
        );
      } else {
        const { updateBucketListItem } = await import('$lib/api/client');
        await updateBucketListItem(userId, id, { content: newContent });

        buckets = buckets.map((b: Bucket) => (b.id === id ? { ...b, content: newContent } : b));
      }
    } catch (error) {
      console.error('バケットリスト項目の保存に失敗しました:', error);
    }
  }

  async function deleteItem(id: number, force: boolean = false) {
    const item = buckets.find((b: Bucket) => b.id === id);
    if (!item) return;

    if (force || confirm(`「${item.content || '新しいバケット'}」を削除してもよろしいですか？`)) {
      try {
        if (!item.isNew) {
          const { deleteBucketListItem } = await import('$lib/api/client');
          await deleteBucketListItem(userId, id);
        }

        buckets = buckets.filter((b: Bucket) => b.id !== id);
      } catch (error) {
        console.error('バケットリスト項目の削除に失敗しました:', error);
      }
    }
  }

  function handleSave(id: number, newContent: string): boolean {
    const item = buckets.find((b: Bucket) => b.id === id);
    if (!item) return false;

    if (item.isNew && newContent.trim() === '') {
      if (confirm('バケットリストを削除しますか？')) {
        deleteItem(id, true);
        return true;
      } else {
        // キャンセルした場合は編集状態を維持
        return false;
      }
    } else {
      editItem(id, newContent);
      return true;
    }
  }

  function handleCancel(id: number) {
    const item = buckets.find((b: Bucket) => b.id === id);
    if (!item) return;

    if (item.isNew) {
      deleteItem(id, true);
    }
  }
</script>

<div class="space-y-2">
  {#each buckets as bucket (bucket.id)}
    <BucketListItem
      {bucket}
      {isOwner}
      onToggle={() => toggleItem(bucket.id)}
      onSave={(newContent: string) => handleSave(bucket.id, newContent)}
      onCancel={() => handleCancel(bucket.id)}
      onDelete={() => deleteItem(bucket.id)}
    />
  {/each}

  {#if isOwner}
    <div class="mt-4 flex justify-center">
      <button
        onclick={addItem}
        class="mt-4 w-1/2 rounded-xl bg-orange-100 px-4 py-2 font-semibold text-orange-500 transition duration-200 hover:bg-orange-200 active:bg-orange-300"
      >
        ＋ 新しいバケットを追加
      </button>
    </div>
  {/if}
</div>
