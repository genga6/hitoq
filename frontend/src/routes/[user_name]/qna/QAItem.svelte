<script lang="ts">
  import QuestionAnswerCard from "$lib/components/QuestionAnswerCard.svelte";
  import ActionButtons from "./ActionButtons.svelte";
  import CommentForm from "./CommentForm.svelte";
  import MessageThread from "./MessageThread.svelte";
  import { getMessageThread } from "$lib/api-client/messages";
  import type { BaseUser, Message, CategoryInfo } from "$lib/types";

  const {
    question,
    answer,
    answerId,
    categoryInfo,
    isOwner,
    onUpdate,
    profileUserId,
    profileUserName,
    relatedMessages = [],
    currentUser = null,
    isLoggedIn = false
  } = $props<{
    question: string;
    answer: string;
    answerId?: number;
    categoryInfo?: CategoryInfo;
    isOwner: boolean;
    onUpdate: (newAnswer: string) => void;
    profileUserId?: string;
    profileUserName?: string;
    relatedMessages?: Message[];
    currentUser?: BaseUser;
    isLoggedIn?: boolean;
  }>();

  let showMessagesThread = $state(false);
  let showCommentForm = $state(false);
  let threadMessages = $state<Message[]>([]);
  let editedAnswer = $state(answer);
  let isEditing = $state(false);

  function handleAnswerChange(newAnswer: string) {
    editedAnswer = newAnswer;
  }

  function handleSave() {
    onUpdate(editedAnswer);
    isEditing = false;
  }

  function startEditing() {
    editedAnswer = answer;
    isEditing = true;
  }

  function cancelEdit() {
    editedAnswer = answer;
    isEditing = false;
  }

  function toggleMessagesThread() {
    showMessagesThread = !showMessagesThread;
    if (showMessagesThread && relatedMessages.length > 0) {
      loadRelatedMessagesThread();
    }
  }

  async function loadRelatedMessagesThread() {
    try {
      if (relatedMessages.length > 0 && relatedMessages[0].messageId) {
        threadMessages = await getMessageThread(relatedMessages[0].messageId);
      }
    } catch (error) {
      console.error("Failed to load related messages thread:", error);
    }
  }

  function showCommentInput() {
    showCommentForm = true;
  }

  function cancelComment() {
    showCommentForm = false;
  }

  function handleCommentSuccess() {
    showCommentForm = false;
  }
</script>

<QuestionAnswerCard
  question={typeof question === "string" ? question : question.text}
  answer={isEditing ? editedAnswer : answer}
  {categoryInfo}
  mode={isOwner && isEditing ? "edit" : "display"}
  {isOwner}
  onAnswerChange={handleAnswerChange}
  primaryAction={isOwner && isEditing
    ? {
        label: "保存",
        onClick: handleSave,
        disabled: !editedAnswer?.trim()
      }
    : undefined}
  secondaryAction={isOwner && isEditing
    ? {
        label: "キャンセル",
        onClick: cancelEdit
      }
    : undefined}
>
  {#if isOwner && !isEditing && answer}
    <button
      onclick={startEditing}
      class="theme-text-muted hover:theme-text-secondary absolute top-2 right-2 text-xs opacity-0 transition-opacity group-hover:opacity-100"
    >
      編集
    </button>
  {/if}

  <!-- アクションボタン -->
  <ActionButtons
    {isOwner}
    {profileUserId}
    {profileUserName}
    {answerId}
    {answer}
    {isLoggedIn}
    {currentUser}
    {relatedMessages}
    onShowComment={showCommentInput}
    onToggleMessages={toggleMessagesThread}
  />
</QuestionAnswerCard>

<!-- コメントフォーム -->
<CommentForm
  {showCommentForm}
  {profileUserId}
  {answerId}
  onCancel={cancelComment}
  onSuccess={handleCommentSuccess}
/>

<!-- メッセージスレッド -->
<MessageThread
  {threadMessages}
  {relatedMessages}
  {showMessagesThread}
  {isLoggedIn}
  {currentUser}
  onClose={() => (showMessagesThread = false)}
/>
