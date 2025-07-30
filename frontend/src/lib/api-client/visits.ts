import { fetchApi, fetchApiWithAuth } from "./base";

// Visit related interfaces
export interface VisitorInfo {
  user_id?: string;
  user_name?: string;
  display_name?: string;
  icon_url?: string;
  is_anonymous: boolean;
}

export interface Visit {
  visit_id: number;
  visitor_user_id?: string;
  visited_user_id: string;
  is_anonymous: boolean;
  visited_at: string;
  visitor_info?: VisitorInfo;
}

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
