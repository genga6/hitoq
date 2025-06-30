<script lang="ts">
  import ProfileHeader from '$lib/components/ProfileHeader.svelte';
  import TabNavigation from '$lib/components/TabNavigation.svelte';

  let { data } = $props<data>();
  const { userId, userName, userIconUrl, isOwner, bio } = data;
</script>

<main class="min-h-screen bg-gray-100 p-4 flex justify-center">
  <div class="bg-white shadow-lg rounded-2xl p-6 max-w-3xl w-full space-y-6">
    <ProfileHeader userName={userName} userIconUrl={userIconUrl} bio={bio}/>
    <TabNavigation userId={userId} />
    <slot />
  </div>
</main>
