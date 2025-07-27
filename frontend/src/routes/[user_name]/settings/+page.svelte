<script lang="ts">
	import type { PageData } from './$types';

	type Props = {
		data: PageData;
	};

	let { data }: Props = $props();
</script>

<div class="space-y-6">
	<h1 class="text-2xl font-bold text-gray-800">設定</h1>

	<div class="rounded-lg bg-gray-50 p-4">
		<p class="mb-2 text-sm text-gray-600">ログイン中のユーザー:</p>
		<p class="font-semibold">{data.profile.displayName} (@{data.profile.userName})</p>
	</div>

	<div class="py-8 text-center">
		<p class="text-lg text-gray-600">設定画面は現在開発中です</p>
		<p class="mt-2 text-sm text-gray-500">近日中に機能を追加予定です</p>
	</div>
</div>
