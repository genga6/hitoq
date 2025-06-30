<script lang="ts">
  import { onMount } from 'svelte';

  const userName = 'げんがる';
  const userIconUrl = 'https://via.placeholder.com/80'; // 仮アイコンURL

  const questions = [
    { id: 'q1', text: '好きな食べ物は？' },
    { id: 'q2', text: '大切にしている価値観は？' },
    { id: 'q3', text: '趣味やハマっていることは？' },
  ];

  let answers: Record<string, string> = {};

  onMount(() => {
    questions.forEach(q => {
      answers[q.id] = '';
    });
  });

  const handleSave = () => {
    console.log('保存された内容:', answers);
    // Supabaseに保存処理を追加
  };
</script>

<main class="min-h-screen p-6 bg-gray-100 flex justify-center">
  <div class="bg-white rounded-2xl shadow-lg p-6 w-full max-w-xl space-y-6">
    <!-- ユーザー情報 -->
    <div class="flex items-center space-x-4">
      <img src={userIconUrl} alt="User Icon" class="w-16 h-16 rounded-full border border-gray-300" />
      <h2 class="text-2xl font-bold text-gray-800">{userName}</h2>
    </div>

    <!-- 質問と回答 -->
    <div class="space-y-4">
      {#each questions as q}
        <div>
          <label for={q.id} class="block text-sm font-medium text-gray-700 mb-1">{q.text}</label>
          <textarea
            id={q.id}
            bind:value={answers[q.id]}
            rows="2"
            class="w-full border border-gray-300 rounded-md p-2 focus:outline-none focus:ring-2 focus:ring-orange-300"
          ></textarea>
        </div>
      {/each}
    </div>

    <!-- 保存ボタン -->
    <div class="text-right">
      <button
        on:click={handleSave}
        class="bg-orange-400 text-white px-6 py-2 rounded-xl shadow-md hover:bg-orange-500 transition font-semibold"
      >
        保存する
      </button>
    </div>
  </div>
</main>
