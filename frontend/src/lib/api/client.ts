import { PUBLIC_API_BASE_URL } from "$env/static/public";
import type { Profile, ProfileItem, UserCandidate } from "$lib/types/profile";
import type { BucketListItem } from "$lib/types/bucket";
import type {
  Question,
  Answer,
  UserAnswerGroup,
  QATemplate,
} from "$lib/types/qna";

const API_BASE_URL = PUBLIC_API_BASE_URL;

async function fetchApi<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, options);
  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || "API request failed");
  }
  return response.json();
}

async function fetchApiWithAuth<T>(
  path: string,
  options?: RequestInit,
): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    credentials: "include", // Cookieを自動的に送信
  });
  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || "API request failed");
  }
  return response.json();
}

// サーバーサイド用のfetch関数（Cookieを手動で渡す）
async function fetchApiWithCookies<T>(
  path: string,
  cookieHeader: string,
  options?: RequestInit,
): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      ...options?.headers,
      Cookie: cookieHeader,
    },
  });
  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || "API request failed");
  }
  return response.json();
}

// User related APIs
export const getUserByUserName = async (userName: string): Promise<Profile> => {
  return fetchApi<Profile>(`/users/by-username/${userName}`);
};

export const resolveUsersById = async (
  userName: string,
): Promise<UserCandidate[]> => {
  try {
    const user = await fetchApi<UserCandidate>(
      `/users/resolve-users-id?user_name=${encodeURIComponent(userName)}`,
    );
    return [user];
  } catch {
    return [];
  }
};

// Profile Page Data
// TODO: タブによる画面遷移のたびに、サーバーにリクエストを送る仕様を再検討する（キャッシュなど？）
export const getProfilePageData = async (
  userName: string,
): Promise<{ profile: Profile; profileItems: ProfileItem[] }> => {
  const data = await fetchApi<{
    profile: Profile;
    profileItems: ProfileItem[];
  }>(`/users/by-username/${userName}/profile`);
  return { profile: data.profile, profileItems: data.profileItems };
};

// Bucket List Page Data
export const getBucketListPageData = async (
  userName: string,
): Promise<{ profile: Profile; bucketListItems: BucketListItem[] }> => {
  const data = await fetchApi<{
    profile: Profile;
    bucketListItems: BucketListItem[];
  }>(`/users/by-username/${userName}/bucket-list`);
  return { profile: data.profile, bucketListItems: data.bucketListItems };
};

// Q&A Page Data
export const getQnAPageData = async (
  userName: string,
): Promise<{
  profile: Profile;
  userAnswerGroups: UserAnswerGroup[];
  availableTemplates: QATemplate[];
}> => {
  const data = await fetchApi<{
    profile: Profile;
    userAnswerGroups: UserAnswerGroup[];
    availableTemplates: QATemplate[];
  }>(`/users/by-username/${userName}/qna`);
  return {
    profile: data.profile,
    userAnswerGroups: data.userAnswerGroups,
    availableTemplates: data.availableTemplates,
  };
};

// Profile Item APIs
export const createProfileItem = async (
  userId: string,
  item: Partial<ProfileItem>,
): Promise<ProfileItem> => {
  return fetchApiWithAuth<ProfileItem>(`/users/${userId}/profile-items`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(item),
  });
};

export const updateProfileItem = async (
  userId: string,
  itemId: number,
  item: Partial<ProfileItem>,
): Promise<ProfileItem> => {
  return fetchApiWithAuth<ProfileItem>(
    `/users/${userId}/profile-items/${itemId}`,
    {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(item),
    },
  );
};

export const deleteProfileItem = async (
  userId: string,
  itemId: number,
): Promise<void> => {
  await fetchApiWithAuth<void>(`/users/${userId}/profile-items/${itemId}`, {
    method: "DELETE",
  });
};

// Bucket List Item APIs
export const createBucketListItem = async (
  userId: string,
  item: Partial<BucketListItem>,
): Promise<BucketListItem> => {
  return fetchApiWithAuth<BucketListItem>(
    `/users/${userId}/bucket-list-items`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(item),
    },
  );
};

export const updateBucketListItem = async (
  userId: string,
  itemId: number,
  item: Partial<BucketListItem>,
): Promise<BucketListItem> => {
  return fetchApiWithAuth<BucketListItem>(
    `/users/${userId}/bucket-list-items/${itemId}`,
    {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(item),
    },
  );
};

export const deleteBucketListItem = async (
  userId: string,
  itemId: number,
): Promise<void> => {
  await fetchApiWithAuth<void>(`/users/${userId}/bucket-list-items/${itemId}`, {
    method: "DELETE",
  });
};

// Q&A APIs
export const createAnswer = async (
  userId: string,
  questionId: number,
  answerText: string,
): Promise<Answer> => {
  return fetchApiWithAuth<Answer>(
    `/users/${userId}/questions/${questionId}/answers`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ answer_text: answerText }),
    },
  );
};

export const getAllQuestions = async (): Promise<Question[]> => {
  return fetchApi<Question[]>(`/users/questions`);
};

// Authentication APIs
export const redirectToTwitterLogin = () => {
  window.location.href = `${API_BASE_URL}/auth/login/twitter`;
};

export const logout = async () => {
  try {
    await fetchApiWithAuth<void>("/auth/logout", {
      method: "POST",
    });
  } catch (error) {
    console.error("ログアウトに失敗しました:", error);
    // Manual cookie deletion as fallback
    document.cookie =
      "access_token=; path=/; expires=Thu, 01 Jan 1970 00:00:01 GMT";
    document.cookie =
      "refresh_token=; path=/; expires=Thu, 01 Jan 1970 00:00:01 GMT";
  }
  // ページリロードの代わりにリダイレクトを使用
  window.location.href = "/";
};

export const getCurrentUser = async () => {
  try {
    const user = await fetchApiWithAuth<Profile>("/auth/me", {
      method: "GET",
    });
    return user;
  } catch (error) {
    console.error("ユーザー情報の取得に失敗しました:", error);
    return null;
  }
};

export const refreshAccessToken = async (): Promise<boolean> => {
  try {
    await fetchApiWithAuth<void>("/auth/refresh", {
      method: "POST",
    });
    return true;
  } catch (error) {
    console.error("トークンの更新に失敗しました:", error);
    return false;
  }
};

export const checkAuthStatus = async (): Promise<boolean> => {
  const user = await getCurrentUser();
  return user !== null;
};

// Server-side authentication APIs
export const getCurrentUserServer = async (cookieHeader: string) => {
  try {
    const user = await fetchApiWithCookies<Profile>("/auth/me", cookieHeader, {
      method: "GET",
    });
    return user;
  } catch (error) {
    // 認証エラーは正常な状態なので、詳細なログは出力しない
    if (error instanceof Error && error.message.includes("Not authenticated")) {
      return null;
    }
    // 予期しないエラーの場合のみログを出力
    console.error("サーバーサイドでのユーザー情報の取得に失敗しました:", error);
    return null;
  }
};

export const refreshAccessTokenServer = async (
  cookieHeader: string,
): Promise<boolean> => {
  try {
    await fetchApiWithCookies<void>("/auth/refresh", cookieHeader, {
      method: "POST",
    });
    return true;
  } catch (error) {
    console.error("サーバーサイドでのトークン更新に失敗しました:", error);
    return false;
  }
};
