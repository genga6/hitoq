import { fetchApi, fetchApiWithAuth } from "./base";
import type { ProfileItem } from "$lib/types";

export const getProfileItems = async (
  userName: string,
): Promise<ProfileItem[]> => {
  return fetchApi<ProfileItem[]>(`/by-username/${userName}/profile-items`);
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
