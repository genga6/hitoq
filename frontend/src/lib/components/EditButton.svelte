<script lang="ts">
  let { onClick } = $props<{ onClick: () => void }>();
</script>

<div class="text-right pt-4">
  <button
    onclick={onClick}
    class="bg-orange-400 text-white px-6 py-2 rounded-full border border-orange-300 hover:bg-orange-300 transition font-semibold"
  >
    編集する
  </button>
</div>
