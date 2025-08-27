import { fetchApi, fetchApiWithAuth, fetchApiWithCookies } from "./base";
import type { Visit } from "$lib/types/visits";

export const recordVisit = async (userId: string): Promise<void> => {
  await fetchApiWithAuth<void>(`/users/${userId}/visit`, {
    method: "POST",
  });
};

export const getUserVisits = async (
  userId: string,
  limit: number = 50,
): Promise<Visit[]> => {
  return fetchApi<Visit[]>(`/users/${userId}/visits?limit=${limit}`);
};

export const updateVisitsVisibility = async (
  userId: string,
  visible: boolean,
): Promise<void> => {
  await fetchApiWithAuth<void>(`/users/${userId}/visits-visibility`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ visible }),
  });
};

export const getVisitsVisibility = async (
  userId: string,
): Promise<{ visible: boolean }> => {
  return fetchApiWithAuth<{ visible: boolean }>(
    `/users/${userId}/visits-visibility`,
  );
};

// Server-side visit recording
export const recordVisitServer = async (
  userId: string,
  fetcher: typeof fetch,
): Promise<void> => {
  await fetchApiWithCookies<void>(`/users/${userId}/visit`, fetcher, {
    method: "POST",
  });
};
