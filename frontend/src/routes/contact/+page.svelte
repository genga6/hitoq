<script lang="ts">
  import ValidatedInput from "$lib/components/form/ValidatedInput.svelte";
  import { ValidationRules, sanitizeInput } from "$lib/utils/validation";

  let selectedCategory = $state("bug");
  let isSubmitting = $state(false);
  let showSuccess = $state(false);
  let titleValue = $state("");
  let descriptionValue = $state("");
  let environmentValue = $state("");
  let contactValue = $state("");

  let titleValid = $state(false);
  let descriptionValid = $state(false);
  let environmentValid = $state(true); // Optional field
  let contactValid = $state(true); // Optional field

  const formValid = $derived(titleValid && descriptionValid && environmentValid && contactValid);

  const GOOGLE_FORM_IDS = {
    FORM_ID: "1FAIpQLSdlW6SxDm9gCWqdgadFXEt46fKkTWg2raYPqgXSVpMUku903Q",
    CATEGORY: "entry.1342089124",
    TITLE: "entry.1055742737",
    DESCRIPTION: "entry.274276593",
    ENVIRONMENT: "entry.133493195",
    CONTACT: "entry.1837922336"
  };

  const GOOGLE_FORMS_URL = `https://docs.google.com/forms/d/e/${GOOGLE_FORM_IDS.FORM_ID}/formResponse`;

  const categories = [
    { value: "bug", label: "バグ報告", description: "サービスの不具合やエラーについて" },
    { value: "feature", label: "機能要望", description: "新しい機能や改善の提案" },
    { value: "feedback", label: "フィードバック", description: "サービスに対する感想や意見" },
    { value: "other", label: "その他", description: "上記以外のお問い合わせ" }
  ];

  function handleSubmit(event: Event) {
    event.preventDefault();
    if (!formValid) return;

    isSubmitting = true;

    const formData = new FormData();
    formData.append(GOOGLE_FORM_IDS.CATEGORY, selectedCategory);
    formData.append(GOOGLE_FORM_IDS.TITLE, sanitizeInput(titleValue));
    formData.append(GOOGLE_FORM_IDS.DESCRIPTION, sanitizeInput(descriptionValue));
    formData.append(GOOGLE_FORM_IDS.ENVIRONMENT, sanitizeInput(environmentValue));
    formData.append(GOOGLE_FORM_IDS.CONTACT, sanitizeInput(contactValue));

    // Google Formsに送信
    fetch(GOOGLE_FORMS_URL, {
      method: "POST",
      body: formData,
      mode: "no-cors"
    })
      .then(() => {
        showSuccess = true;
        // Reset form values
        titleValue = "";
        descriptionValue = "";
        environmentValue = "";
        contactValue = "";
        selectedCategory = "bug";
      })
      .catch((error) => {
        console.error("送信エラー:", error);
        alert("送信に失敗しました。しばらく時間をおいて再度お試しください。");
      })
      .finally(() => {
        isSubmitting = false;
      });
  }
</script>

<svelte:head>
  <title>お問い合わせ - hitoQ</title>
  <meta
    name="description"
    content="hitoQへのお問い合わせ、バグ報告、フィードバックはこちらから。"
  />
</svelte:head>

<main class="min-h-screen py-6 md:py-12">
  <div class="container-responsive max-w-2xl">
    <div class="theme-page-container p-4 md:p-8">
      <h1 class="text-responsive-xl theme-text-primary mb-4 font-bold">お問い合わせ</h1>
      <p class="theme-text-primary mb-6 text-sm md:mb-8 md:text-base">
        hitoQに関するバグ報告、機能要望、フィードバックなど、お気軽にお寄せください。
        いただいたご意見は、サービス改善の参考にさせていただきます。
      </p>

      {#if showSuccess}
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
          <button onclick={() => (showSuccess = false)} class="theme-alert-button">
            新しいお問い合わせを送信
          </button>
        </div>
      {:else}
        <form onsubmit={handleSubmit} class="space-y-6">
          <!-- カテゴリー選択 -->
          <div>
            <!-- svelte-ignore a11y_label_has_associated_control -->
            <label class="theme-text-secondary mb-3 block text-sm font-medium">
              お問い合わせ種別 <span class="text-red-500">*</span>
            </label>
            <div class="grid grid-cols-1 gap-3 sm:grid-cols-2">
              {#each categories as category (category.value)}
                <label class="relative cursor-pointer">
                  <input
                    type="radio"
                    name={GOOGLE_FORM_IDS.CATEGORY}
                    value={category.value}
                    bind:group={selectedCategory}
                    class="sr-only"
                    required
                  />
                  <div
                    class="rounded-lg border-2 p-4 transition-all {selectedCategory ===
                    category.value
                      ? 'border-orange-400 bg-orange-50 dark:border-orange-500 dark:bg-orange-900/50'
                      : 'theme-border-light theme-hover-bg'}"
                  >
                    <div class="flex items-start">
                      <div class="mt-1 flex-shrink-0">
                        <div
                          class="h-4 w-4 rounded-full border-2 {selectedCategory === category.value
                            ? 'border-orange-400 bg-orange-400 dark:border-orange-500 dark:bg-orange-500'
                            : 'theme-border-light'}"
                        >
                          {#if selectedCategory === category.value}
                            <div class="mx-auto mt-0.5 h-2 w-2 rounded-full bg-white"></div>
                          {/if}
                        </div>
                      </div>
                      <div class="ml-3">
                        <div class="theme-text-primary font-medium">{category.label}</div>
                        <div class="theme-text-subtle text-sm">{category.description}</div>
                      </div>
                    </div>
                  </div>
                </label>
              {/each}
            </div>
          </div>

          <!-- タイトル -->
          <ValidatedInput
            value={titleValue}
            rules={ValidationRules.contactTitle}
            label="タイトル"
            placeholder="例：ログインができません"
            onInput={(value, isValid) => {
              titleValue = value;
              titleValid = isValid;
            }}
          />

          <!-- 詳細内容 -->
          <ValidatedInput
            value={descriptionValue}
            rules={ValidationRules.contactDescription}
            label="詳細内容"
            type="textarea"
            placeholder="具体的な状況や手順、エラーメッセージなどを詳しく記載してください"
            onInput={(value, isValid) => {
              descriptionValue = value;
              descriptionValid = isValid;
            }}
          />

          <!-- 環境情報（バグ報告の場合のみ表示） -->
          {#if selectedCategory === "bug"}
            <div>
              <ValidatedInput
                value={environmentValue}
                rules={{ required: false, maxLength: 500 }}
                label="環境情報"
                type="textarea"
                placeholder="例：Chrome 120, Windows 11, iPhone Safari など"
                onInput={(value, isValid) => {
                  environmentValue = value;
                  environmentValid = isValid;
                }}
              />
              <p class="theme-text-subtle mt-1 text-sm">
                ブラウザ、OS、デバイス情報などをご記載いただけると問題解決に役立ちます。
              </p>
            </div>
          {/if}

          <!-- 連絡先（任意） -->
          <div>
            <ValidatedInput
              value={contactValue}
              rules={ValidationRules.contactEmail}
              label="連絡先（任意）"
              placeholder="返信が必要な場合はメールアドレスをご記載ください"
              onInput={(value, isValid) => {
                contactValue = value;
                contactValid = isValid;
              }}
            />
            <p class="theme-text-subtle mt-1 text-sm">
              回答が必要な場合のみご記載ください。お答えできない場合もございます。
            </p>
          </div>

          <!-- 送信ボタン -->
          <div class="flex justify-center pt-4">
            <button
              type="submit"
              disabled={isSubmitting || !formValid}
              class="btn-primary px-8 py-3 {!formValid ? 'cursor-not-allowed opacity-50' : ''}"
            >
              {#if isSubmitting}
                <span class="flex items-center justify-center">
                  <svg
                    class="mr-3 -ml-1 h-5 w-5 animate-spin text-white"
                    xmlns="http://www.w3.org/2000/svg"
                    fill="none"
                    viewBox="0 0 24 24"
                  >
                    <circle
                      class="opacity-25"
                      cx="12"
                      cy="12"
                      r="10"
                      stroke="currentColor"
                      stroke-width="4"
                    ></circle>
                    <path
                      class="opacity-75"
                      fill="currentColor"
                      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                    ></path>
                  </svg>
                  送信中...
                </span>
              {:else}
                送信する
              {/if}
            </button>
          </div>
        </form>

        <div class="theme-bg-elevated mt-8 rounded-lg p-4">
          <h3 class="theme-text-primary mb-2 font-semibold">📝 お問い合わせについて</h3>
          <ul class="theme-text-secondary space-y-1 text-sm">
            <li>• 技術的な質問やバグ報告は詳細な情報をご提供ください</li>
            <li>• 回答をお約束するものではありませんが、サービス改善の参考にいたします</li>
            <li>• 緊急性の高い問題については、可能な限り迅速に対応いたします</li>
          </ul>
        </div>
      {/if}
    </div>
  </div>
</main>
