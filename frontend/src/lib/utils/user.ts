import type { Profile } from "$lib/types/profile";
import type { BasePageData } from "$lib/types/page";

// 開発用モック
export const getBasicUserData = async (
  userId: string,
): Promise<BasePageData> => {
  const userName = userId === "gengaru_" ? "げんがる" : "ユーザー名";
  const iconUrl = "https://via.placeholder.com/80";
  const bio =
    userId === "gengaru_"
      ? "探究心とエンタメ精神で今日も生きてます。"
      : "よろしくお願いします！";
  const loggedInUser = "gengaru_"; // 実際にはCookieなどから取得する
  const isOwner = loggedInUser === userId;

  const profile: Profile = {
    userId: userId,
    userName: userName,
    iconUrl: iconUrl,
    bio: bio,
    createdAt: new Date().toISOString(),
  };

  return {
    isOwner,
    profile,
  };
};
