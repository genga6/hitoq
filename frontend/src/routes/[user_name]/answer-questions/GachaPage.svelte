<script lang="ts">
  import type { CategoryInfo } from '$lib/types';
  import type { Question } from '$lib/types';
  import CategoryFilter from '$lib/components/CategoryFilter.svelte';

  type Props = {
    categories: Record<string, CategoryInfo>;
    isOwner: boolean;
    userId: string;
  };

  const { categories, isOwner, userId }: Props = $props();

  let gachaQuestionCount = $state(3);
  let selectedCategories = $state<string[]>([]);

  // 各質問の入力値を管理
  let questionInputs = $state<Record<string, string>>({});

  interface UnansweredQAPair {
    groupId: string;
    question: Question;
    questionIndex: number;
    groupIndex: number;
    categoryInfo?: CategoryInfo;
  }

  // ガチャ結果の未回答質問を管理
  let unansweredQAPairs = $state<UnansweredQAPair[]>([]);

  // localStorageのキー
  const STORAGE_KEY = `hitoq-unanswered-questions-${userId}`;
  const STORAGE_KEY_INPUTS = `hitoq-question-inputs-${userId}`;
  const STORAGE_KEY_NEW_QUESTIONS = `hitoq-new-questions-${userId}`;

  interface NewQuestion {
    messageId: string;
    content: string;
    fromUserId: string;
    fromUserName: string;
    fromDisplayName: string;
    createdAt: string;
    groupId: string;
    questionIndex: number;
  }

  // 新規質問（メッセージ）を管理
  let newQuestions = $state<NewQuestion[]>([]);

  function generateGroupId(): string {
    return `group-${Date.now()}-${Math.random().toString(36).slice(2, 11)}`;
  }

  async function performGacha(categoryFilter?: string, count: number = gachaQuestionCount) {
    try {
      let questions;

      if (categoryFilter) {
        const { getQuestionsByCategory } = await import('$lib/api-client/qna');
        questions = await getQuestionsByCategory(categoryFilter);
      } else {
        const { getAllQuestions } = await import('$lib/api-client/qna');
        const allQuestions = await getAllQuestions();
        questions = allQuestions;
      }

      if (questions.length === 0) {
        return 0;
      }

      const shuffled = [...questions].sort(() => Math.random() - 0.5);
      const selectedQuestions = shuffled.slice(0, Math.min(count, shuffled.length));

      // 新しい未回答質問として追加
      const newUnansweredPairs = selectedQuestions.map(
        (question: Question, index: number): UnansweredQAPair => ({
          groupId: generateGroupId(),
          question: {
            questionId: question.questionId,
            text: question.text,
            categoryId: question.categoryId,
            displayOrder: question.displayOrder
          },
          questionIndex: index,
          groupIndex: unansweredQAPairs.length + index,
          categoryInfo: categories[question.categoryId]
        })
      );

      unansweredQAPairs = [...unansweredQAPairs, ...newUnansweredPairs];
      saveToStorage();

      return selectedQuestions.length;
    } catch (error) {
      console.error('ガチャ実行エラー:', error);
      return 0;
    }
  }

  async function performRandomGacha() {
    // カテゴリが選択されている場合はカテゴリフィルターを適用
    if (selectedCategories.length > 0) {
      // 複数カテゴリが選択されている場合はランダムに1つを選択
      const randomCategory = selectedCategories[Math.floor(Math.random() * selectedCategories.length)];
      const count = await performGacha(randomCategory, gachaQuestionCount);
      if (count === 0) {
        const categoryInfo = categories[randomCategory];
        alert(`${categoryInfo?.label || randomCategory}カテゴリにはもう回答できる質問がありません！`);
      }
    } else {
      const count = await performGacha(undefined, gachaQuestionCount);
      if (count === 0) {
        alert('もう回答できる質問がありません！');
      }
    }
  }

  // async function performCategoryGacha(category: string) {
  //   const count = await performGacha(category, gachaQuestionCount);
  //   if (count === 0) {
  //     const categoryInfo = categories[category];
  //     alert(`${categoryInfo?.label || category}カテゴリにはもう回答できる質問がありません！`);
  //   }
  // }

  async function handleSaveAnswer(pair: UnansweredQAPair) {
    const questionKey = `${pair.groupId}-${pair.questionIndex}`;
    const inputValue = questionInputs[questionKey] || '';

    if (!inputValue.trim()) return;

    try {
      const { createAnswer } = await import('$lib/api-client/qna');

      // 質問に対する回答を作成
      await createAnswer(
        userId,
        pair.question.questionId,
        inputValue.trim()
      );

      // 成功したら未回答リストから削除（フェードアウト効果付き）
      const questionElement = document.querySelector(`[data-question-id="${pair.groupId}"]`) as HTMLElement;
      if (questionElement) {
        questionElement.style.transition = 'opacity 0.3s ease-out, transform 0.3s ease-out';
        questionElement.style.opacity = '0';
        questionElement.style.transform = 'translateY(-10px)';
        
        setTimeout(() => {
          unansweredQAPairs = unansweredQAPairs.filter((p) => p.groupId !== pair.groupId);
          questionInputs[questionKey] = '';
          saveToStorage();
        }, 300);
      } else {
        unansweredQAPairs = unansweredQAPairs.filter((p) => p.groupId !== pair.groupId);
        questionInputs[questionKey] = '';
        saveToStorage();
      }
    } catch (error) {
      console.error('回答保存エラー:', error);
      alert('回答の保存に失敗しました。');
    }
  }

  function handleSkip(pair: UnansweredQAPair) {
    // 未回答リストから削除
    unansweredQAPairs = unansweredQAPairs.filter((p) => p.groupId !== pair.groupId);
    // 入力値をクリア
    const questionKey = `${pair.groupId}-${pair.questionIndex}`;
    questionInputs[questionKey] = '';
    saveToStorage();
  }


  // 新規質問を取得
  async function loadNewQuestions() {
    if (!isOwner) return;

    try {
      const { getMyMessages } = await import('$lib/api-client/messages');
      const messages = await getMyMessages();


      // 未回答のメッセージのみを新規質問として表示（いいねメッセージは除外）
      interface APIMessage {
        messageId: string;
        content: string;
        fromUserId: string;
        fromUserName: string;
        fromDisplayName: string;
        createdAt: string;
        isAnswered: boolean;
        messageType: string;
      }
      
      const unansweredMessages = (messages as APIMessage[]).filter((msg: APIMessage) => 
        !msg.isAnswered && msg.messageType !== 'like'
      );
      const newQuestionsFromAPI = unansweredMessages.map(
        (msg): NewQuestion => ({
          messageId: msg.messageId,
          content: msg.content,
          fromUserId: msg.fromUserId,
          fromUserName: msg.fromUserName,
          fromDisplayName: msg.fromDisplayName,
          createdAt: msg.createdAt,
          groupId: generateGroupId(),
          questionIndex: 0
        })
      );

      // 既存のローカル質問と重複しないようにマージ
      const existingMessageIds = new Set(newQuestions.map(q => q.messageId));
      const newUniqueQuestions = newQuestionsFromAPI.filter(q => !existingMessageIds.has(q.messageId));
      
      if (newUniqueQuestions.length > 0) {
        newQuestions = [...newQuestions, ...newUniqueQuestions];
        saveToStorage();
      }
    } catch (error) {
      console.error('新規質問の取得に失敗しました:', error);
    }
  }

  // 新規質問に回答
  async function handleAnswerNewQuestion(question: NewQuestion) {
    const questionKey = `new-${question.groupId}`;
    const inputValue = questionInputs[questionKey] || '';

    if (!inputValue.trim()) return;

    try {
      const { createMessage } = await import('$lib/api-client/messages');

      // メッセージに返信
      await createMessage({
        toUserId: question.fromUserId || '',
        messageType: 'comment',
        content: inputValue.trim(),
        parentMessageId: question.messageId
      });

      // 成功したら新規質問リストから削除
      newQuestions = newQuestions.filter((q) => q.messageId !== question.messageId);
      questionInputs[questionKey] = '';
      saveToStorage();

      // 成功メッセージ
      alert('回答を送信しました！');
    } catch (error) {
      console.error('回答送信エラー:', error);
      alert('回答の送信に失敗しました。');
    }
  }

  function handleSkipNewQuestion(question: NewQuestion) {
    // 新規質問リストから削除
    newQuestions = newQuestions.filter((q) => q.messageId !== question.messageId);
    // 入力値をクリア
    const questionKey = `new-${question.groupId}`;
    questionInputs[questionKey] = '';
    saveToStorage();
  }

  // localStorageから保存されたデータを読み込み
  function loadFromStorage() {
    if (typeof window === 'undefined') return;
    
    try {
      const savedQuestions = localStorage.getItem(STORAGE_KEY);
      const savedInputs = localStorage.getItem(STORAGE_KEY_INPUTS);
      const savedNewQuestions = localStorage.getItem(STORAGE_KEY_NEW_QUESTIONS);
      
      if (savedQuestions) {
        const parsed = JSON.parse(savedQuestions);
        if (Array.isArray(parsed)) {
          unansweredQAPairs = parsed;
          console.log('復元した未回答質問数:', parsed.length);
        }
      }
      
      if (savedInputs) {
        const parsed = JSON.parse(savedInputs);
        if (typeof parsed === 'object' && parsed !== null) {
          questionInputs = parsed;
        }
      }

      if (savedNewQuestions) {
        const parsed = JSON.parse(savedNewQuestions);
        if (Array.isArray(parsed)) {
          newQuestions = parsed;
          console.log('復元した新規質問数:', parsed.length);
        }
      }
    } catch (error) {
      console.error('localStorageからのデータ読み込みエラー:', error);
    }
  }

  // localStorageにデータを保存
  function saveToStorage() {
    if (typeof window === 'undefined') return;
    
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(unansweredQAPairs));
      localStorage.setItem(STORAGE_KEY_INPUTS, JSON.stringify(questionInputs));
      localStorage.setItem(STORAGE_KEY_NEW_QUESTIONS, JSON.stringify(newQuestions));
      console.log('保存した未回答質問数:', unansweredQAPairs.length, '新規質問数:', newQuestions.length);
    } catch (error) {
      console.error('localStorageへのデータ保存エラー:', error);
    }
  }

  // 初期化フラグ
  let isInitialized = $state(false);

  // ページ読み込み時に新規質問を取得とlocalStorageから復元
  $effect(() => {
    if (!isInitialized) {
      loadFromStorage();
      if (isOwner) {
        loadNewQuestions();
      }
      isInitialized = true;
    }
  });

  // データが変更された時にlocalStorageに保存（初期化後のみ）
  $effect(() => {
    if (isInitialized) {
      saveToStorage();
    }
  });
</script>

<!-- 質問ガチャとカテゴリフィルター -->
<div>
  <!-- 質問ガチャ -->
  <div class="rounded-2xl bg-white p-6">
    <h2 class="text-lg font-semibold text-gray-800 mb-4">質問ガチャ</h2>
    
    <div class="flex items-center gap-4 mb-4">
      <span class="text-sm text-gray-700">質問数</span>
      <select bind:value={gachaQuestionCount} class="px-3 py-1 border border-gray-300 rounded text-sm">
        {#each [1, 2, 3, 4, 5] as num (num)}
          <option value={num}>{num}問</option>
        {/each}
      </select>
      <button onclick={performRandomGacha} class="px-4 py-2 bg-orange-500 text-white rounded-lg text-sm font-medium hover:bg-orange-600">
        ガチャ
      </button>
    </div>
  </div>

  <!-- カテゴリフィルター -->
  <CategoryFilter
    {categories}
    {selectedCategories}
    answeredCount={0}
    onToggleCategory={(categoryId) => {
      if (selectedCategories.includes(categoryId)) {
        selectedCategories = selectedCategories.filter(c => c !== categoryId);
      } else {
        selectedCategories = [...selectedCategories, categoryId];
      }
    }}
    onClearFilters={() => {
      selectedCategories = [];
    }}
  />
</div>

<!-- 受信した質問 -->
{#if newQuestions && newQuestions.length > 0}
  <div class="mt-8 rounded-2xl border border-gray-200 bg-white p-6">
    <div class="flex items-center gap-2 mb-4">
      <h2 class="text-lg font-semibold text-gray-800">受信した質問</h2>
      <span class="rounded-full bg-gray-100 px-2 py-0.5 text-xs font-medium text-gray-600">{newQuestions.length}件</span>
    </div>
    
    {#each newQuestions as question (`new-question-${question.messageId}`)}
      {@const questionKey = `new-${question.groupId}`}
      <div class="border border-gray-200 rounded-lg p-4 mb-4">
        <div class="flex items-center gap-2 mb-3">
          <span class="text-sm text-gray-600">{question.fromDisplayName}</span>
          <span class="text-xs text-gray-400">{new Date(question.createdAt).toLocaleDateString('ja-JP')}</span>
        </div>
        
        <p class="text-gray-700 mb-3">{question.content}</p>
        
        <textarea bind:value={questionInputs[questionKey]} placeholder="回答を入力..." class="w-full rounded-lg border border-gray-300 p-3 text-sm focus:border-orange-400 focus:outline-none mb-3" rows="3"></textarea>
        
        <div class="flex items-center justify-end gap-3">
          <button onclick={() => handleSkipNewQuestion(question)} class="px-4 py-2 text-sm text-gray-500 hover:text-gray-700">スキップ</button>
          <button onclick={() => handleAnswerNewQuestion(question)} disabled={!questionInputs[questionKey]?.trim()} class="rounded-lg bg-orange-500 px-4 py-2 text-sm text-white hover:bg-orange-600 disabled:opacity-50">回答を送信</button>
        </div>
      </div>
    {/each}
  </div>
{/if}

<!-- 回答待ちの質問 -->
{#if unansweredQAPairs && unansweredQAPairs.length > 0}
  <div class="mt-8 rounded-2xl border border-gray-200 bg-white p-6">
    <div class="flex items-center gap-2 mb-4">
      <h2 class="text-lg font-semibold text-gray-800">回答待ちの質問</h2>
      <span class="rounded-full bg-gray-100 px-2 py-0.5 text-xs font-medium text-gray-600">{unansweredQAPairs.length}件</span>
    </div>
    
    {#each unansweredQAPairs as pair (`unanswered-gacha-${pair.groupId}-${pair.question.questionId}-${pair.questionIndex}`)}
      {@const questionKey = `${pair.groupId}-${pair.questionIndex}`}
      <div class="border border-gray-200 rounded-lg p-4 mb-4" data-question-id="{pair.groupId}">
        {#if pair.categoryInfo}
          <div class="mb-3">
            <span class="text-xs text-gray-500">{pair.categoryInfo.label}</span>
          </div>
        {/if}
        
        <p class="text-gray-700 mb-3">{pair.question.text}</p>
        
        <textarea bind:value={questionInputs[questionKey]} placeholder="回答を入力..." class="w-full rounded-lg border border-gray-300 p-3 text-sm focus:border-orange-400 focus:outline-none mb-3" rows="3"></textarea>
        
        <div class="flex items-center justify-end gap-3">
          <button onclick={() => handleSkip(pair)} class="px-4 py-2 text-sm text-gray-500 hover:text-gray-700">スキップ</button>
          <button onclick={() => handleSaveAnswer(pair)} disabled={!questionInputs[questionKey]?.trim()} class="rounded-lg bg-orange-500 px-4 py-2 text-sm text-white hover:bg-orange-600 disabled:opacity-50">保存</button>
        </div>
      </div>
    {/each}
  </div>
{/if}

