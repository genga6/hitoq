<script lang="ts">
  type Props = {
    userName: string;
    userIconUrl?: string;
    bio?: string;
  };
  const { userName, userIconUrl, bio }: Props = $props();
  console.log('ProfileHeader props:', { userName, userIconUrl, bio });

</script>

<div class="flex items-start space-x-4">
  <img
    src={userIconUrl || 'https://via.placeholder.com/80'}
    alt="User Icon"
    class="w-20 h-20 rounded-full border border-gray-300"
  />
  <div>
    <h2 class="text-2xl font-bold text-gray-700">{userName}</h2>

    {#if bio}
      <p class="text-gray-700 mt-2 whitespace-pre-line">{bio}</p>
    {/if}
  </div>
</div>
