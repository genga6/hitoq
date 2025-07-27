<script lang="ts">
	type Props = {
		displayName: string;
		iconUrl?: string;
		bio?: string;
	};
	const { displayName, iconUrl, bio }: Props = $props();
</script>

<div class="flex items-start space-x-4">
	<img src={iconUrl} alt="User Icon" class="h-20 w-20 rounded-full border border-gray-300" />
	<div>
		<h2 class="text-2xl font-bold text-gray-700">{displayName}</h2>

		{#if bio}
			<p class="mt-2 whitespace-pre-line text-gray-700">{bio}</p>
		{/if}
	</div>
</div>
