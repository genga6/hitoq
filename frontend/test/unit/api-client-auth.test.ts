import { describe, it, expect, vi, beforeEach } from "vitest";
import {
  redirectToTwitterLogin,
  logout,
  getCurrentUser,
  refreshAccessToken,
  checkAuthStatus,
  deleteUser,
  getCurrentUserServer,
  refreshAccessTokenServer,
} from "$lib/api-client/auth";
import { fetchApiWithAuth, fetchApiWithCookies } from "$lib/api-client/base";

// Mock the base module
vi.mock("$lib/api-client/base", () => ({
  fetchApiWithAuth: vi.fn(),
  fetchApiWithCookies: vi.fn(),
  API_BASE_URL: "http://localhost:8000",
}));

// Mock console methods
const mockConsoleError = vi
  .spyOn(console, "error")
  .mockImplementation(() => {});

describe("Auth API Client", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockConsoleError.mockClear();

    // Mock window.location
    Object.defineProperty(window, "location", {
      value: { href: "" },
      writable: true,
    });

    // Mock document.cookie
    Object.defineProperty(document, "cookie", {
      value: "",
      writable: true,
    });
  });

  describe("redirectToTwitterLogin", () => {
    it("should redirect to Twitter login URL", () => {
      redirectToTwitterLogin();
      expect(window.location.href).toBe(
        "http://localhost:8000/auth/login/twitter",
      );
    });
  });

  describe("logout", () => {
    it("should logout successfully and redirect", async () => {
      vi.mocked(fetchApiWithAuth).mockResolvedValue(undefined);

      await logout();

      expect(fetchApiWithAuth).toHaveBeenCalledWith("/auth/logout", {
        method: "POST",
      });
      expect(window.location.href).toBe("/");
    });

    it("should handle logout error and clear cookies manually", async () => {
      vi.mocked(fetchApiWithAuth).mockRejectedValue(new Error("Logout failed"));

      await logout();

      expect(mockConsoleError).toHaveBeenCalledWith(
        "ログアウトに失敗しました:",
        expect.any(Error),
      );
      expect(window.location.href).toBe("/");
    });
  });

  describe("getCurrentUser", () => {
    it("should return user data on success", async () => {
      const mockUser = {
        id: "1",
        user_name: "testuser",
        display_name: "Test User",
      };
      vi.mocked(fetchApiWithAuth).mockResolvedValue(mockUser);

      const result = await getCurrentUser();

      expect(fetchApiWithAuth).toHaveBeenCalledWith("/auth/me", {
        method: "GET",
      });
      expect(result).toEqual(mockUser);
    });

    it("should return null on error", async () => {
      vi.mocked(fetchApiWithAuth).mockRejectedValue(new Error("Unauthorized"));

      const result = await getCurrentUser();

      expect(mockConsoleError).toHaveBeenCalledWith(
        "ユーザー情報の取得に失敗しました:",
        expect.any(Error),
      );
      expect(result).toBeNull();
    });
  });

  describe("refreshAccessToken", () => {
    it("should return true on successful refresh", async () => {
      vi.mocked(fetchApiWithAuth).mockResolvedValue(undefined);

      const result = await refreshAccessToken();

      expect(fetchApiWithAuth).toHaveBeenCalledWith("/auth/refresh-token", {
        method: "POST",
      });
      expect(result).toBe(true);
    });

    it("should return false on refresh error", async () => {
      vi.mocked(fetchApiWithAuth).mockRejectedValue(
        new Error("Refresh failed"),
      );

      const result = await refreshAccessToken();

      expect(mockConsoleError).toHaveBeenCalledWith(
        "トークンの更新に失敗しました:",
        expect.any(Error),
      );
      expect(result).toBe(false);
    });
  });

  describe("checkAuthStatus", () => {
    it("should return true when user exists", async () => {
      const mockUser = { id: "1", user_name: "testuser" };
      vi.mocked(fetchApiWithAuth).mockResolvedValue(mockUser);

      const result = await checkAuthStatus();

      expect(result).toBe(true);
    });

    it("should return false when user is null", async () => {
      vi.mocked(fetchApiWithAuth).mockRejectedValue(new Error("Unauthorized"));

      const result = await checkAuthStatus();

      expect(result).toBe(false);
    });
  });

  describe("deleteUser", () => {
    it("should delete user and clear cookies", async () => {
      vi.mocked(fetchApiWithAuth).mockResolvedValue(undefined);

      await deleteUser("user123");

      expect(fetchApiWithAuth).toHaveBeenCalledWith("/users/user123", {
        method: "DELETE",
      });
    });
  });

  describe("getCurrentUserServer", () => {
    it("should return user data on success", async () => {
      const mockUser = { id: "1", user_name: "testuser" };
      vi.mocked(fetchApiWithCookies).mockResolvedValue(mockUser);

      const result = await getCurrentUserServer("session=abc123");

      expect(fetchApiWithCookies).toHaveBeenCalledWith(
        "/auth/me",
        "session=abc123",
        {
          method: "GET",
        },
      );
      expect(result).toEqual(mockUser);
    });

    it("should return null on authentication error without logging", async () => {
      vi.mocked(fetchApiWithCookies).mockRejectedValue(
        new Error("Not authenticated"),
      );

      const result = await getCurrentUserServer("session=abc123");

      expect(result).toBeNull();
      expect(mockConsoleError).not.toHaveBeenCalled();
    });

    it("should return null on user not found without logging", async () => {
      vi.mocked(fetchApiWithCookies).mockRejectedValue(
        new Error("User not found"),
      );

      const result = await getCurrentUserServer("session=abc123");

      expect(result).toBeNull();
      expect(mockConsoleError).not.toHaveBeenCalled();
    });

    it("should return null and log unexpected errors", async () => {
      vi.mocked(fetchApiWithCookies).mockRejectedValue(
        new Error("Unexpected server error"),
      );

      const result = await getCurrentUserServer("session=abc123");

      expect(result).toBeNull();
      expect(mockConsoleError).toHaveBeenCalledWith(
        "サーバーサイドでのユーザー情報の取得に失敗しました:",
        expect.any(Error),
      );
    });
  });

  describe("refreshAccessTokenServer", () => {
    it("should return true on successful refresh", async () => {
      vi.mocked(fetchApiWithCookies).mockResolvedValue(undefined);

      const result = await refreshAccessTokenServer("session=abc123");

      expect(fetchApiWithCookies).toHaveBeenCalledWith(
        "/auth/refresh-token",
        "session=abc123",
        {
          method: "POST",
        },
      );
      expect(result).toBe(true);
    });

    it("should return false on user not found without logging", async () => {
      vi.mocked(fetchApiWithCookies).mockRejectedValue(
        new Error("User not found"),
      );

      const result = await refreshAccessTokenServer("session=abc123");

      expect(result).toBe(false);
      expect(mockConsoleError).not.toHaveBeenCalled();
    });

    it("should return false and log unexpected errors", async () => {
      vi.mocked(fetchApiWithCookies).mockRejectedValue(
        new Error("Server error"),
      );

      const result = await refreshAccessTokenServer("session=abc123");

      expect(result).toBe(false);
      expect(mockConsoleError).toHaveBeenCalledWith(
        "サーバーサイドでのトークン更新に失敗しました:",
        expect.any(Error),
      );
    });
  });
});
