import type { LayoutServerLoad, LayoutServerLoadEvent } from "./$types";
import {
  getAuthenticatedUser,
  createAuthResponse,
} from "$lib/utils/auth-server";

export const load: LayoutServerLoad = async ({
  cookies,
  fetch,
}: LayoutServerLoadEvent) => {
  try {
    const user = await getAuthenticatedUser(cookies, fetch);
    return createAuthResponse(user);
  } catch (error) {
    console.error("認証状態の確認に失敗しました:", error);
    return createAuthResponse(null);
  }
};
