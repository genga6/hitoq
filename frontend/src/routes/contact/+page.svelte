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
    }).then(() => {
      showSuccess = true;
      form.reset();
      selectedCategory = 'bug';
    }).catch((error) => {
      console.error('送信エラー:', error);
      alert('送信に失敗しました。しばらく時間をおいて再度お試しください。');
    }).finally(() => {
      isSubmitting = false;
    });
  }
</script>

<svelte:head>
  <title>お問い合わせ - hitoQ</title>
  <meta name="description" content="hitoQへのお問い合わせ、バグ報告、フィードバックはこちらから。" />
</svelte:head>

<main class="min-h-screen bg-gray-50 py-12">
  <div class="max-w-2xl mx-auto px-4">
    <div class="bg-white rounded-lg shadow-sm p-8">
      <h1 class="text-3xl font-bold text-gray-800 mb-4">お問い合わせ</h1>
      <p class="text-gray-600 mb-8">
        hitoQに関するバグ報告、機能要望、フィードバックなど、お気軽にお寄せください。
        いただいたご意見は、サービス改善の参考にさせていただきます。
      </p>

      {#if showSuccess}
        <div class="bg-green-50 border border-green-200 rounded-lg p-6 mb-8">
          <div class="flex items-center">
            <svg class="w-6 h-6 text-green-600 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
            </svg>
            <h3 class="text-lg font-semibold text-green-800">送信完了</h3>
          </div>
          <p class="text-green-700 mt-2">
            お問い合わせありがとうございます。内容を確認の上、必要に応じてご連絡いたします。
          </p>
          <button 
            onclick={() => showSuccess = false}
            class="mt-4 text-sm text-green-600 hover:text-green-800 underline"
          >
            新しいお問い合わせを送信
          </button>
        </div>
      {:else}
        <form onsubmit={handleSubmit} class="space-y-6">
          <!-- カテゴリー選択 -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-3">
              お問い合わせ種別 <span class="text-red-500">*</span>
            </label>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
              {#each categories as category}
                <label class="relative cursor-pointer">
                  <input
                    type="radio"
                    name="entry.CATEGORY_FIELD_ID"
                    value={category.value}
                    bind:group={selectedCategory}
                    class="sr-only"
                    required
                  />
                  <div class="border-2 rounded-lg p-4 transition-all {selectedCategory === category.value ? 'border-orange-400 bg-orange-50' : 'border-gray-200 hover:border-gray-300'}">
                    <div class="flex items-start">
                      <div class="flex-shrink-0 mt-1">
                        <div class="w-4 h-4 rounded-full border-2 {selectedCategory === category.value ? 'border-orange-400 bg-orange-400' : 'border-gray-300'}">
                          {#if selectedCategory === category.value}
                            <div class="w-2 h-2 bg-white rounded-full mx-auto mt-0.5"></div>
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
            <label for="title" class="block text-sm font-medium text-gray-700 mb-2">
              タイトル <span class="text-red-500">*</span>
            </label>
            <input
              type="text"
              id="title"
              name="entry.TITLE_FIELD_ID"
              required
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-orange-400 focus:border-transparent"
              placeholder="例：ログインができません"
            />
          </div>

          <!-- 詳細内容 -->
          <div>
            <label for="description" class="block text-sm font-medium text-gray-700 mb-2">
              詳細内容 <span class="text-red-500">*</span>
            </label>
            <textarea
              id="description"
              name="entry.DESCRIPTION_FIELD_ID"
              rows="6"
              required
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-orange-400 focus:border-transparent"
              placeholder="具体的な状況や手順、エラーメッセージなどを詳しく記載してください"
            ></textarea>
          </div>

          <!-- 環境情報（バグ報告の場合のみ表示） -->
          {#if selectedCategory === 'bug'}
            <div>
              <label for="environment" class="block text-sm font-medium text-gray-700 mb-2">
                環境情報
              </label>
              <textarea
                id="environment"
                name="entry.ENVIRONMENT_FIELD_ID"
                rows="3"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-orange-400 focus:border-transparent"
                placeholder="例：Chrome 120, Windows 11, iPhone Safari など"
              ></textarea>
              <p class="text-sm text-gray-500 mt-1">
                ブラウザ、OS、デバイス情報などをご記載いただけると問題解決に役立ちます。
              </p>
            </div>
          {/if}

          <!-- 連絡先（任意） -->
          <div>
            <label for="contact" class="block text-sm font-medium text-gray-700 mb-2">
              連絡先（任意）
            </label>
            <input
              type="email"
              id="contact"
              name="entry.CONTACT_FIELD_ID"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-orange-400 focus:border-transparent"
              placeholder="返信が必要な場合はメールアドレスをご記載ください"
            />
            <p class="text-sm text-gray-500 mt-1">
              回答が必要な場合のみご記載ください。お答えできない場合もございます。
            </p>
          </div>

          <!-- 送信ボタン -->
          <div class="pt-4">
            <button
              type="submit"
              disabled={isSubmitting}
              class="w-full bg-orange-400 text-white py-3 px-4 rounded-md font-semibold hover:bg-orange-500 active:bg-orange-600 disabled:bg-gray-300 disabled:cursor-not-allowed transition duration-200"
            >
              {#if isSubmitting}
                <span class="flex items-center justify-center">
                  <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  送信中...
                </span>
              {:else}
                送信する
              {/if}
            </button>
          </div>
        </form>

        <div class="mt-8 p-4 bg-blue-50 rounded-lg">
          <h3 class="font-semibold text-blue-800 mb-2">📝 お問い合わせについて</h3>
          <ul class="text-sm text-blue-700 space-y-1">
            <li>• 技術的な質問やバグ報告は詳細な情報をご提供ください</li>
            <li>• 回答をお約束するものではありませんが、サービス改善の参考にいたします</li>
            <li>• 緊急性の高い問題については、可能な限り迅速に対応いたします</li>
          </ul>
        </div>
      {/if}
    </div>
  </div>
</main>