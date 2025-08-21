<script lang="ts">
  import { redirectToTwitterLogin } from "$lib/api-client/auth";
  import { goto } from "$app/navigation";
  import type { PageData } from "./$types";

  let { data }: { data: PageData } = $props();

  $effect(() => {
    // If the user is logged in, redirect to the profile page
    if (data?.isLoggedIn && data?.userName) {
      goto(`/${data.userName}`);
    }
  });

  const login = () => {
    redirectToTwitterLogin();
  };
</script>

<main
  class="theme-bg-surface theme-text-secondary flex min-h-screen flex-col items-center justify-center p-4 md:p-8"
>
  <h1
    class="mb-6 text-center text-4xl font-bold theme-text-brand md:text-5xl bg-gradient-to-r from-orange-500 to-amber-500 bg-clip-text md:text-transparent"
  >
    「あの人どんな人？」から「友達」に。
  </h1>

  <div class="mb-8 max-w-2xl px-4 text-center md:mb-12">
    <p class="theme-text-muted text-base leading-relaxed md:text-lg">
      SNSでは伝わらない「あなたらしさ」を、Q&Aで表現してみませんか？
      hitoQは、質問に答えるだけであなたの内面が伝わるページが作れるサービスです。
    </p>
    <p class="theme-text-muted mt-4 text-base leading-relaxed md:text-lg">
      気になるあの人のことを知ったり、自分のことを知ってもらったり。
      匿名の質問から始まるコミュニケーションで、新しい関係を育てましょう。
    </p>
  </div>

  <div
    class="container-responsive mb-8 grid max-w-4xl gap-6 sm:grid-cols-2 md:mb-12 md:gap-8 lg:grid-cols-3"
  >
    <div class="card text-center">
      <div class="card-body">
        <div class="mb-4 flex justify-center text-orange-400">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            stroke-width="1.5"
            stroke="currentColor"
            class="h-8 w-8"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              d="M16.862 4.487l1.687-1.688a1.875 1.875 0 112.652 2.652L10.582 16.07a4.5 4.5 0 01-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 011.13-1.897l8.932-8.931zm0 0L19.5 7.125M18 14v4.75A2.25 2.25 0 0115.75 21H5.25A2.25 2.25 0 013 18.75V8.25A2.25 2.25 0 015.25 6H10"
            />
          </svg>
        </div>
        <h3 class="theme-text-primary mb-2 text-lg font-semibold md:text-xl">Q&A</h3>
        <p class="theme-text-muted text-sm md:text-base">
          SNSでは伝わりにくいあなたの内面や価値観をQ&A形式で表現。質問に答えることで、自分らしさが伝わります。
        </p>
      </div>
    </div>

    <div class="card text-center">
      <div class="card-body">
        <div class="mb-4 flex justify-center text-orange-400">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            stroke-width="1.5"
            stroke="currentColor"
            class="h-8 w-8"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              d="M8.625 12a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0H8.25m4.125 0a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0H12m4.125 0a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0h-.375M21 12c0 4.556-4.03 8.25-9 8.25a9.764 9.764 0 01-2.555-.337A5.972 5.972 0 015.41 20.97a5.969 5.969 0 01-.474-.065 4.48 4.48 0 00.978-2.025c.09-.457-.133-.901-.467-1.226C3.93 16.178 3 14.189 3 12c0-4.556 4.03-8.25 9-8.25s9 3.694 9 8.25z"
            />
          </svg>
        </div>
        <h3 class="theme-text-primary mb-2 text-lg font-semibold md:text-xl">トーク</h3>
        <p class="theme-text-muted text-sm md:text-base">
          Q&Aへの深掘りや新しい質問をスレッド形式で誰でも投稿可能。公開トークで、より深いコミュニケーションを。
        </p>
      </div>
    </div>

    <div class="card text-center sm:col-span-2 lg:col-span-1">
      <div class="card-body">
        <div class="mb-4 flex justify-center text-orange-400">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            stroke-width="1.5"
            stroke="currentColor"
            class="h-8 w-8"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              d="M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.607 10.607z"
            />
          </svg>
        </div>
        <h3 class="theme-text-primary mb-2 text-lg font-semibold md:text-xl">発見</h3>
        <p class="theme-text-muted text-sm md:text-base">
          新着ユーザーやランダム表示から、思いがけない出会いを。あなたの興味に合う人を見つけて、新しいつながりを作りましょう。
        </p>
      </div>
    </div>
  </div>

  <h2 class="theme-text-primary mb-4 text-center text-xl font-bold md:text-2xl">
    さあ、はじめよう
  </h2>
  <p class="theme-text-muted mb-6 px-4 text-center text-sm md:text-base">
    Xアカウントでログインするだけ。3分であなたのページが完成します。
  </p>

  <button
    onclick={login}
    class="mb-8 flex items-center space-x-2 rounded-full bg-black px-6 py-2.5 text-base font-semibold text-white shadow-lg transition-transform hover:scale-105 hover:bg-gray-800 md:space-x-3 md:px-8 md:py-3 md:text-lg dark:hover:bg-gray-700"
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