import { PUBLIC_API_BASE_URL } from "$env/static/public";

const API_BASE_URL = PUBLIC_API_BASE_URL;

export async function fetchApi<T>(
  path: string,
  options?: RequestInit,
): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, options);
  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || "API request failed");
  }
  return response.json();
}

export async function fetchApiWithAuth<T>(
  path: string,
  options?: RequestInit,
): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    credentials: "include", // Automatically set cookies
  });
  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || "API request failed");
  }

  // No need to parse JSON if the response is empty (204 No Content (e.g. user deletion))
  if (response.status === 204) {
    return undefined as T;
  }

  return response.json();
}

// サーバーサイド用のfetch関数（Cookieを手動で渡す）
export async function fetchApiWithCookies<T>(
  path: string,
  cookieHeader: string,
  options?: RequestInit,
): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      ...options?.headers,
      Cookie: cookieHeader,
    },
  });

  // No need to parse JSON if the response is empty (204 No Content)
  if (response.status === 204) {
    return undefined as T;
  }

  // Read the response body once
  const responseText = await response.text();

  if (!response.ok) {
    let errorData;
    try {
      errorData = JSON.parse(responseText);
    } catch {
      // JSON parse error, likely HTML error page
      throw new Error(
        `API request failed with status ${response.status}: ${responseText}`,
      );
    }
    throw new Error(errorData.detail || "API request failed");
  }

  try {
    return JSON.parse(responseText);
  } catch {
    throw new Error(`Failed to parse JSON response: ${responseText}`);
  }
}

export { API_BASE_URL };
