<script lang="ts">
  interface Props {
    onNewContact: () => void;
  }

  let { onNewContact }: Props = $props();
</script>

<div class="theme-alert-primary mb-8">
  <div class="flex items-center">
    <svg
      class="theme-alert-icon mr-3"
      fill="none"
      stroke="currentColor"
      viewBox="0 0 24 24"
    >
      <path
        stroke-linecap="round"
        stroke-linejoin="round"
        stroke-width="2"
        d="M5 13l4 4L19 7"
      ></path>
    </svg>
    <h3 class="theme-alert-title">送信完了</h3>
  </div>
  <p class="theme-alert-text">
    お問い合わせありがとうございます。内容を確認の上、必要に応じてご連絡いたします。
  </p>
  <button onclick={onNewContact} class="theme-alert-button">
    新しいお問い合わせを送信
  </button>
</div>