<script lang="ts">
  import { sendMessage } from "$lib/api-client/messages";
  import TextareaForm from "$lib/components/TextareaForm.svelte";

  const { showCommentForm, profileUserId, answerId, onCancel, onSuccess } = $props<{
    showCommentForm: boolean;
    profileUserId?: string;
    answerId?: number;
    onCancel: () => void;
    onSuccess: () => void;
  }>();

  async function handleCommentSubmit(content: string) {
    if (!profileUserId) return;

    const messageData = {
      toUserId: profileUserId,
      messageType: "comment" as const,
      content,
      referenceAnswerId: answerId || undefined
    };

    await sendMessage(messageData);
    onSuccess();
  }
</script>

{#if showCommentForm}
  <div class="theme-bg-card mt-4 rounded-lg p-4 shadow-sm">
    <TextareaForm
      placeholder="この回答についてコメントを書く..."
      submitLabel="コメント送信"
      onSubmit={handleCommentSubmit}
      {onCancel}
    />
  </div>
{/if}
