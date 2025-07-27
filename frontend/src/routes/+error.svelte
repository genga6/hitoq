<script lang="ts">
	import { page } from '$app/state';
</script>

<div class="flex flex-col items-center justify-center px-4 py-24 text-center">
	<div class="max-w-md">
		<h1 class="text-6xl font-bold text-orange-400 drop-shadow-sm">
			{page.status}
		</h1>

		<p class="mt-4 text-3xl font-semibold text-gray-700">
			{page.error?.message ?? 'ページが見つかりません'}
		</p>

		<p class="mt-4 text-gray-600">
			お探しのページは存在しないか、移動または削除された可能性があります。
			URLに間違いがないかご確認ください。
		</p>

		<a
			href="/"
			class="mx-auto mt-8 block w-1/2 rounded-xl bg-orange-100 px-4 py-2 font-semibold text-orange-500 transition duration-200 hover:bg-orange-200 active:bg-orange-300"
		>
			トップページに戻る
		</a>
	</div>
</div>
