<script lang="ts">
  import { useClickOutside } from "$lib/utils/useClickOutside";
  import { fade } from "svelte/transition";
  import { tick } from "svelte";
  import ValidatedInput from "./ValidatedInput.svelte";
  import { ValidationRules } from "$lib/utils/validation";
  import type { ValidationRule } from "$lib/utils/validation";
  import type { Snippet } from "svelte";

  type Props = {
    isOwner: boolean;
    value: string;
    onSave: (newValue: string) => boolean | void;
    onCancel?: () => void;
    children: Snippet;
    as?: "div" | "span";
    inputType?: "input" | "textarea";
    startInEditMode?: boolean;
    validationType?:
      | "profileLabel"
      | "profileValue"
      | "qaAnswer"
      | "displayName"
      | "bio"
      | "selfIntroduction";
  };

  const {
    isOwner,
    value,
    onSave,
    onCancel,
    children,
    as: Element = "div",
    inputType = "textarea",
    startInEditMode = false,
    validationType = "profileValue"
  }: Props = $props();

  let isEditing = $state(startInEditMode);
  let tempValue = $state(value);
  let isValid = $state(true);

  let containerElement: HTMLElement | null = $state(null);
  let inputElement: HTMLInputElement | HTMLTextAreaElement | null = $state(null);

  // バリデーションルールを取得
  const validationRule: ValidationRule = ValidationRules[validationType];

  async function startEdit() {
    if (!isOwner || isEditing) return;

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

  function confirmEdit() {
    if (!isEditing || !isValid) return;

    const result = onSave(tempValue);
    if (result !== false) {
      isEditing = false;
    }
  }

  function handleValidationChange(value: string, valid: boolean) {
    tempValue = value;
    isValid = valid;
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
      const cleanupClickOutside = useClickOutside(containerElement, [], confirmEdit);

      return () => {
        window.removeEventListener("keydown", handleKeydown);
        cleanupClickOutside();
      };
    }
  });
</script>

{#if isOwner && isEditing}
  <svelte:element
    this={Element}
    bind:this={containerElement}
    class="flex flex-col gap-2"
    transition:fade={{ duration: 150 }}
  >
    <ValidatedInput
      value={tempValue}
      rules={validationRule}
      type={inputType}
      onInput={handleValidationChange}
      class="w-full border-0 border-b-2 border-gray-200 bg-transparent px-1 py-1 text-base font-semibold text-gray-700 transition-colors focus:border-orange-500 focus:ring-0 focus:outline-none sm:text-lg"
    />

    <!-- キーボードショートカットヒント -->
    <div class="mt-1 text-xs text-gray-500">Ctrl+Enter で保存、Esc でキャンセル</div>

    <!-- アクションボタン -->
    <div class="mt-2 flex justify-end gap-1 sm:gap-2">
      <button
        onclick={(e) => {
          e.stopPropagation();
          cancelEdit();
        }}
        class="touch-manipulation rounded-full p-1.5 text-gray-500 transition-colors hover:bg-gray-100 sm:p-2"
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
          : 'cursor-not-allowed text-gray-300'}"
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
    role={isOwner ? "button" : "region"}
    tabindex={isOwner ? 0 : -1}
    onclick={startEdit}
    onkeydown={(e: KeyboardEvent) => {
      if (isOwner && (e.key === "Enter" || e.key === " ")) {
        e.preventDefault();
        startEdit();
      }
    }}
    class="relative transition-all duration-300"
    class:cursor-pointer={isOwner}
  >
    {@render children()}
  </svelte:element>
{/if}
