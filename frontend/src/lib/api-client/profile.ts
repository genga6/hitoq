import { fetchApi, fetchApiWithAuth } from "./base";
import type { Profile, ProfileItem, UserUpdate } from "$lib/types";

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
  itemId: string,
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
  itemId: string,
): Promise<void> => {
  await fetchApiWithAuth<void>(`/users/${userId}/profile-items/${itemId}`, {
    method: "DELETE",
  });
};

// User APIs
export const updateUser = async (
  userId: string,
  userData: UserUpdate,
): Promise<Profile> => {
  return fetchApiWithAuth<Profile>(`/users/me`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(userData),
  });
};
