<script lang="ts">
  import HeaderDesktop from "./HeaderDesktop.svelte";
  import HeaderMobile from "./HeaderMobile.svelte";
  import type { UserCandidate } from "$lib/types";
  import { searchUsersByDisplayName } from "$lib/api-client/users";
  import { goto, invalidate } from "$app/navigation";
  import { errorUtils } from "$lib/stores/errorStore";

  type Props = {
    isLoggedIn: boolean;
    currentUser?: {
      userId: string;
      userName: string;
      displayName: string;
    } | null;
    onLogin: () => void;
    onLogout: () => Promise<void>;
  };

  const { isLoggedIn, currentUser, onLogin, onLogout }: Props =
    $props();

  let searchQuery = $state("");
  let candidates = $state<UserCandidate[]>([]);
  let showCandidates = $state(false);
  let isLoading = $state(false);
  let debounceTimer: ReturnType<typeof setTimeout> | null = null;

  const showCandidateList = (candidatesData: UserCandidate[]) => {
    candidates = candidatesData;
    showCandidates = true;
  };

  const selectCandidate = async (candidate: UserCandidate) => {
    searchQuery = "";
    showCandidates = false;
    candidates = [];
    await invalidate(() => true);
    await goto(`/${candidate.userName}`);
  };

  const performSearch = async () => {
    if (searchQuery.trim() === "") {
      showCandidates = false;
      return;
    }

    isLoading = true;

    try {
      const candidatesData = await searchUsersByDisplayName(searchQuery);
      if (candidatesData.length > 0) {
        showCandidateList(candidatesData);
      } else {
        candidates = [];
        showCandidates = true;
      }
    } catch (error) {
      console.error("Search failed:", error);
      errorUtils.networkError("検索に失敗しました");
      candidates = [];
      showCandidates = true;
    } finally {
      isLoading = false;
    }
  };

  const handleInput = (event: Event) => {
    const target = event.target as HTMLInputElement;
    searchQuery = target.value;

    if (debounceTimer) clearTimeout(debounceTimer);

    if (searchQuery.trim() === "") {
      showCandidates = false;
      return;
    }

    debounceTimer = setTimeout(() => {
      performSearch();
    }, 300);
  };

  const handleKeydown = (e: KeyboardEvent) => {
    if (e.key === "Enter" && searchQuery.trim() !== "") {
      if (debounceTimer) clearTimeout(debounceTimer);
      performSearch();
    }
  };
</script>

<header class="theme-bg-surface relative z-50 w-full py-4 shadow-md md:py-6 lg:py-8">
  <div class="container-responsive max-w-4xl">
    <!-- Desktop Layout -->
    <div class="hidden sm:block">
      <HeaderDesktop
        {isLoggedIn}
        {currentUser}
        {searchQuery}
        {candidates}
        {showCandidates}
        {isLoading}
        {onLogin}
        {onLogout}
        {handleInput}
        {handleKeydown}
        {selectCandidate}
      />
    </div>

    <!-- Mobile Layout -->
    <div class="sm:hidden">
      <HeaderMobile
        {isLoggedIn}
        {currentUser}
        {searchQuery}
        {candidates}
        {showCandidates}
        {isLoading}
        {onLogin}
        {onLogout}
        {handleInput}
        {handleKeydown}
        {selectCandidate}
      />
    </div>
  </div>
</header>
