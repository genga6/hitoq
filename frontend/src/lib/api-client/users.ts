import { fetchApi, fetchApiWithAuth } from "./base";
import type { Profile, UserCandidate, UserUpdate } from "$lib/types";

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

export const updateCurrentUser = async (
  userUpdate: UserUpdate,
): Promise<Profile> => {
  return fetchApiWithAuth("/users/me", {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(userUpdate),
  });
};

export const discoverUsers = async (
  type: "activity" | "random" | "recommend" = "recommend",
  limit: number = 10,
  offset: number = 0,
): Promise<Profile[]> => {
  const params = new URLSearchParams({
    type,
    limit: limit.toString(),
    offset: offset.toString(),
  });

  try {
    return fetchApiWithAuth<Profile[]>(`/users/discover?${params.toString()}`);
  } catch {
    return [];
  }
};
