<script lang="ts">
  import Editable from "$lib/components/form/Editable.svelte";
  import EditIcon from "$lib/components/ui/EditIcon.svelte";
  import CommentForm from "./CommentForm.svelte";
  import MessageThread from "./MessageThread.svelte";
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
  let isEditing = $state(false);

  async function handleAnswerSave(newAnswer: string): Promise<boolean> {
    try {
      onUpdate(newAnswer);
      isEditing = false;
      return true;
    } catch (error) {
      console.error("回答の保存に失敗しました:", error);
      return false;
    }
  }

  function startEditing() {
    if (isOwner && answer) {
      isEditing = true;
    }
  }

  function cancelEditing() {
    isEditing = false;
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

<!-- svelte-ignore a11y_no_noninteractive_tabindex -->
<div 
  class="group relative theme-bg-surface rounded-2xl p-6 theme-border theme-visitor-hover transition-all duration-300 {isOwner && answer ? 'cursor-pointer' : ''}"
  role={isOwner && answer ? "button" : undefined}
  tabindex={isOwner && answer ? 0 : -1}
  onclick={(e) => {
    // インタラクションボタンのクリックを除外
    if (e.target instanceof Element && e.target.closest('.interaction-buttons')) {
      return;
    }
    startEditing();
  }}
  onkeydown={(e) => {
    if (isOwner && answer && (e.key === 'Enter' || e.key === ' ')) {
      e.preventDefault();
      // インタラクションボタンのフォーカスを除外
      if (e.target instanceof Element && e.target.closest('.interaction-buttons')) {
        return;
      }
      startEditing();
    }
  }}
>
  <!-- 質問エリア -->
  <div class="mb-2 {!isOwner && isLoggedIn && currentUser ? 'pr-20 sm:pr-16' : ''}">
    <p class="theme-text-muted mb-2 text-sm font-medium break-words sm:text-base">
      {typeof question === "string" ? question : question.text}
    </p>
    {#if categoryInfo}
      <span
        class="inline-flex items-center gap-1 rounded-full bg-orange-100 px-2.5 py-1 text-xs font-medium text-orange-700 dark:bg-orange-900/30 dark:text-orange-200"
      >
        <svg class="h-3 w-3" fill="currentColor" viewBox="0 0 20 20">
          <path
            fill-rule="evenodd"
            d="M3 4a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1V4zm0 4a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1V8zm0 4a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1v-2z"
            clip-rule="evenodd"
          />
        </svg>
        {categoryInfo.label}
      </span>
    {/if}
  </div>

  <!-- 回答エリア -->
  {#if answer}
    {#if isOwner && isEditing}
      <Editable
        value={answer}
        onSave={handleAnswerSave}
        onCancel={cancelEditing}
        inputType="textarea"
        validationType="qaAnswer"
        placeholder="回答を入力..."
        startInEditMode={true}
      >
        <p class="theme-text-primary text-base font-semibold break-words whitespace-pre-wrap sm:text-lg">
          {answer}
        </p>
      </Editable>
    {:else}
      <p class="theme-text-primary text-base font-semibold break-words whitespace-pre-wrap sm:text-lg">
        {answer}
      </p>
    {/if}
  {:else}
    <p class="theme-text-subtle text-sm italic sm:text-base">
      回答待ち
    </p>
  {/if}

  <!-- 編集アイコン -->
  <EditIcon show={isOwner && !!answer} />

  <!-- インタラクションボタン（いいね・コメント） -->
  {#if !isOwner && profileUserId && profileUserName && answer && isLoggedIn && currentUser}
    <div class="interaction-buttons absolute top-3 right-3 z-0 flex flex-col items-end gap-1 sm:flex-row sm:items-center sm:gap-1">
      <!-- ハートボタン（いいね） -->
      <button
        onclick={() => {/* TODO: いいね機能 */}}
        class="flex items-center gap-1 rounded-full px-2 py-1 text-xs sm:px-3 sm:py-1.5 sm:text-sm transition-all duration-200 hover:bg-gray-100 dark:hover:bg-gray-800 theme-text-muted hover:text-red-500"
        title="いいね"
        aria-label="いいね"
      >
        <svg
          class="h-3 w-3 transition-all duration-200 hover:scale-110 sm:h-4 sm:w-4"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"
          />
        </svg>
      </button>

      <!-- コメントボタン -->
      <button
        onclick={showCommentInput}
        class="flex items-center gap-1 rounded-full px-2 py-1 text-xs sm:px-3 sm:py-1.5 sm:text-sm transition-all duration-200 hover:bg-gray-100 dark:hover:bg-gray-800 theme-text-muted hover:text-blue-500"
        title="コメント"
        aria-label="コメントを追加"
      >
        <svg class="h-3 w-3 sm:h-4 sm:w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
          />
        </svg>
      </button>
    </div>
  {/if}
</div>

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
