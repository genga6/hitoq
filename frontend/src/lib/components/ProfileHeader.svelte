<script lang="ts">
  type Props = {
    displayName: string;
    iconUrl?: string;
    bio?: string;
    userName: string;
    isOwner?: boolean;
  };
  const { displayName, iconUrl, bio, userName, isOwner = false }: Props = $props();
</script>

<div class="relative flex items-start space-x-4">
  <img src={iconUrl} alt="User Icon" class="h-20 w-20 rounded-full border border-gray-300" />
  <div class="flex-1 {isOwner ? 'pr-12 sm:pr-16 lg:pr-20' : ''}">
    <h2 class="text-2xl font-bold text-gray-700">{displayName}</h2>

    {#if bio}
      <p class="mt-2 whitespace-pre-line text-gray-700">{bio}</p>
    {/if}
  </div>

  {#if isOwner}
    <!-- 付箋のような足跡ボタン -->
    <a 
      href="/{userName}/visits" 
      class="group absolute -top-1.5 -right-1.5 sm:-top-2 sm:-right-2 lg:-top-3 lg:-right-3 flex flex-col items-center space-y-0.5 sm:space-y-1 px-1.5 py-1 sm:px-2 sm:py-1.5 lg:px-3 lg:py-2.5 bg-gradient-to-br from-orange-100 to-orange-200 border-2 border-orange-300 text-orange-700 hover:from-orange-200 hover:to-orange-300 hover:border-orange-400 hover:text-orange-800 transform rotate-3 hover:rotate-0 transition-all duration-300 shadow-md hover:shadow-lg z-10"
      style="clip-path: polygon(0% 0%, 100% 0%, 100% 85%, 50% 100%, 0% 85%)"
      title="足跡を見る"
    >
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640" class="h-3 w-3 sm:h-4 sm:w-4 lg:h-5 lg:w-5 group-hover:scale-110 transition-transform duration-200">
        <path d="M298.5 156.9C312.8 199.8 298.2 243.1 265.9 253.7C233.6 264.3 195.8 238.1 181.5 195.2C167.2 152.3 181.8 109 214.1 98.4C246.4 87.8 284.2 114 298.5 156.9zM164.4 262.6C183.3 295 178.7 332.7 154.2 346.7C129.7 360.7 94.5 345.8 75.7 313.4C56.9 281 61.4 243.3 85.9 229.3C110.4 215.3 145.6 230.2 164.4 262.6zM133.2 465.2C185.6 323.9 278.7 288 320 288C361.3 288 454.4 323.9 506.8 465.2C510.4 474.9 512 485.3 512 495.7L512 497.3C512 523.1 491.1 544 465.3 544C453.8 544 442.4 542.6 431.3 539.8L343.3 517.8C328 514 312 514 296.7 517.8L208.7 539.8C197.6 542.6 186.2 544 174.7 544C148.9 544 128 523.1 128 497.3L128 495.7C128 485.3 129.6 474.9 133.2 465.2zM485.8 346.7C461.3 332.7 456.7 295 475.6 262.6C494.5 230.2 529.6 215.3 554.1 229.3C578.6 243.3 583.2 281 564.3 313.4C545.4 345.8 510.3 360.7 485.8 346.7zM374.1 253.7C341.8 243.1 327.2 199.8 341.5 156.9C355.8 114 393.6 87.8 425.9 98.4C458.2 109 472.8 152.3 458.5 195.2C444.2 238.1 406.4 264.3 374.1 253.7z"/>
      </svg>
    </a>
  {/if}
</div>
