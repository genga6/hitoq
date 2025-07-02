<script lang="ts">
  import BucketList from './BucketList.svelte';
  
  const { data } = $props();
  let buckets = data.buckets || [];
</script>

<BucketList { buckets } />