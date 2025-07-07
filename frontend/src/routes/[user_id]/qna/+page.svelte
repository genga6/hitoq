<script lang="ts">
  import QAPage from './QAPage.svelte'
  import type { PageData } from './$types';

  const { data } = $props();
  console.log('データ', data)
</script>

<QAPage
  initialAnswerGroups={data.userAnswerGroups}
  availableTemplates={data.availableTemplates}
/>
