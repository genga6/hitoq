<script lang="ts">
	import { redirectToTwitterLogin } from '$lib/api/client';
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

<main class="flex min-h-screen flex-col items-center justify-center bg-gray-50 p-8 text-gray-700">
	<h1
		class="mb-6 bg-gradient-to-r from-orange-500 to-amber-500 bg-clip-text text-5xl font-bold text-transparent"
	>
		あなたの「好き」を、もっと伝えよう
	</h1>

	<p class="mb-12 max-w-2xl text-center text-lg leading-relaxed text-gray-600">
		Xのプロフィールだけでは伝わらない、あなたの価値観や内面。
		<br />
		hitoQは、簡単なQ&Aに答えるだけで「あなたのこと」が伝わるページを作れるサービスです。
	</p>

	<div class="mb-12 grid max-w-4xl gap-8 md:grid-cols-3">
		<div class="rounded-lg bg-white p-6 text-center shadow-sm">
			<div class="mb-4 text-3xl">💬</div>
			<h3 class="mb-2 text-xl font-semibold">質問に答えるだけ</h3>
			<p class="text-gray-600">
				好きなもの、価値観、趣味について簡単な質問に答えるだけ。複雑な設定は不要です。
			</p>
		</div>

		<div class="rounded-lg bg-white p-6 text-center shadow-sm">
			<div class="mb-4 text-3xl">🎯</div>
			<h3 class="mb-2 text-xl font-semibold">あなたらしさを表現</h3>
			<p class="text-gray-600">
				やりたいことリスト（バケットリスト）やQ&Aで、プロフィールでは伝わらない「本当のあなた」を表現できます。
			</p>
		</div>

		<div class="rounded-lg bg-white p-6 text-center shadow-sm">
			<div class="mb-4 text-3xl">🔗</div>
			<h3 class="mb-2 text-xl font-semibold">簡単にシェア</h3>
			<p class="text-gray-600">
				作成したページは専用URLで簡単にシェア。SNSでの自己紹介がもっと深くなります。
			</p>
		</div>
	</div>

	<h2 class="mb-4 text-2xl font-bold">さあ、はじめよう</h2>
	<p class="mb-6 text-gray-600">Xアカウントでログインするだけ。3分であなたのページが完成します。</p>

	<button
		onclick={login}
		class="mb-8 flex items-center space-x-3 rounded-full bg-black px-8 py-3 text-lg font-semibold
    text-white shadow-lg transition-transform hover:scale-105 hover:bg-gray-800"
	>
		<svg
			xmlns="http://www.w3.org/2000/svg"
			viewBox="0 0 1200 1227"
			fill="currentColor"
			class="h-6 w-6"
		>
			<path
				d="M745 561L1167 0H1064L698 482 389 0H0L455 704 0 1227H103L494 717 823 1227H1200L745 561ZM576 649L514 558 172 101H342L622 531 685 622 1041 1117H873L576 649Z"
			/>
		</svg>
		<span>Xでログイン</span>
	</button>
</main>
