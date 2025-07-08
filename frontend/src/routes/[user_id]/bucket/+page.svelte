<script lang="ts">
  import BucketList from './BucketList.svelte';

  type Props = {
    data: {
      buckets: any[]; // 本来はBucket型
      isOwner: boolean;
    }
  };

  const { data } = $props();
  let { buckets, isOwner } = data;
</script>

<BucketList {buckets} {isOwner} />
