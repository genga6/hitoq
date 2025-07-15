<script lang="ts">
  type Props = {
    displayName: string;
    iconUrl?: string;
    bio?: string;
  };
  const { displayName, iconUrl, bio }: Props = $props();
</script>

<div class="flex items-start space-x-4">
  <img
    src={iconUrl}
    alt="User Icon"
    class="w-20 h-20 rounded-full border border-gray-300"
  />
  <div>
    <h2 class="text-2xl font-bold text-gray-700">{displayName}</h2>

    {#if bio}
      <p class="text-gray-700 mt-2 whitespace-pre-line">{bio}</p>
    {/if}
  </div>
</div>
