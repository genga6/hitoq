<script lang="ts">
  let selectedCategory = $state('bug');
  let isSubmitting = $state(false);
  let showSuccess = $state(false);

  const GOOGLE_FORM_IDS = {
    FORM_ID: '1FAIpQLSdlW6SxDm9gCWqdgadFXEt46fKkTWg2raYPqgXSVpMUku903Q',
    CATEGORY: 'entry.1342089124',
    TITLE: 'entry.1055742737',
    DESCRIPTION: 'entry.274276593',
    ENVIRONMENT: 'entry.133493195',
    CONTACT: 'entry.1837922336'
  };

  const GOOGLE_FORMS_URL = `https://docs.google.com/forms/d/e/${GOOGLE_FORM_IDS.FORM_ID}/formResponse`;

  const categories = [
    { value: 'bug', label: 'バグ報告', description: 'サービスの不具合やエラーについて' },
    { value: 'feature', label: '機能要望', description: '新しい機能や改善の提案' },
    { value: 'feedback', label: 'フィードバック', description: 'サービスに対する感想や意見' },
    { value: 'other', label: 'その他', description: '上記以外のお問い合わせ' }
  ];

  function handleSubmit(event: Event) {
    event.preventDefault();
    isSubmitting = true;

    const form = event.target as HTMLFormElement;
    const formData = new FormData(form);

    // Google Formsに送信
    fetch(GOOGLE_FORMS_URL, {
      method: 'POST',
      body: formData,
      mode: 'no-cors'
    })
      .then(() => {
        showSuccess = true;
        form.reset();
        selectedCategory = 'bug';
      })
      .catch((error) => {
        console.error('送信エラー:', error);
        alert('送信に失敗しました。しばらく時間をおいて再度お試しください。');
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

<main class="min-h-screen bg-gray-50 py-12">
  <div class="mx-auto max-w-2xl px-4">
    <div class="rounded-lg bg-white p-8 shadow-sm">
      <h1 class="mb-4 text-3xl font-bold text-gray-800">お問い合わせ</h1>
      <p class="mb-8 text-gray-600">
        hitoQに関するバグ報告、機能要望、フィードバックなど、お気軽にお寄せください。
        いただいたご意見は、サービス改善の参考にさせていただきます。
      </p>

      {#if showSuccess}
        <div class="mb-8 rounded-lg border border-green-200 bg-green-50 p-6">
          <div class="flex items-center">
            <svg
              class="mr-3 h-6 w-6 text-green-600"
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
            <h3 class="text-lg font-semibold text-green-800">送信完了</h3>
          </div>
          <p class="mt-2 text-green-700">
            お問い合わせありがとうございます。内容を確認の上、必要に応じてご連絡いたします。
          </p>
          <button
            onclick={() => (showSuccess = false)}
            class="mt-4 text-sm text-green-600 underline hover:text-green-800"
          >
            新しいお問い合わせを送信
          </button>
        </div>
      {:else}
        <form onsubmit={handleSubmit} class="space-y-6">
          <!-- カテゴリー選択 -->
          <div>
            <label class="mb-3 block text-sm font-medium text-gray-700">
              お問い合わせ種別 <span class="text-red-500">*</span>
            </label>
            <div class="grid grid-cols-1 gap-3 md:grid-cols-2">
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
                      ? 'border-orange-400 bg-orange-50'
                      : 'border-gray-200 hover:border-gray-300'}"
                  >
                    <div class="flex items-start">
                      <div class="mt-1 flex-shrink-0">
                        <div
                          class="h-4 w-4 rounded-full border-2 {selectedCategory === category.value
                            ? 'border-orange-400 bg-orange-400'
                            : 'border-gray-300'}"
                        >
                          {#if selectedCategory === category.value}
                            <div class="mx-auto mt-0.5 h-2 w-2 rounded-full bg-white"></div>
                          {/if}
                        </div>
                      </div>
                      <div class="ml-3">
                        <div class="font-medium text-gray-900">{category.label}</div>
                        <div class="text-sm text-gray-500">{category.description}</div>
                      </div>
                    </div>
                  </div>
                </label>
              {/each}
            </div>
          </div>

          <!-- タイトル -->
          <div>
            <label for="title" class="mb-2 block text-sm font-medium text-gray-700">
              タイトル <span class="text-red-500">*</span>
            </label>
            <input
              type="text"
              id="title"
              name={GOOGLE_FORM_IDS.TITLE}
              required
              class="w-full rounded-md border border-gray-300 px-3 py-2 focus:border-transparent focus:ring-2 focus:ring-orange-400 focus:outline-none"
              placeholder="例：ログインができません"
            />
          </div>

          <!-- 詳細内容 -->
          <div>
            <label for="description" class="mb-2 block text-sm font-medium text-gray-700">
              詳細内容 <span class="text-red-500">*</span>
            </label>
            <textarea
              id="description"
              name={GOOGLE_FORM_IDS.DESCRIPTION}
              rows="6"
              required
              class="w-full rounded-md border border-gray-300 px-3 py-2 focus:border-transparent focus:ring-2 focus:ring-orange-400 focus:outline-none"
              placeholder="具体的な状況や手順、エラーメッセージなどを詳しく記載してください"
            ></textarea>
          </div>

          <!-- 環境情報（バグ報告の場合のみ表示） -->
          {#if selectedCategory === 'bug'}
            <div>
              <label for="environment" class="mb-2 block text-sm font-medium text-gray-700">
                環境情報
              </label>
              <textarea
                id="environment"
                name={GOOGLE_FORM_IDS.ENVIRONMENT}
                rows="3"
                class="w-full rounded-md border border-gray-300 px-3 py-2 focus:border-transparent focus:ring-2 focus:ring-orange-400 focus:outline-none"
                placeholder="例：Chrome 120, Windows 11, iPhone Safari など"
              ></textarea>
              <p class="mt-1 text-sm text-gray-500">
                ブラウザ、OS、デバイス情報などをご記載いただけると問題解決に役立ちます。
              </p>
            </div>
          {/if}

          <!-- 連絡先（任意） -->
          <div>
            <label for="contact" class="mb-2 block text-sm font-medium text-gray-700">
              連絡先（任意）
            </label>
            <input
              type="email"
              id="contact"
              name={GOOGLE_FORM_IDS.CONTACT}
              class="w-full rounded-md border border-gray-300 px-3 py-2 focus:border-transparent focus:ring-2 focus:ring-orange-400 focus:outline-none"
              placeholder="返信が必要な場合はメールアドレスをご記載ください"
            />
            <p class="mt-1 text-sm text-gray-500">
              回答が必要な場合のみご記載ください。お答えできない場合もございます。
            </p>
          </div>

          <!-- 送信ボタン -->
          <div class="pt-4">
            <button
              type="submit"
              disabled={isSubmitting}
              class="w-full rounded-md bg-orange-400 px-4 py-3 font-semibold text-white transition duration-200 hover:bg-orange-500 active:bg-orange-600 disabled:cursor-not-allowed disabled:bg-gray-300"
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

        <div class="mt-8 rounded-lg bg-blue-50 p-4">
          <h3 class="mb-2 font-semibold text-blue-800">📝 お問い合わせについて</h3>
          <ul class="space-y-1 text-sm text-blue-700">
            <li>• 技術的な質問やバグ報告は詳細な情報をご提供ください</li>
            <li>• 回答をお約束するものではありませんが、サービス改善の参考にいたします</li>
            <li>• 緊急性の高い問題については、可能な限り迅速に対応いたします</li>
          </ul>
        </div>
      {/if}
    </div>
  </div>
</main>
