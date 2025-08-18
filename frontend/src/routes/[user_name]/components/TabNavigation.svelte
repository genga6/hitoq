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
    { id: `/${userName}`, label: "プロフィール", href: `/${userName}`},
    ...(isOwner
      ? [
          {
            id: `/${userName}/answer-questions`,
            label: "回答する",
            href: `/${userName}/answer-questions`,
          }
        ]
      : []),
    { id: `/${userName}/qna`, label: "回答一覧", href: `/${userName}/qna`},
    { id: `/${userName}/talk`, label: "トーク", href: `/${userName}/talk`}
  ]);
</script>

<nav>
  <TabGroup tabs={navigationTabs} activeTab={page.url.pathname} variant="navigation" size="md" />
</nav>

