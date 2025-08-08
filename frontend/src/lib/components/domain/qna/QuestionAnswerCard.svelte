<script lang="ts">
  import type { CategoryInfo } from "$lib/types";
  import Card from "../../ui/Card.svelte";

  const {
    question,
    answer = "",
    categoryInfo,
    mode = "display", // "display" | "edit" | "input"
    isOwner = false,
    placeholder = "回答を入力...",
    onAnswerChange,
    primaryAction,
    secondaryAction,
    children
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
  }>();

  let localAnswer = $state(answer);

  function handleAnswerInput(event: Event) {
    const target = event.target as HTMLTextAreaElement;
    localAnswer = target.value;
    onAnswerChange?.(target.value);
  }
</script>

<Card variant="default" padding="md" class="group relative">
  <!-- 質問エリア -->
  <div class="mb-2 {mode === 'display' && !isOwner ? 'pr-20 sm:pr-16' : ''}">
    <p class="theme-text-muted mb-2 text-sm font-medium break-words sm:text-base">
      {question}
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
  {:else if mode === "edit"}
    <textarea
      value={localAnswer}
      oninput={handleAnswerInput}
      {placeholder}
      class="theme-border theme-bg-surface theme-text-primary mb-3 w-full rounded-lg p-3 text-sm focus:border-orange-500 focus:ring-1 focus:ring-orange-500 focus:outline-none"
      rows="3"
    ></textarea>
  {:else if mode === "input"}
    <textarea
      value={localAnswer}
      oninput={handleAnswerInput}
      {placeholder}
      class="theme-border theme-bg-surface theme-text-primary mb-3 w-full rounded-lg p-3 text-sm focus:border-orange-400 focus:outline-none"
      rows="3"
    ></textarea>
  {/if}

  <!-- アクションボタン -->
  {#if (mode === "edit" || mode === "input") && (primaryAction || secondaryAction)}
    <div class="mt-3 flex items-center justify-end gap-3">
      {#if secondaryAction}
        <button
          onclick={secondaryAction.onClick}
          class="theme-text-muted px-4 py-2 text-sm hover:opacity-80"
        >
          {secondaryAction.label}
        </button>
      {/if}
      {#if primaryAction}
        <button
          onclick={primaryAction.onClick}
          disabled={primaryAction.disabled}
          class="rounded-lg bg-orange-500 px-4 py-2 text-sm text-white hover:bg-orange-600 disabled:opacity-50"
        >
          {primaryAction.label}
        </button>
      {/if}
    </div>
  {/if}
</Card>

<!-- 追加コンテンツ（アクションボタンなど） -->
{#if children}
  {@render children()}
{/if}
