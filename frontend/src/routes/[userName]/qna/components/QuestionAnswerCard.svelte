<script lang="ts">
  import type { CategoryInfo } from "$lib/types";
  import Editable from "$lib/components/form/Editable.svelte";
  import TextareaForm from "$lib/components/form/TextareaForm.svelte";
  import { sendMessage } from "$lib/api-client/messages";


  const {
    question,
    answer = "",
    categoryInfo,
    mode = "display", // "display" | "edit" | "input"
    isOwner = false,
    placeholder = "回答を入力...",
    onAnswerChange,
    secondaryAction,
    children,
    // いいね・コメント機能用の新しいプロパティ
    answerId,
    profileUserId,
    profileUserName,
    currentUser,
    isLoggedIn = false,
    showInteractions = false,
    onCommentSuccess
  } = $props<{
    question: string;
    answer?: string;
    categoryInfo?: CategoryInfo;
    mode?: "display" | "edit" | "input";
    isOwner?: boolean;
    placeholder?: string;
    onAnswerChange?: (value: string) => void;
    primaryAction?: {
      label: string;
      onClick: () => void;
      disabled?: boolean;
    };
    secondaryAction?: {
      label: string;
      onClick: () => void;
    };
    children?: import("svelte").Snippet;
    // 新しいプロパティ
    answerId?: number;
    profileUserId?: string;
    profileUserName?: string;
    currentUser?: import("$lib/types").BaseUser;
    isLoggedIn?: boolean;
    showInteractions?: boolean;
    onCommentSuccess?: () => void;
  }>();

  let localAnswer = $state(answer);
  let isEditing = $state(false);
  let showCommentForm = $state(false);
  let isLiked = $state(false);
  let likeCount = $state(0);
  let isLikeSubmitting = $state(false);

  async function handleSave(newValue: string): Promise<boolean> {
    if (onAnswerChange) {
      // onAnswerChangeが非同期処理の場合に対応
      const result = onAnswerChange(newValue);
      if (result instanceof Promise) {
        try {
          await result;
          localAnswer = newValue;
          return true;
        } catch (error) {
          console.error('Save failed:', error);
          return false;
        }
      } else {
        localAnswer = newValue;
        return true;
      }
    }
    return false;
  }

  function handleCancel() {
    // 入力をキャンセルして元の値に戻す
    localAnswer = answer;
    isEditing = false;
  }

  function handleSkip() {
    if (secondaryAction) {
      secondaryAction.onClick();
    }
  }

  function startEditing() {
    isEditing = true;
  }

  async function handleHeartToggle() {
    if (!profileUserId || isLikeSubmitting) return;

    const wasLiked = isLiked;
    if (isLiked) {
      likeCount = Math.max(0, likeCount - 1);
      isLiked = false;
    } else {
      likeCount = likeCount + 1;
      isLiked = true;
    }

    try {
      isLikeSubmitting = true;

      const likeMessageData = {
        toUserId: profileUserId,
        messageType: "like" as const,
        content: `回答「${answer?.substring(0, 50)}...」にいいねしました`,
        referenceAnswerId: answerId || undefined
      };

      await sendMessage(likeMessageData);
    } catch (error) {
      console.error("いいね通知の送信に失敗しました:", error);

      if (wasLiked) {
        likeCount = likeCount + 1;
        isLiked = true;
      } else {
        likeCount = Math.max(0, likeCount - 1);
        isLiked = false;
      }
    } finally {
      isLikeSubmitting = false;
    }
  }

  function showCommentInput() {
    showCommentForm = true;
  }

  function cancelComment() {
    showCommentForm = false;
  }

  async function handleCommentSubmit(content: string) {
    if (!profileUserId) return;

    const messageData = {
      toUserId: profileUserId,
      messageType: "comment" as const,
      content,
      referenceAnswerId: answerId || undefined
    };

    await sendMessage(messageData);
    showCommentForm = false;
    onCommentSuccess?.();
  }
</script>

<div class="group relative">
  <!-- 質問エリア -->
  <div class="mb-2 {mode === 'display' && !isOwner ? 'pr-20 sm:pr-16' : ''}">
    <p class="theme-text-muted mb-2 text-sm font-medium break-words sm:text-base">
      {question}
    </p>
    <div class="flex items-center gap-2 flex-wrap">
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
  </div>

  <!-- 回答エリア -->
  {#if mode === "display"}
    {#if answer}
      <p
        class="theme-text-primary text-base font-semibold break-words whitespace-pre-wrap sm:text-lg"
      >
        {answer}
      </p>
    {:else}
      <p class="text-base font-semibold sm:text-lg">
        <span class="theme-text-subtle text-sm italic sm:text-base">ー</span>
      </p>
    {/if}
  {:else if (mode === "edit" || mode === "input") && !isEditing}
    <!-- 一覧状態（編集前） -->
    <div class="space-y-3">
      {#if localAnswer}
        <p class="theme-text-primary text-base font-semibold break-words whitespace-pre-wrap sm:text-lg">
          {localAnswer}
        </p>
      {:else}
        <p class="theme-text-muted text-base italic">
          {placeholder || "回答を入力..."}
        </p>
      {/if}
      
      <!-- アクションボタン -->
      <div class="flex items-center justify-end gap-3">
        {#if secondaryAction}
          <button
            onclick={handleSkip}
            class="theme-text-muted px-4 py-2 text-sm hover:opacity-80"
          >
            {secondaryAction.label}
          </button>
        {/if}
        <button
          onclick={startEditing}
          class="rounded-lg bg-orange-500 px-4 py-2 text-sm text-white hover:bg-orange-600"
        >
          回答する
        </button>
      </div>
    </div>
  {:else if (mode === "edit" || mode === "input") && isEditing}
    <!-- 編集状態 -->
    <Editable
      value={localAnswer}
      onSave={handleSave}
      onCancel={handleCancel}
      inputType="textarea"
      validationType="qaAnswer"
      {placeholder}
      startInEditMode={true}
    >
      <textarea
        value={localAnswer}
        {placeholder}
        class="theme-border theme-bg-surface theme-text-primary mb-3 w-full rounded-lg p-3 text-sm focus:border-orange-400 focus:outline-none"
        rows="3"
        readonly
      ></textarea>
    </Editable>
  {/if}

  <!-- インタラクションボタン（いいね・コメント） -->
  {#if showInteractions && !isOwner && profileUserId && profileUserName && answer && isLoggedIn && currentUser}
    <div class="absolute top-3 right-3 z-0 flex flex-col items-end gap-1 sm:flex-row sm:items-center sm:gap-1">
      <!-- ハートボタン（いいね） -->
      <button
        onclick={handleHeartToggle}
        disabled={isLikeSubmitting}
        class="flex items-center gap-1 rounded-full px-2 py-1 text-xs sm:px-3 sm:py-1.5 sm:text-sm transition-all duration-200 hover:bg-gray-100 dark:hover:bg-gray-800 {isLiked ? 'text-red-500' : 'theme-text-muted hover:text-red-500'}"
        title={isLiked ? "いいねを取り消す" : "いいね"}
        aria-label={isLiked ? "いいねを取り消す" : "いいね"}
      >
        {#if isLiked}
          <!-- 赤塗りハート -->
          <svg
            class="h-3 w-3 transition-all duration-200 sm:h-4 sm:w-4"
            fill="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"
            />
          </svg>
        {:else}
          <!-- 空のハート -->
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
        {/if}
        {#if likeCount > 0}
          <span class="font-medium transition-colors duration-200">{likeCount}</span>
        {/if}
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
{#if showCommentForm}
  <div class="theme-bg-card mt-4 rounded-lg p-4 shadow-sm">
    <TextareaForm
      placeholder="この回答についてコメントを書く..."
      submitLabel="コメント送信"
      onSubmit={handleCommentSubmit}
      onCancel={cancelComment}
    />
  </div>
{/if}

<!-- 追加コンテンツ（アクションボタンなど） -->
{#if children}
  {@render children()}
{/if}
