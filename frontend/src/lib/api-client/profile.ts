import { fetchApi, fetchApiWithAuth } from "./base";
import type { Profile, ProfileItem } from "$lib/types";

export const getProfilePageData = async (
  userName: string,
): Promise<{ profile: Profile; profileItems: ProfileItem[] }> => {
  const data = await fetchApi<{
    profile: Profile;
    profileItems: ProfileItem[];
  }>(`/users/by-username/${userName}/profile`);
  return { profile: data.profile, profileItems: data.profileItems };
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
