<script lang="ts">
  import { goto } from '$app/navigation';
  import EditButton from '$lib/components/EditButton.svelte';
  
  const { data } = $props<{ data: any }>();

  const editProfile = () => {
    goto(`/${data.userId}/edit`);
  };
</script>

<!-- 何を表示するか検討中 -->

{#if data.isOwner}
  <EditButton onClick={editProfile} />
{/if}