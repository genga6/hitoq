<script lang="ts">
  import type { QATemplate, UserAnswerGroup } from '$lib/types/qna';
  import QAGroup from './QAGroup.svelte';
  import { slide } from 'svelte/transition';
  import { fade } from 'svelte/transition';

  const { initialAnswerGroups, availableTemplates, isOwner } = $props<{
    initialAnswerGroups: UserAnswerGroup[];
    availableTemplates: QATemplate[];
    isOwner: boolean;
  }>();

  let answerGroups = $state(initialAnswerGroups || []);
  let showTemplateSelector = $state(false);

  async function addQAGroup(template: QATemplate) {
    if (!isOwner) return;

    const newAnswerGroup: UserAnswerGroup = {
      templateId: template.id,
      templateTitle: template.title,
      answers: template.questions.map(q => ({ question: q, answer: '' })),
    };

    // TODO: ここでサーバーに新しいグループを作成するAPIを叩く
    // const createdGroup = await fetch('/api/qa', { method: 'POST', body: JSON.stringify(newAnswerGroup) });
    // const result = await createdGroup.json();

    answerGroups.push(newAnswerGroup);

    showTemplateSelector = false;
  }

  function handleAnswerUpdate(groupIndex: number, questionIndex: number, newAnswer: string) {
    const newAnswerGroups = [...answerGroups];
    const updatedGroup = { ...newAnswerGroups[groupIndex] }; 
    const updatedAnswers = [...updatedGroup.answers]; 

    updatedAnswers[questionIndex] = { ...updatedAnswers[questionIndex], answer: newAnswer };
    updatedGroup.answers = updatedAnswers;
    newAnswerGroups[groupIndex] = updatedGroup;
    answerGroups = newAnswerGroups;

  }
</script>

<div>
  {#if answerGroups && answerGroups.length > 0}
    <div class="space-y-6">
      {#each answerGroups as group, groupIndex (group.templateId)}
        <QAGroup 
          answerGroup={group} 
          {isOwner} 
          onAnswerUpdate={(questionIndex, newAnswer) => 
            handleAnswerUpdate(groupIndex, questionIndex, newAnswer)
          }
        />
      {/each}
    </div>
  {:else if isOwner}
    <div class="text-center py-12 px-6 bg-gray-50 rounded-3xl">
      <p class="text-lg text-gray-600">まだ回答済みのQ&Aがありません。</p>
      <p class="mt-2 text-gray-500">下のボタンから新しい質問セットを追加してみましょう！</p>
    </div>
  {:else}
    <div class="text-center py-12 px-6 bg-gray-50 rounded-3xl">
      <p class="text-lg text-gray-600">このユーザーはまだQ&Aに回答していません。</p>
    </div>
  {/if}

  {#if isOwner}
    <div class="mt-12 text-center">
      {#if !showTemplateSelector}
        <button
          onclick={() => showTemplateSelector = true}
          class="inline-flex items-center gap-2 rounded-full bg-orange-500 px-6 py-3 text-lg font-semibold text-white shadow-md transition-transform hover:scale-105 hover:bg-orange-600 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:ring-offset-2"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
          </svg>
          新しいQ&Aを追加する
        </button>
      {/if}

      {#if showTemplateSelector}
        <div transition:slide={{ duration: 300 }} class="mt-8 rounded-2xl bg-white p-6 shadow-lg border border-gray-200">
          <div class="flex justify-between items-center mb-4">
              <h3 class="text-xl font-bold text-gray-800">挑戦するQ&Aを選ぶ</h3>
              <!-- svelte-ignore a11y_consider_explicit_label -->
              <button onclick={() => showTemplateSelector = false} class="text-gray-400 hover:text-gray-600">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {#each availableTemplates as template (template.id)}
              <button
                onclick={() => addQAGroup(template)}
                class="group flex flex-col items-center justify-center p-6 text-center rounded-xl border-2 border-dashed border-gray-300 transition-all duration-300 hover:border-orange-400 hover:bg-orange-50 hover:shadow-sm"
              >
                <span class="text-lg font-semibold text-gray-700 group-hover:text-orange-600">{template.title}</span>
                <span class="mt-1 text-sm text-gray-500">{template.questions.length}問</span>
              </button>
            {:else}
              <p class="text-gray-500 md:col-span-2 lg:col-span-3 text-center py-4">
                すべてのQ&Aに回答済みです！素晴らしい！
              </p>
            {/each}
          </div>
        </div>
      {/if}
    </div>
  {/if}
</div>