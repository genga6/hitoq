<script lang="ts">
  import { validateInput, type ValidationRule } from '$lib/utils/validation';
  import type { Snippet } from 'svelte';

  type Props = {
    value: string;
    rules: ValidationRule;
    placeholder?: string;
    disabled?: boolean;
    type?: 'input' | 'textarea';
    label?: string;
    onInput?: (value: string, isValid: boolean) => void;
    children?: Snippet;
    class?: string;
  };

  const {
    value = '',
    rules,
    placeholder = '',
    disabled = false,
    type = 'input',
    label,
    onInput,
    children,
    class: className = ''
  }: Props = $props();

  let touched = $state(false);
  
  const inputId = Math.random().toString(36).substr(2, 9);

  // 入力値を管理する$derived（writable）
  let inputValue = $derived.by(() => value);

  // 入力時のバリデーション
  function handleInput(event: Event) {
    const target = event.target as HTMLInputElement | HTMLTextAreaElement;
    inputValue = target.value;
    
    if (touched) {
      const result = validateInput(inputValue, rules);
      onInput?.(inputValue, result.isValid);
    }
  }

  // フォーカスアウト時のバリデーション
  function handleBlur() {
    touched = true;
    const result = validateInput(inputValue, rules);
    onInput?.(inputValue, result.isValid);
  }

  // エラー情報
  const errors = $derived(() => {
    if (!touched) return [];
    return validateInput(inputValue, rules).errors;
  });

  const hasErrors = $derived(errors.length > 0 && touched);
  const isValid = $derived(!hasErrors && touched);
</script>

<div class={`space-y-1 ${className}`}>
  {#if label}
    <label for="validated-input-{inputId}" class="block text-sm font-medium text-gray-700">
      {label}
      {#if rules.required}
        <span class="text-red-500">*</span>
      {/if}
    </label>
  {/if}

  {#if type === 'textarea'}
    <textarea
      id="validated-input-{inputId}"
      bind:value={inputValue}
      {placeholder}
      {disabled}
      oninput={handleInput}
      onblur={handleBlur}
      class="input-primary {hasErrors ? 'border-red-300 focus:border-red-500 focus:ring-red-500' : ''} {isValid ? 'border-green-300 focus:border-green-500 focus:ring-green-500' : ''}"
      rows="3"
    ></textarea>
  {:else}
    <input
      id="validated-input-{inputId}"
      type="text"
      bind:value={inputValue}
      {placeholder}
      {disabled}
      oninput={handleInput}
      onblur={handleBlur}
      class="input-primary {hasErrors ? 'border-red-300 focus:border-red-500 focus:ring-red-500' : ''} {isValid ? 'border-green-300 focus:border-green-500 focus:ring-green-500' : ''}"
    />
  {/if}

  <!-- 文字数カウンター -->
  {#if rules.maxLength}
    <div class="flex justify-between text-xs">
      <span></span>
      <span class="text-gray-500 {inputValue.length > rules.maxLength ? 'text-red-500' : ''}">
        {inputValue.length}/{rules.maxLength}
      </span>
    </div>
  {/if}

  <!-- エラーメッセージ -->
  {#if hasErrors}
    <div class="space-y-1">
      {#each errors as error, index (index)}
        <p class="text-sm text-red-600">{error}</p>
      {/each}
    </div>
  {/if}

  <!-- 成功メッセージ -->
  {#if isValid && rules.required}
    <p class="text-sm text-green-600">✓ 入力完了</p>
  {/if}

  {#if children}
    {@render children()}
  {/if}
</div>