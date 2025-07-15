<script lang="ts">
  import BucketList from './BucketList.svelte';
  import type { BucketListPageData } from '$lib/types/page';

  type Props = {
    data: BucketListPageData;
  };

  const { data } = $props();
  let { buckets, isOwner } = data;
</script>

<BucketList {buckets} {isOwner} />
