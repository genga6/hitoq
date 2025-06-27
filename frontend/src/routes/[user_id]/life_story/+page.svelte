<script lang="ts">
  import ProfileHeader from '$lib/components/ProfileHeader.svelte';
  export let data;

  const { isOwner, lifeStory, profileUserName, profileUserIconUrl } = data;

  let editedStory = {
    childhood: lifeStory?.childhood ?? '', 
    studentDays: lifeStory?.studentDays ?? '', 
    now: lifeStory?.now ?? '', 
  };

  const saveLifeStory = () => {
    alert('保存機能は未実装です');
    // TODO: Supabaseにpatchする処理を実装
  };
</script>

<main class="min-h-screen p-6 bg-gray-100 flex justify-center">
  <div class="bg-white rounded-2xl shadow-lg p-6 w-full max-w-2xl space-y-8 text-left">

    <ProfileHeader userName={profileUserName} iconUrl={profileUserIconUrl} subtitle="📜 自分史" />

    <!-- childhood -->
    <section>
      <h2 class="text-xl text-gray-600 font-semibold mb-2">👶 子ども時代</h2>
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
      <h2 class="text-xl text-gray-600 font-semibold mb-2">🎓 学生時代</h2>
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
      <h2 class="text-xl text-gray-600 font-semibold mb-2">🌱 今・これから</h2>
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

    {#if isOwner}
      <div class="text-right pt-4">
        <button
          on:click={saveLifeStory}
          class="bg-orange-400 text-white px-8 py-3 rounded-full shadow-md hover:bg-orange-300 transition font-bold"
        >
          保存
        </button>
      </div>
    {/if}
  </div>
</main>