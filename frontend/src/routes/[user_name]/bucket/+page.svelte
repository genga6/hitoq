<script lang="ts">
  import BucketList from './BucketList.svelte';
  import type { BucketListPageData } from '$lib/types/page';

  const { data }: { data: BucketListPageData } = $props();
  const { bucketListItems, isOwner } = data;

  // Map bucketListItems to the format expected by BucketList component
  const buckets = (bucketListItems || []).map((item) => ({
    id: item.bucketListItemId,
    content: item.content,
    checked: item.isCompleted,
    displayOrder: item.displayOrder,
    isNew: false
  }));
</script>

<BucketList {buckets} {isOwner} userId={data.profile.userId} />
