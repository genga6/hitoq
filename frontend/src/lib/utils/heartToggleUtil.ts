import { toggleHeartReaction } from "$lib/api-client/messages";
import { invalidate } from "$app/navigation";
import { toasts } from "$lib/stores/toast";

export async function handleHeartToggleLogic(
  messageId: string,
  currentUser: { userId: string; userName: string; displayName: string } | null,
  currentLiked: boolean,
  setLiked: (liked: boolean) => void,
  currentCount: number,
  setCount: (count: number) => void,
  isToggling: boolean,
  setIsToggling: (isToggling: boolean) => void,
  invalidateId: string,
) {
  if (!currentUser || isToggling) return;

  setIsToggling(true);

  const wasLiked = currentLiked;
  const previousCount = currentCount;

  setLiked(!currentLiked);
  setCount(currentLiked ? Math.max(0, currentCount - 1) : currentCount + 1);

  try {
    const result = await toggleHeartReaction(messageId);

    setLiked(result.userLiked);
    setCount(result.likeCount);

    await invalidate(invalidateId);

    if (result.userLiked) {
      toasts.success("いいねしました！");
    } else {
      toasts.info("いいねを取り消しました。");
    }
  } catch (error) {
    console.error("Failed to toggle heart:", error);
    setLiked(wasLiked);
    setCount(previousCount);
    toasts.error("いいねの操作に失敗しました。");
  } finally {
    setIsToggling(false);
  }
}
