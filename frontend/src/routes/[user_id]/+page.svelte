<script lang="ts">
  import { goto } from '$app/navigation';
  export let data;

  const editProfile = () => {
    goto(`/edit`);
  };
</script>

<main class="min-h-screen p-6 bg-gray-100 flex justify-center">
  <div class="bg-white rounded-2xl shadow-lg p-6 w-full max-w-2xl space-y-6 text-left">
    <div class="flex items-start space-x-4">
      <img src={data.profileUserIconUrl || 'https://via.placeholder.com/80'} alt="User Icon" class="w-16 h-16 rounded-full border border-gray-300" />
      <div>
        <h2 class="text-2xl font-bold text-gray-800">{data.profileUserName}</h2>
        <p class="text-gray-600 mt-2">{data.bio}</p>
      </div>
    </div>

    {#each data.featuredAnswers as item}
      <div class="bg-gray-50 p-4 rounde-lg border border-gray-200">
        <p class="text-sm text-gray-500">Q. {item.question}</p>
        <p class="mt-1 text-gray-800">A. {item.answer}</p>
      </div>
    {/each}

    <hr class="my-4" />
    <div class="space-y-2">
      {#each data.sections as section}
        <button
          on:click={() => goto(`/${data.user_id}/${section.id}`)}
          class="flex items-center justify-between w-full bg-gray-100 px-4 py-3 rounded-lg shadow-sm hover:bg-gray-200 transition"
        >
          <span>{section.icon} {section.label}</span>
          <span class="text-gray-500">▶</span>
        </button>
      {/each}
    </div>

    {#if data.isOwner}
      <div class="text-right pt-4">
        <button
          on:click={editProfile}
          class="bg-orange-400 text-white px-8 py-3 rounded-full shadow-md hover:bg-orange-300 transition font-bold"
        >
          編集する
        </button>
      </div>
    {/if}
  </div>
</main>
