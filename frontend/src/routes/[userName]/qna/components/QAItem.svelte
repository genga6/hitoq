<script lang="ts">
  import Editable from "$lib/components/form/Editable.svelte";
  import EditIcon from "$lib/components/ui/EditIcon.svelte";
  import CommentForm from "./CommentForm.svelte";
  import MessageThread from "./MessageThread.svelte";
  import ActionButtons from "./ActionButtons.svelte";
  import type { BaseUser, Message, CategoryInfo } from "$lib/types";
  import { createOperationId } from "$lib/utils/optimisticUI";
  import { loadingStore } from "$lib/stores/loadingStore";

  const {
    question,
    answer,
    answerId,
    categoryInfo,
    isOwner,
    onUpdate,
    onUpdateError, // エラー時のロールバック用
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
    onUpdate: (newAnswer: string) => Promise<boolean>;
    onUpdateError?: (originalAnswer: string) => void; // ロールバック用
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
  
  // 楽観的UI状態管理
  const operationId = createOperationId('qa-answer-update', answerId?.toString() || 'new');

  async function handleAnswerSave(newAnswer: string): Promise<boolean> {
    const originalAnswer = answer;
    
    try {
      // 楽観的UI開始
      loadingStore.startOperation(operationId);
      
      // 親コンポーネントの更新処理を呼び出し
      const success = await onUpdate(newAnswer);
      
      if (success) {
        loadingStore.finishOperation(operationId);
        isEditing = false;
        return true;
      } else {
        throw new Error('更新に失敗しました');
      }
    } catch (error) {
      console.error("回答の保存に失敗しました:", error);
      
      // エラー状態
      loadingStore.finishOperation(operationId);
      
      // 親コンポーネントにロールバックを通知
      onUpdateError?.(originalAnswer);
      
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
  role={isOwner && answer ? 'button' : undefined}
  tabindex={isOwner && answer ? 0 : -1}
  onclick={isOwner && answer
    ? (e) => {
        // インタラクションボタンのクリックを除外
        if (e.target instanceof Element && e.target.closest('.interaction-buttons')) {
          return;
        }
        startEditing();
      }
    : undefined}
  onkeydown={isOwner && answer
    ? (e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          // インタラクションボタンのフォーカスを除外
          if (e.target instanceof Element && e.target.closest('.interaction-buttons')) {
            return;
          }
          startEditing();
        }
      }
    : undefined}
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
        onToggleMessages={() => { showMessagesThread = !showMessagesThread; }}
      />
    </div>
  {/if}
</div>


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
