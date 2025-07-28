<script lang="ts">
  import QAPage from './QAPage.svelte';
  import type { PageData } from './$types';

  const { data }: { data: PageData } = $props();
  
</script>

<QAPage
  initialAnswerGroups={data.userAnswerGroups}
  availableTemplates={data.availableTemplates}
  categories={data.categories}
  isOwner={data.isOwner}
  userId={data.profile.userId}
/>
