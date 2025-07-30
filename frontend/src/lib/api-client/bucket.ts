import { fetchApi, fetchApiWithAuth } from "./base";
import type { Profile } from "$lib/types/profile";
import type { BucketListItem } from "$lib/types/bucket";

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
