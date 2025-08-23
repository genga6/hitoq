import { PUBLIC_API_BASE_URL } from "$env/static/public";

const API_BASE_URL = PUBLIC_API_BASE_URL;

export async function getCsrfToken(): Promise<string | null> {
  try {
    const response = await fetch(`${API_BASE_URL}/auth/csrf-token`, {
      method: "GET",
      credentials: "include", // Include cookies to set csrf_token cookie
    });

    if (!response.ok) {
      throw new Error(`CSRF token request failed: ${response.status}`);
    }

    const data = await response.json();
    return data.csrf_token;
  } catch (error) {
    console.error("CSRFトークンの取得に失敗しました:", error);
    return null;
  }
}

function getCsrfTokenFromCookie(): string | null {
  if (typeof document === "undefined") return null;

  const cookies = document.cookie.split(";");
  for (const cookie of cookies) {
    const [name, value] = cookie.trim().split("=");
    if (name === "csrf_token") {
      return value;
    }
  }
  return null;
}

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
  const headers = new Headers(options?.headers);

  if (
    options?.method &&
    ["POST", "PUT", "DELETE", "PATCH"].includes(options.method.toUpperCase())
  ) {
    const csrfToken = getCsrfTokenFromCookie();
    if (csrfToken) {
      headers.set("X-CSRFToken", csrfToken);
    }
  }

  let response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    credentials: "include", // Automatically set cookies
    headers,
  });

  // If 401 Unauthorized, try to refresh token once
  if (response.status === 401) {
    try {
      const refreshResponse = await fetch(
        `${API_BASE_URL}/auth/refresh-token`,
        {
          method: "POST",
          credentials: "include",
        },
      );

      if (refreshResponse.ok) {
        // Retry the original request
        response = await fetch(`${API_BASE_URL}${path}`, {
          ...options,
          credentials: "include",
          headers,
        });
      }
    } catch (refreshError) {
      console.debug("Token refresh failed:", refreshError);
    }
  }

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

export async function fetchApiWithCookies<T>(
  path: string,
  fetcher: typeof fetch,
  options?: RequestInit,
): Promise<T> {
  const headers = new Headers(options?.headers);

  if (
    options?.method &&
    ["POST", "PUT", "DELETE", "PATCH"].includes(options.method.toUpperCase())
  ) {
    try {
      const csrfResponse = await fetcher(`${API_BASE_URL}/auth/csrf-token`);
      if (csrfResponse.ok) {
        const csrfData = await csrfResponse.json();
        if (csrfData.csrf_token) {
          headers.set("X-CSRFToken", csrfData.csrf_token);
        }
      }
    } catch (error) {
      console.debug("Failed to get CSRF token for server-side request:", error);
    }
  }

  const response = await fetcher(`${API_BASE_URL}${path}`, {
    ...options,
    headers,
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
