<script lang="ts">
	import { goto } from '$app/navigation';
	import { redirectToTwitterLogin } from '$lib/api-client/auth';
	import type { PageData } from './$types';

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
	<!-- Hero Section -->
	<section class="w-full max-w-4xl text-center">
		<h1
			class="mb-8 bg-gradient-to-r from-orange-500 to-amber-500 bg-clip-text text-5xl font-extrabold text-transparent md:text-6xl"
		>
			hitoQ
		</h1>
		<p class="theme-text-primary mb-6 text-xl font-semibold md:text-2xl">「あの人、どんな人？」から「友達」に。</p>
		<p class="theme-text-muted mx-auto mb-8 max-w-2xl text-base leading-relaxed md:text-lg">
			人との関係は、相手を「知る」ことから始まります。<br>
			hitoQは、Q&Aを通じてあなたの内面が伝えるプロフィールサービスです。<br>
			気になる相手の新たな一面を見つけたり、あなたの魅力を伝えることで、<br>
			新しいつながりを生み出します。
		</p>
	</section>

	<!-- Features Section -->
	<section class="container-responsive mb-8 grid max-w-5xl gap-6 sm:grid-cols-2 md:mb-12 md:gap-8 lg:grid-cols-3">
		<div class="card text-center">
			<div class="card-body">
				<div class="mb-4 flex justify-center">
					<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="h-10 w-10 text-orange-500">
						<path stroke-linecap="round" stroke-linejoin="round" d="m16.862 4.487 1.687-1.688a1.875 1.875 0 1 1 2.652 2.652L10.582 16.07a4.5 4.5 0 0 1-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 0 1 1.13-1.897l8.932-8.931Zm0 0L19.5 7.125M18 14v4.75A2.25 2.25 0 0 1 15.75 21H5.25A2.25 2.25 0 0 1 3 18.75V8.25A2.25 2.25 0 0 1 5.25 6H10" />
					</svg>
				</div>
				<h3 class="theme-text-primary mb-2 text-lg font-semibold md:text-xl">自己紹介</h3>
				<p class="theme-text-subtle text-sm md:text-base">
					用意された質問に答えるだけで、あなたの価値観や興味を伝えるプロフィールが完成します。
				</p>
			</div>
		</div>

		<div class="card text-center">
			<div class="card-body">
				<div class="mb-4 flex justify-center">
					<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="h-10 w-10 text-orange-500">
						<path stroke-linecap="round" stroke-linejoin="round" d="M7.5 8.25h9m-9 3H12m-9.75 1.51c0 1.6 1.123 2.994 2.707 3.227 1.129.166 2.27.293 3.423.379.35.026.67.21.865.501L12 21l2.755-4.133a1.14 1.14 0 0 1 .865-.501 48.172 48.172 0 0 0 3.423-.379c1.584-.233 2.707-1.626 2.707-3.228V6.741c0-1.602-1.123-2.995-2.707-3.228A48.394 48.394 0 0 0 12 3c-2.392 0-4.744.175-7.043.513C3.373 3.746 2.25 5.14 2.25 6.741v6.018Z" />
					</svg>
				</div>
				<h3 class="theme-text-primary mb-2 text-lg font-semibold md:text-xl">トーク</h3>
				<p class="theme-text-subtle text-sm md:text-base">
					気になる相手のプロフィールにコメントを残し、スレッド形式で会話を深めることができます。
				</p>
			</div>
		</div>

		<div class="card text-center sm:col-span-2 lg:col-span-1">
			<div class="card-body">
				<div class="mb-4 flex justify-center">
					<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="h-10 w-10 text-orange-500">
						<path stroke-linecap="round" stroke-linejoin="round" d="M15 19.128a9.38 9.38 0 0 0 2.625.372 9.337 9.337 0 0 0 4.121-.952 4.125 4.125 0 0 0-7.533-2.493M15 19.128v-.003c0-1.113-.285-2.16-.786-3.07M15 19.128v.106A12.318 12.318 0 0 1 8.624 21c-2.331 0-4.512-.645-6.374-1.766l-.001-.109a6.375 6.375 0 0 1 11.964-3.07M12 6.375a3.375 3.375 0 1 1-6.75 0 3.375 3.375 0 0 1 6.75 0Zm8.25 2.25a2.625 2.625 0 1 1-5.25 0 2.625 2.625 0 0 1 5.25 0Z" />
					</svg>
				</div>
				<h3 class="theme-text-primary mb-2 text-lg font-semibold md:text-xl">新しいつながり</h3>
				<p class="theme-text-subtle text-sm md:text-base">
					興味や価値観が近いユーザーを見つけて、新たな交流を始めましょう。思わぬ共通点が見つかるかも。
				</p>
			</div>
		</div>
	</section>

	<!-- Call to Action -->
	<section class="flex w-full flex-col items-center text-center">
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
			<span>Xでログインして始める</span>
		</button>
	</section>
</main>