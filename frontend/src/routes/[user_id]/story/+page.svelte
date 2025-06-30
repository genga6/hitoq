<script lang="ts">
  import { goto } from '$app/navigation';
  import EditButton from '$lib/components/EditButton.svelte';
  export let data;

  const editProfile = () => {
    goto(`/${data.userId}/edit`);
  };

  export let lifeStory: {
    childhood?: string;
    studentDays?: string;
    now?: string;
  };
  export let isOwner: boolean;

  let editedStory = {
    childhood: lifeStory?.childhood || '',
    studentDays: lifeStory?.studentDays || '',
    now: lifeStory?.now || ''
  };

  const saveLifeStory = () => {
    alert('保存機能は未実装です');
  };
</script>

<!-- childhood -->
<section>
  <h2 class="text-xl text-gray-600 font-semibold mb-2">子ども時代</h2>
  {#if isOwner}
    <textarea
      bind:value={editedStory.childhood}
      rows="4"
      placeholder="泣き虫でした。"
      class="w-full p-3 border border-gray-300 rounded-md text-gray-700 focus:outline-none focus:ring-2 focus:ring-orange-400"
    ></textarea>
  {:else}
    <p class="whitespace-pre-line text-gray-700">{lifeStory?.childhood || '準備中'}</p>
  {/if}
</section>

<!-- studentDays -->
<section>
  <h2 class="text-xl text-gray-600 font-semibold mb-2">学生時代</h2>
  {#if isOwner}
    <textarea
      bind:value={editedStory.studentDays}
      rows="4"
      placeholder="勉強せずに野球ばかりしてました。"
      class="w-full p-3 border border-gray-300 rounded-md text-gray-700 focus:outline-none focus:ring-2 focus:ring-orange-400"
    ></textarea>
  {:else}
    <p class="whitespace-pre-line text-gray-700">{lifeStory?.studentDays || '準備中'}</p>
  {/if}
</section>

<!-- now -->
<section>
  <h2 class="text-xl text-gray-600 font-semibold mb-2">今・これから</h2>
  {#if isOwner}
    <textarea
      bind:value={editedStory.now}
      rows="4"
      placeholder="読書が好きになりました。"
      class="w-full p-3 border border-gray-300 rounded-md text-gray-700 focus:outline-none focus:ring-2 focus:ring-orange-400"
    ></textarea>
  {:else}
    <p class="whitespace-pre-line text-gray-700">{lifeStory?.now || '準備中'}</p>
  {/if}
</section>

{#if data.isOwner}
  <EditButton onClick={editProfile} />
{/if}