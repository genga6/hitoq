<script lang="ts">
  type Props = {
    referenceAnswerId: number;
    profileUserName: string;
  };

  const { referenceAnswerId, profileUserName }: Props = $props();
</script>

<!-- 参照している回答がある場合 -->
<div class="mt-2 rounded-md border border-orange-200 bg-orange-50 p-2">
  <div class="flex items-start space-x-1.5">
    <svg
      class="mt-0.5 h-3 w-3 text-orange-500"
      fill="none"
      stroke="currentColor"
      viewBox="0 0 24 24"
    >
      <path
        stroke-linecap="round"
        stroke-linejoin="round"
        stroke-width="2"
        d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
      />
    </svg>
    <div>
      <p class="text-xs font-medium text-orange-800">このQ&Aに関連:</p>
      <a
        href="/{profileUserName}/qna#{referenceAnswerId}"
        class="text-xs text-orange-600 hover:text-orange-800 hover:underline"
      >
        Q&A回答 #{referenceAnswerId} を表示
      </a>
    </div>
  </div>
</div>
