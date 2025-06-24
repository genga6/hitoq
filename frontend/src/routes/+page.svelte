<script lang="ts">
  const handleStart = () => {
    alert("まだ機能は実装されていません");
  }
</script>

<main class="min-h-screen bg-white flex flex-col items-center justify-center px-4 text-center space-y-10">
  <section>
    <h1 class="text-4xl sm:text-6xl font-bold mb-4 text-gray-900">hitoQ</h1>
  <button
    on:click={handleStart}
    class="mt-6 bg-blue-600 text-white px-6 py-3 rounded-2xl shadow-md hover:bg-blue-700 transition"
  >
    はじめる！
  </button>
</section>
</main>
