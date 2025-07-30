<script lang="ts">
  import { redirectToTwitterLogin } from '$lib/api-client/auth';
  import { goto } from '$app/navigation';

  let { data } = $props();

  $effect(() => {
    // ログイン済みの場合はプロフィールページにリダイレクト
    if (data?.isLoggedIn && data?.userName) {
      goto(`/${data.userName}`);
    }
  });

  const login = () => {
    redirectToTwitterLogin();
  };
</script>

<main
  class="flex min-h-screen flex-col items-center justify-center bg-gray-50 p-4 text-gray-700 md:p-8"
>
  <h1
    class="mb-6 bg-gradient-to-r from-orange-500 to-amber-500 bg-clip-text text-center text-4xl font-bold text-transparent md:text-5xl"
  >
    あなたの「好き」を、もっと伝えよう
  </h1>

  <p
    class="mb-8 max-w-2xl px-4 text-center text-base leading-relaxed text-gray-600 md:mb-12 md:text-lg"
  >
    Xのプロフィールだけでは伝わらない、あなたの価値観や内面。
    <br class="hidden sm:block" />
    hitoQは、簡単なQ&Aに答えるだけで「あなたのこと」が伝わるページを作れるサービスです。
  </p>

  <div
    class="container-responsive mb-8 grid max-w-4xl gap-6 sm:grid-cols-2 md:mb-12 md:gap-8 lg:grid-cols-3"
  >
    <div class="card text-center">
      <div class="card-body">
        <div class="mb-4 text-2xl md:text-3xl">💬</div>
        <h3 class="mb-2 text-lg font-semibold md:text-xl">質問に答えるだけ</h3>
        <p class="text-sm text-gray-600 md:text-base">
          好きなもの、価値観、趣味について簡単な質問に答えるだけ。複雑な設定は不要です。
        </p>
      </div>
    </div>

    <div class="card text-center">
      <div class="card-body">
        <div class="mb-4 text-2xl md:text-3xl">🎯</div>
        <h3 class="mb-2 text-lg font-semibold md:text-xl">あなたらしさを表現</h3>
        <p class="text-sm text-gray-600 md:text-base">
          やりたいことリスト（バケットリスト）やQ&Aで、プロフィールでは伝わらない「本当のあなた」を表現できます。
        </p>
      </div>
    </div>

    <div class="card text-center sm:col-span-2 lg:col-span-1">
      <div class="card-body">
        <div class="mb-4 text-2xl md:text-3xl">🔗</div>
        <h3 class="mb-2 text-lg font-semibold md:text-xl">簡単にシェア</h3>
        <p class="text-sm text-gray-600 md:text-base">
          作成したページは専用URLで簡単にシェア。SNSでの自己紹介がもっと深くなります。
        </p>
      </div>
    </div>
  </div>

  <h2 class="mb-4 text-center text-xl font-bold md:text-2xl">さあ、はじめよう</h2>
  <p class="mb-6 px-4 text-center text-sm text-gray-600 md:text-base">
    Xアカウントでログインするだけ。3分であなたのページが完成します。
  </p>

  <button
    onclick={login}
    class="mb-8 flex items-center space-x-2 rounded-full bg-black px-6 py-2.5 text-base font-semibold text-white shadow-lg transition-transform hover:scale-105 hover:bg-gray-800 md:space-x-3 md:px-8 md:py-3 md:text-lg"
  >
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 1200 1227"
      fill="currentColor"
      class="h-5 w-5 md:h-6 md:w-6"
    >
      <path
        d="M745 561L1167 0H1064L698 482 389 0H0L455 704 0 1227H103L494 717 823 1227H1200L745 561ZM576 649L514 558 172 101H342L622 531 685 622 1041 1117H873L576 649Z"
      />
    </svg>
    <span>Xでログイン</span>
  </button>
</main>
