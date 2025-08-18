import { describe, it, expect, vi, beforeEach } from "vitest";
import {
  fetchApi,
  fetchApiWithAuth,
  fetchApiWithCookies,
  API_BASE_URL,
} from "$lib/api-client/base";

// Mock environment variables
vi.mock("$env/static/public", () => ({
  PUBLIC_API_BASE_URL: "http://localhost:8000",
}));

describe("API Client Base", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    // Reset fetch mock
    global.fetch = vi.fn();
  });

  describe("fetchApi", () => {
    it("should make successful GET request", async () => {
      const mockData = { id: 1, name: "test" };
      const mockResponse = {
        ok: true,
        json: vi.fn().mockResolvedValue(mockData),
      };

      global.fetch = vi.fn().mockResolvedValue(mockResponse);

      const result = await fetchApi<typeof mockData>("/test");

      expect(global.fetch).toHaveBeenCalledWith(
        "http://localhost:8000/test",
        undefined,
      );
      expect(result).toEqual(mockData);
    });

    it("should make successful POST request with data", async () => {
      const mockData = { success: true };
      const mockResponse = {
        ok: true,
        json: vi.fn().mockResolvedValue(mockData),
      };

      global.fetch = vi.fn().mockResolvedValue(mockResponse);

      const postData = { name: "test" };
      const result = await fetchApi<typeof mockData>("/test", {
        method: "POST",
        body: JSON.stringify(postData),
      });

      expect(global.fetch).toHaveBeenCalledWith("http://localhost:8000/test", {
        method: "POST",
        body: JSON.stringify(postData),
      });
      expect(result).toEqual(mockData);
    });

    it("should throw error on failed request", async () => {
      const errorData = { detail: "Not found" };
      const mockResponse = {
        ok: false,
        json: vi.fn().mockResolvedValue(errorData),
      };

      global.fetch = vi.fn().mockResolvedValue(mockResponse);

      await expect(fetchApi("/test")).rejects.toThrow("Not found");
      expect(global.fetch).toHaveBeenCalledWith(
        "http://localhost:8000/test",
        undefined,
      );
    });

    it("should throw generic error when detail is not provided", async () => {
      const errorData = {};
      const mockResponse = {
        ok: false,
        json: vi.fn().mockResolvedValue(errorData),
      };

      global.fetch = vi.fn().mockResolvedValue(mockResponse);

      await expect(fetchApi("/test")).rejects.toThrow("API request failed");
    });
  });

  describe("fetchApiWithAuth", () => {
    it("should make successful authenticated request", async () => {
      const mockData = { id: 1, name: "authenticated" };
      const mockResponse = {
        ok: true,
        status: 200,
        json: vi.fn().mockResolvedValue(mockData),
      };

      global.fetch = vi.fn().mockResolvedValue(mockResponse);

      const result = await fetchApiWithAuth<typeof mockData>("/auth-test");

      expect(global.fetch).toHaveBeenCalledWith(
        "http://localhost:8000/auth-test",
        {
          credentials: "include",
        },
      );
      expect(result).toEqual(mockData);
    });

    it("should handle 204 No Content response", async () => {
      const mockResponse = {
        ok: true,
        status: 204,
        json: vi.fn(),
      };

      global.fetch = vi.fn().mockResolvedValue(mockResponse);

      const result = await fetchApiWithAuth<void>("/delete-test", {
        method: "DELETE",
      });

      expect(global.fetch).toHaveBeenCalledWith(
        "http://localhost:8000/delete-test",
        {
          method: "DELETE",
          credentials: "include",
        },
      );
      expect(result).toBeUndefined();
      expect(mockResponse.json).not.toHaveBeenCalled();
    });

    it("should merge options with credentials", async () => {
      const mockData = { success: true };
      const mockResponse = {
        ok: true,
        status: 200,
        json: vi.fn().mockResolvedValue(mockData),
      };

      global.fetch = vi.fn().mockResolvedValue(mockResponse);

      await fetchApiWithAuth("/test", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
      });

      expect(global.fetch).toHaveBeenCalledWith("http://localhost:8000/test", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
      });
    });
  });

  describe("fetchApiWithCookies", () => {
    it("should make successful request with cookies", async () => {
      const mockData = { server: true };
      const mockResponse = {
        ok: true,
        status: 200,
        text: vi.fn().mockResolvedValue(JSON.stringify(mockData)),
      };

      global.fetch = vi.fn().mockResolvedValue(mockResponse);

      const cookieHeader = "session=abc123; user=test";
      const result = await fetchApiWithCookies<typeof mockData>(
        "/server-test",
        cookieHeader,
      );

      expect(global.fetch).toHaveBeenCalledWith(
        "http://localhost:8000/server-test",
        {
          headers: {
            Cookie: cookieHeader,
          },
        },
      );
      expect(result).toEqual(mockData);
    });

    it("should handle 204 No Content response", async () => {
      const mockResponse = {
        ok: true,
        status: 204,
        text: vi.fn().mockResolvedValue(""),
      };

      global.fetch = vi.fn().mockResolvedValue(mockResponse);

      const result = await fetchApiWithCookies<void>(
        "/delete",
        "session=abc123",
      );

      expect(result).toBeUndefined();
    });

    it("should throw error on failed request with JSON error", async () => {
      const errorData = { detail: "Server error" };
      const mockResponse = {
        ok: false,
        status: 500,
        text: vi.fn().mockResolvedValue(JSON.stringify(errorData)),
      };

      global.fetch = vi.fn().mockResolvedValue(mockResponse);

      await expect(
        fetchApiWithCookies("/test", "session=abc123"),
      ).rejects.toThrow("Server error");
    });

    it("should throw error on failed request with HTML error", async () => {
      const htmlError = "<html><body>Internal Server Error</body></html>";
      const mockResponse = {
        ok: false,
        status: 500,
        text: vi.fn().mockResolvedValue(htmlError),
      };

      global.fetch = vi.fn().mockResolvedValue(mockResponse);

      await expect(
        fetchApiWithCookies("/test", "session=abc123"),
      ).rejects.toThrow("API request failed with status 500");
    });

    it("should throw error on invalid JSON response", async () => {
      const invalidJson = "not json";
      const mockResponse = {
        ok: true,
        status: 200,
        text: vi.fn().mockResolvedValue(invalidJson),
      };

      global.fetch = vi.fn().mockResolvedValue(mockResponse);

      await expect(
        fetchApiWithCookies("/test", "session=abc123"),
      ).rejects.toThrow("Failed to parse JSON response");
    });

    it("should merge custom headers with Cookie header", async () => {
      const mockData = { success: true };
      const mockResponse = {
        ok: true,
        status: 200,
        text: vi.fn().mockResolvedValue(JSON.stringify(mockData)),
      };

      global.fetch = vi.fn().mockResolvedValue(mockResponse);

      await fetchApiWithCookies("/test", "session=abc123", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Custom": "value",
        },
      });

      expect(global.fetch).toHaveBeenCalledWith("http://localhost:8000/test", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Custom": "value",
          Cookie: "session=abc123",
        },
      });
    });
  });

  describe("API_BASE_URL", () => {
    it("should export the correct base URL", () => {
      expect(API_BASE_URL).toBe("http://localhost:8000");
    });
  });
});
