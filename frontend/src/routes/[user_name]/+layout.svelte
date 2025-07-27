<script lang="ts">
	import ProfileHeader from '$lib/components/ProfileHeader.svelte';
	import TabNavigation from '$lib/components/TabNavigation.svelte';
	import type { Snippet } from 'svelte';
	import type { BasePageData } from '$lib/types/page';

	type Props = {
		data: BasePageData;
		children?: Snippet;
	};
	let { data, children }: Props = $props();
</script>

<main class="flex min-h-screen justify-center bg-gray-100 p-4">
	<div class="w-full max-w-3xl space-y-6 rounded-2xl bg-white p-6 shadow-lg">
		{#if data.profile}
			<ProfileHeader
				displayName={data.profile.displayName}
				iconUrl={data.profile.iconUrl}
				bio={data.profile.bio}
			/>
			<TabNavigation userName={data.profile.userName} />
		{/if}
		{@render children?.()}
	</div>
</main>
