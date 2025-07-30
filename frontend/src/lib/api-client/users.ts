import { fetchApi } from "./base";
import type { Profile, UserCandidate } from "$lib/types/profile";

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

export const searchUsersByDisplayName = async (
  query: string,
  limit: number = 10,
): Promise<UserCandidate[]> => {
  try {
    const users = await fetchApi<UserCandidate[]>(
      `/users/search/users?q=${encodeURIComponent(query)}&limit=${limit}`,
    );
    return users;
  } catch {
    return [];
  }
};
