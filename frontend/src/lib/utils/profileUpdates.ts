import type { ProfileItem, Profile } from "$lib/types";

export const updateProfileItemValue = async (
  userId: string,
  profileItemId: string,
  newValue: string,
): Promise<ProfileItem> => {
  const { updateProfileItem } = await import("$lib/api-client/profile");
  return updateProfileItem(userId, profileItemId, { value: newValue });
};

export const updateUserSelfIntroduction = async (
  userId: string,
  selfIntroduction: string,
): Promise<Profile> => {
  const { updateUser } = await import("$lib/api-client/profile");
  return updateUser(userId, { selfIntroduction });
};
