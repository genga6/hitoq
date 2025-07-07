export const getBasicUserData = async (userId: string) => {
  const userName = userId === "gengaru_" ? "げんがる" : "ユーザー名";
  const userIconUrl = "https://via.placeholder.com/80";
  const bio =
    userId === "gengaru_"
      ? "探究心とエンタメ精神で今日も生きてます。"
      : "よろしくお願いします！";
  const loggedInUser = "gengaru_";
  const isOwner = loggedInUser === userId;

  return {
    userId,
    userName,
    userIconUrl,
    bio,
    isOwner,
  };
};
