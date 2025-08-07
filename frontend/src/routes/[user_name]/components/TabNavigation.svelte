<script lang="ts">
  import { page } from "$app/state";
  import type { Profile } from "$lib/types";
  import TabGroup from "$lib/components/ui/TabGroup.svelte";

  type Props = {
    userName: Profile["userName"];
    isOwner: boolean;
  };
  const { userName, isOwner }: Props = $props();

  const navigationTabs = $derived([
    { id: `/${userName}`, label: "プロフィール", href: `/${userName}` },
    ...(isOwner
      ? [
          {
            id: `/${userName}/answer-questions`,
            label: "質問に答える",
            href: `/${userName}/answer-questions`
          }
        ]
      : []),
    { id: `/${userName}/qna`, label: "Q&A", href: `/${userName}/qna` },
    { id: `/${userName}/messages`, label: "メッセージ", href: `/${userName}/messages` }
  ]);
</script>

<nav>
  <TabGroup tabs={navigationTabs} activeTab={page.url.pathname} variant="navigation" />
</nav>
