<script lang="ts">
  import { redirectToTwitterLogin } from '$lib/api/client';

  const login = () => {
    redirectToTwitterLogin();
  };

  const handleSearch = (event: Event) => {
    event.preventDefault();

    // 入力値を取得して検索処理を行う（ここは将来的に実装）
    const form = event.target as HTMLFormElement;
    const input = form.querySelector('input[type="text"]') as HTMLInputElement;
    const username = input.value;

    if (username) {
      alert(`「${username}」を検索します（未実装）`);
      // 将来的には window.location.href = `/user/${username}`; のような処理になる
    } else {
      alert('ユーザー名を入力してください。');
    }
  };
</script>

<main class="min-h-screen flex flex-col items-center justify-center p-8 bg-gray-50 text-gray-700">
  <h1 class="text-5xl font-bold mb-4 text-transparent bg-clip-text bg-gradient-to-r from-orange-500 to-amber-500">
    見えない「好き」で、つながろう。
  </h1>

  <p class="text-lg text-gray-600 leading-relaxed mb-12 max-w-2xl text-center">
    Xのプロフィールだけでは伝わらない、あなたの価値観や内面。
    <br />
    hitoQは、簡単なQ&Aに答えるだけで「あなたのこと」が伝わるページを作れるサービスです。
  </p>

  <div class="bg-white p-4 rounded-xl shadow-lg mb-12 w-full max-w-md">
    <img src="/path/to/sample-image.png" alt="hitoQのプロフィールサンプル" class="rounded-lg" />
  </div>

  <h2 class="text-2xl font-bold mb-4">さあ、はじめよう</h2>
  <p class="text-gray-600 mb-6">Xアカウントでログインするだけ。3分であなたのページが完成します。</p>

  <button onclick={login}
    class="flex items-center space-x-3 bg-black text-white px-8 py-3 rounded-full shadow-lg hover:bg-gray-800
    transition-transform hover:scale-105 font-semibold mb-8 text-lg"
  >
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 1227" fill="currentColor" class="w-6 h-6">
      <path d="M745 561L1167 0H1064L698 482 389 0H0L455 704 0 1227H103L494 717 823 1227H1200L745 561ZM576 649L514 558 172 101H342L622 531 685 622 1041 1117H873L576 649Z" />
    </svg>
    <span>Xでログイン</span>
  </button>
</main>
