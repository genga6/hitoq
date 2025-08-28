import { fetchApiWithAuth, fetchApiWithCookies, API_BASE_URL } from "./base";
import type { Profile } from "$lib/types";

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
  }
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
    await fetchApiWithAuth<void>("/auth/refresh-token", {
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

export const deleteUser = async (userId: string): Promise<void> => {
  await fetchApiWithAuth<void>(`/users/${userId}`, {
    method: "DELETE",
  });

  await logout();
};

// Server-side authentication APIs
export const getCurrentUserServer = async (fetcher: typeof fetch) => {
  try {
    const user = await fetchApiWithCookies<Profile>("/auth/me", fetcher, {
      method: "GET",
    });
    return user;
  } catch (error) {
    if (
      error instanceof Error &&
      (error.message.includes("Not authenticated") ||
        error.message.includes("User not found"))
    ) {
      return null;
    }
    console.error("サーバーサイドでのユーザー情報の取得に失敗しました:", error);
    return null;
  }
};

export const refreshAccessTokenServer = async (
  fetcher: typeof fetch,
): Promise<boolean> => {
  try {
    await fetchApiWithCookies<void>("/auth/refresh-token", fetcher, {
      method: "POST",
    });
    return true;
  } catch (error) {
    if (error instanceof Error && error.message.includes("User not found")) {
      return false;
    }
    console.error("サーバーサイドでのトークン更新に失敗しました:", error);
    return false;
  }
};
