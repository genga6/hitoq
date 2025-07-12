import type { PageServerLoad } from "./$types";
import { getBucketListPageData } from "$lib/api/client";
import { error } from "@sveltejs/kit";

export const load: PageServerLoad = async ({ params }) => {
  const userId = params.user_id;

  try {
    const { bucketListItems } = await getBucketListPageData(userId);
    return { bucketListItems };
  } catch (e) {
    console.error("Error loading bucket list items:", e);
    throw error(404, "バケットリストが見つかりませんでした");
  }
};
