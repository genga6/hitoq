<script lang="ts">
  import { useClickOutside } from "$lib/utils/useClickOutside";
  import { fade } from "svelte/transition";
  import { tick } from "svelte";
  import { validateInput, ValidationRules } from "$lib/utils/validation";
  import type { ValidationRule } from "$lib/utils/validation";
  import type { Snippet } from "svelte";

  type Props = {
    value: string;
    onSave: (newValue: string) => boolean | void | Promise<boolean>;
    onCancel?: () => void;
    children: Snippet;
    as?: "div" | "span";
    inputType?: "input" | "textarea";
    startInEditMode?: boolean;
    placeholder?: string;
    validationType?:
      | "profileLabel"
      | "profileValue"
      | "qaAnswer"
      | "displayName"
      | "bio"
      | "selfIntroduction";
  };

  const {
    value,
    onSave,
    onCancel,
    children,
    as: Element = "div",
    inputType = "textarea",
    startInEditMode = false,
    placeholder,
    validationType = "profileValue"
  }: Props = $props();

  let isEditing = $state(startInEditMode);
  let tempValue = $state(value);
  let isValid = $state(true);
  let touched = $state(false);

  let containerElement: HTMLElement | null = $state(null);
  let inputElement: HTMLInputElement | HTMLTextAreaElement | null = $state(null);

  // バリデーションルールを取得
  const validationRule: ValidationRule = ValidationRules[validationType];

  // バリデーション結果
  const errors = $derived(() => {
    if (!touched) return [];
    return validateInput(tempValue, validationRule).errors;
  });

  const hasErrors = $derived(errors().length > 0 && touched);

  async function startEdit() {
    if (isEditing) return;

    tempValue = value;
    isEditing = true;

    await tick();
    if (inputElement) {
      inputElement.focus();
      if (inputElement instanceof HTMLTextAreaElement) {
        adjustTextareaHeight(inputElement);
      }
    }
  }

  async function confirmEdit() {
    if (!isEditing || !isValid) return;

    // Optimistic UI update - immediately exit edit mode
    const previousValue = value;
    const newValue = tempValue;
    isEditing = false;

    try {
      const result = onSave(newValue);

      // Handle both sync and async results
      if (result instanceof Promise) {
        const asyncResult = await result;
        if (asyncResult === false) {
          // Revert on failure
          tempValue = previousValue;
          isEditing = true;
        }
      } else if (result === false) {
        // Revert on failure
        tempValue = previousValue;
        isEditing = true;
      }
    } catch (error) {
      // Revert on error
      tempValue = previousValue;
      isEditing = true;
      console.error('Save failed:', error);
    }
  }

  function handleInput(event: Event) {
    const target = event.target as HTMLInputElement | HTMLTextAreaElement;
    tempValue = target.value;

    if (touched) {
      const result = validateInput(tempValue, validationRule);
      isValid = result.isValid;
    }
  }

  function handleBlur() {
    touched = true;
    const result = validateInput(tempValue, validationRule);
    isValid = result.isValid;
  }

  function cancelEdit() {
    if (onCancel) {
      onCancel();
    }
    isEditing = false;
  }

  function adjustTextareaHeight(textarea: HTMLTextAreaElement) {
    textarea.style.height = "auto";
    textarea.style.height = `${textarea.scrollHeight}px`;
  }

  $effect(() => {
    const handleKeydown = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        cancelEdit();
      } else if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) {
        e.preventDefault();
        confirmEdit();
      }
    };

    if (isEditing) {
      window.addEventListener("keydown", handleKeydown);
    }

    if (isEditing && containerElement) {
      const handleClickOutside = () => {
        confirmEdit();
      };
      
      const cleanupClickOutside = useClickOutside(containerElement, [], handleClickOutside);

      return () => {
        window.removeEventListener("keydown", handleKeydown);
        cleanupClickOutside();
      };
    }
  });
</script>

{#if isEditing}
  <svelte:element
    this={Element}
    bind:this={containerElement}
    class="flex flex-col gap-2"
    transition:fade={{ duration: 150 }}
  >
    {#if inputType === "textarea"}
      <textarea
        bind:this={inputElement}
        bind:value={tempValue}
        {placeholder}
        oninput={handleInput}
        onblur={handleBlur}
        class="theme-border theme-text-primary w-full resize-none border-0 border-b-2 bg-transparent px-1 py-1 text-base font-semibold transition-colors focus:border-orange-500 focus:ring-0 focus:outline-none sm:text-lg {hasErrors
          ? 'border-red-500 focus:border-red-500'
          : ''}"
        rows="3"
      ></textarea>
    {:else}
      <input
        bind:this={inputElement}
        type="text"
        bind:value={tempValue}
        {placeholder}
        oninput={handleInput}
        onblur={handleBlur}
        class="theme-border theme-text-primary w-full border-0 border-b-2 bg-transparent px-1 py-1 text-base font-semibold transition-colors focus:border-orange-500 focus:ring-0 focus:outline-none sm:text-lg {hasErrors
          ? 'border-red-500 focus:border-red-500'
          : ''}"
      />
    {/if}

    <!-- 文字数カウンター -->
    {#if validationRule.maxLength}
      <div class="flex justify-end">
        <span
          class="text-xs {tempValue.length > validationRule.maxLength
            ? 'text-red-500'
            : 'theme-text-muted'}"
        >
          {tempValue.length}/{validationRule.maxLength}
        </span>
      </div>
    {/if}

    <!-- エラーメッセージ -->
    {#if hasErrors}
      <div class="space-y-1">
        {#each errors() as error, index (index)}
          <p class="text-sm text-red-500">{error}</p>
        {/each}
      </div>
    {/if}

    <!-- キーボードショートカットヒント（デスクトップのみ） -->
    <div class="theme-text-muted mt-1 text-xs hidden sm:block">Ctrl+Enter で保存、Esc でキャンセル</div>

    <!-- アクションボタン -->
    <div class="mt-2 flex justify-end gap-1 sm:gap-2">
      <button
        onclick={(e) => {
          e.stopPropagation();
          cancelEdit();
        }}
        class="theme-text-muted theme-bg-hover touch-manipulation rounded-full p-1.5 transition-colors sm:p-2"
        aria-label="Cancel"
      >
        <!-- Cancel Icon (X) -->
        <svg
          xmlns="http://www.w3.org/2000/svg"
          class="h-4 w-4 sm:h-5 sm:w-5"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          stroke-width="2"
          ><path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" /></svg
        >
      </button>
      <button
        onclick={(e) => {
          e.stopPropagation();
          confirmEdit();
        }}
        disabled={!isValid}
        class="touch-manipulation rounded-full p-1.5 transition-colors sm:p-2 {isValid
          ? 'text-green-500 hover:bg-green-50'
          : 'theme-text-muted cursor-not-allowed opacity-50'}"
        aria-label="Confirm"
      >
        <!-- Confirm Icon (Check) -->
        <svg
          xmlns="http://www.w3.org/2000/svg"
          class="h-4 w-4 sm:h-5 sm:w-5"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          stroke-width="2"
          ><path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" /></svg
        >
      </button>
    </div>
  </svelte:element>
{:else}
  <svelte:element
    this={Element}
    role="button"
    tabindex="0"
    onclick={startEdit}
    onkeydown={(e: KeyboardEvent) => {
      if (e.key === "Enter" || e.key === " ") {
        e.preventDefault();
        startEdit();
      }
    }}
    class="relative transition-all duration-300 cursor-pointer"
  >
    {@render children()}
  </svelte:element>
{/if}
