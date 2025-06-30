<script lang="ts">
  const login = () => {
    alert('Xログインはまだ未実装です');
  };
</script>

<main class="min-h-screen flex flex-col items-center justify-center p-8 text-center bg-gray-100">
  <h1 class="text-5xl text-gray-600 font-bold mb-12">hitoQとは</h1>
  <p class="text-lg text-gray-700 leading-relaxed mb-4">
    hitoQは、SNSユーザーが自分の価値観や内面をカジュアルに共有できる自己紹介ページサービスです。
  </p>
  <p class="text-lg text-gray-700 leading-relaxed mb-4">
    提示されたQ&Aテンプレートに回答することで、自分だけのプロフィールページを簡単に作成できます。
  </p>
  <p class="text-lg text-gray-700 leading-relaxed mb-6">
    「好きなもの」や「大切にしていること」など、普段のタイムラインでは見えづらい個性を伝え、
    新たなつながりのきっかけを提供します。
  </p>

  <hr class="w-2/3 border-t-2 border-orange-300 my-6 mx-auto" />

  <p class="text-lg text-gray-700 mb-6 max-w-lg leading-relaxed mx-auto">
    hitoQは、X（旧Twitter）アカウントでログインするだけで利用できます。
  </p>

  <button onclick={login} 
    class="flex items-center space-x-3 bg-black text-white px-6 py-3 rounded-full shadow hover:bg-gray-600 transition font-semibold mb-4 cursor-pointer"
  >
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 1227" fill="currentColor" class="w-5 h-5">
      <path d="M745 561L1167 0H1064L698 482 389 0H0L455 704 0 1227H103L494 717 823 1227H1200L745 561ZM576 649L514 558 172 101H342L622 531 685 622 1041 1117H873L576 649Z" />
    </svg>
    <span>Xでログインする</span>
  </button>

  <p class="text-sm text-gray-700">ログインせずにお友達のページを見る</p>
</main>