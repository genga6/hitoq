<script lang="ts">
  import type { CategoryInfo } from "$lib/types";
  import type { Question } from "$lib/types";
  import QuestionAnswerCard from "$lib/components/domain/qna/QuestionAnswerCard.svelte";
  import GachaControls from "./components/GachaControls.svelte";
  import ToastContainer from "$lib/components/ui/ToastContainer.svelte";
  import { toasts } from "$lib/stores/toast";
  import { fly } from "svelte/transition";

  type Props = {
    categories: Record<string, CategoryInfo>;
    userId: string;
  };

  const { categories, userId }: Props = $props();

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
    isNew?: boolean; // 新しく追加された質問かどうか
  }

  // ガチャ結果の未回答質問を管理
  let unansweredQAPairs = $state<UnansweredQAPair[]>([]);

  // localStorageのキー
  const STORAGE_KEY = `hitoq-unanswered-questions-${userId}`;
  const STORAGE_KEY_INPUTS = `hitoq-question-inputs-${userId}`;

  function generateGroupId(): string {
    return `group-${Date.now()}-${Math.random().toString(36).slice(2, 11)}`;
  }

  async function performGacha(categoryFilter?: string, count: number = gachaQuestionCount) {
    try {
      let questions;

      if (categoryFilter) {
        const { getQuestionsByCategory } = await import("$lib/api-client/qna");
        questions = await getQuestionsByCategory(categoryFilter);
      } else {
        const { getAllQuestions } = await import("$lib/api-client/qna");
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
          groupIndex: index,
          categoryInfo: categories[question.categoryId],
          isNew: true // 新しい質問としてマーク
        })
      );

      unansweredQAPairs = [...newUnansweredPairs, ...unansweredQAPairs];
      
      // 少し遅延させてアニメーション効果を演出
      setTimeout(() => {
        unansweredQAPairs = unansweredQAPairs.map(pair => ({
          ...pair,
          isNew: false
        }));
      }, 2000);
      
      saveToStorage();

      return selectedQuestions.length;
    } catch (error) {
      console.error("ガチャ実行エラー:", error);
      return 0;
    }
  }

  async function performRandomGacha(count: number = gachaQuestionCount) {
    let resultCount = 0;
    // カテゴリが選択されている場合はカテゴリフィルターを適用
    if (selectedCategories.length > 0) {
      // 複数カテゴリが選択されている場合はランダムに1つを選択
      const randomCategory =
        selectedCategories[Math.floor(Math.random() * selectedCategories.length)];
      resultCount = await performGacha(randomCategory, count);
      if (resultCount === 0) {
        const categoryInfo = categories[randomCategory];
        toasts.warning(
          `${categoryInfo?.label || randomCategory}カテゴリにはもう回答できる質問がありません！`
        );
      }
    } else {
      resultCount = await performGacha(undefined, count);
      if (resultCount === 0) {
        toasts.warning("もう回答できる質問がありません！");
      }
    }

    if (resultCount > 0) {
      toasts.success(`${resultCount}問の質問を追加しました！`);
    }
  }

  function toggleCategory(categoryId: string) {
    if (selectedCategories.includes(categoryId)) {
      selectedCategories = selectedCategories.filter((c) => c !== categoryId);
    } else {
      selectedCategories = [...selectedCategories, categoryId];
    }
  }

  function clearFilters() {
    selectedCategories = [];
  }

  async function handleSaveAnswer(pair: UnansweredQAPair) {
    const questionKey = `${pair.groupId}-${pair.questionIndex}`;
    const inputValue = questionInputs[questionKey] || "";

    if (!inputValue.trim()) return;

    try {
      const { createAnswer } = await import("$lib/api-client/qna");

      // 質問に対する回答を作成
      await createAnswer(userId, pair.question.questionId, inputValue.trim());

      // 成功したら未回答リストから削除（フェードアウト効果付き）
      const questionElement = document.querySelector(
        `[data-question-id="${pair.groupId}"]`
      ) as HTMLElement;
      if (questionElement) {
        questionElement.style.transition = "opacity 0.3s ease-out, transform 0.3s ease-out";
        questionElement.style.opacity = "0";
        questionElement.style.transform = "translateY(-10px)";

        setTimeout(() => {
          unansweredQAPairs = unansweredQAPairs.filter((p) => p.groupId !== pair.groupId);
          questionInputs[questionKey] = "";
          saveToStorage();
        }, 300);
      } else {
        unansweredQAPairs = unansweredQAPairs.filter((p) => p.groupId !== pair.groupId);
        questionInputs[questionKey] = "";
        saveToStorage();
      }
    } catch (error) {
      console.error("回答保存エラー:", error);
      alert("回答の保存に失敗しました。");
    }
  }

  function handleSkip(pair: UnansweredQAPair) {
    // 未回答リストから削除
    unansweredQAPairs = unansweredQAPairs.filter((p) => p.groupId !== pair.groupId);
    // 入力値をクリア
    const questionKey = `${pair.groupId}-${pair.questionIndex}`;
    questionInputs[questionKey] = "";
    saveToStorage();
  }

  // localStorageから保存されたデータを読み込み
  function loadFromStorage() {
    if (typeof window === "undefined") return;

    try {
      const savedQuestions = localStorage.getItem(STORAGE_KEY);
      const savedInputs = localStorage.getItem(STORAGE_KEY_INPUTS);

      if (savedQuestions) {
        const parsed = JSON.parse(savedQuestions);
        if (Array.isArray(parsed)) {
          unansweredQAPairs = parsed;
          console.log("復元した未回答質問数:", parsed.length);
        }
      }

      if (savedInputs) {
        const parsed = JSON.parse(savedInputs);
        if (typeof parsed === "object" && parsed !== null) {
          questionInputs = parsed;
        }
      }
    } catch (error) {
      console.error("localStorageからのデータ読み込みエラー:", error);
    }
  }

  // localStorageにデータを保存
  function saveToStorage() {
    if (typeof window === "undefined") return;

    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(unansweredQAPairs));
      localStorage.setItem(STORAGE_KEY_INPUTS, JSON.stringify(questionInputs));
      console.log("保存した未回答質問数:", unansweredQAPairs.length);
    } catch (error) {
      console.error("localStorageへのデータ保存エラー:", error);
    }
  }

  // 初期化フラグ
  let isInitialized = $state(false);

  // ページ読み込み時にlocalStorageから復元
  $effect(() => {
    if (!isInitialized) {
      loadFromStorage();
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
<GachaControls
  {categories}
  {gachaQuestionCount}
  {selectedCategories}
  onGacha={performRandomGacha}
  onToggleCategory={toggleCategory}
  onClearFilters={clearFilters}
/>

<!-- 回答待ちの質問 -->
{#if unansweredQAPairs && unansweredQAPairs.length > 0}
  <div class="theme-border theme-bg-surface mt-8 rounded-2xl p-6">
    <div class="mb-4 flex items-center gap-2">
      <h2 class="theme-text-primary text-lg font-semibold">回答待ちの質問</h2>
      <span class="theme-bg-subtle theme-text-muted rounded-full px-2 py-0.5 text-xs font-medium"
        >{unansweredQAPairs.length}件</span
      >
    </div>

    <div class="divide-y divide-gray-200 dark:divide-gray-700">
      {#each unansweredQAPairs as pair, i (`unanswered-gacha-${pair.groupId}-${pair.question.questionId}-${pair.questionIndex}`)}
        {@const questionKey = `${pair.groupId}-${pair.questionIndex}`}
        <div 
          data-question-id={pair.groupId} 
          class="py-6 first:pt-0 last:pb-0 {pair.isNew ? 'bg-orange-50 dark:bg-orange-900/20 rounded-lg -mx-2 px-4 border-l-4 border-orange-400' : ''}"
          transition:fly={{ y: 20, duration: 300, delay: i * 100 }}
        >
          <QuestionAnswerCard
            question={pair.question.text}
            answer={questionInputs[questionKey] || ""}
            categoryInfo={pair.categoryInfo}
            mode="input"
            onAnswerChange={(value) => {
              questionInputs[questionKey] = value;
            }}
            primaryAction={{
              label: "保存",
              onClick: () => handleSaveAnswer(pair),
              disabled: !questionInputs[questionKey]?.trim()
            }}
            secondaryAction={{
              label: "スキップ",
              onClick: () => handleSkip(pair)
            }}
          />
          {#if pair.isNew}
            <div class="mt-2 flex items-center gap-2 text-sm text-orange-600 dark:text-orange-400 font-medium">
              <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v3m0 0v3m0-3h3m-3 0H9m12 0a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              新しく追加された質問
            </div>
          {/if}
        </div>
      {/each}
    </div>
  </div>
{/if}

<!-- トースト通知 -->
<ToastContainer />
