<script lang="ts">
  export let iconUrl: string;
  export let userName: string;
  export let subtitle: string = '';
  </script>

  <div class="flex items-start space-x-4">
  <img
    src={iconUrl || 'https://via.placeholder.com/80'}
    alt="User Icon"
    class="w-16 h-16 rounded-full border border-gray-300"
  />
  <div>
    <h2 class="text-2xl font-bold text-gray-600">{userName}</h2>
    {#if subtitle}
      <p class="text-gray-600 mt-1">{subtitle}</p>
    {/if}
  </div>
</div>
