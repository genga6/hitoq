import { describe, it, expect, vi, beforeEach } from "vitest";
import {
  getUserByUserName,
  resolveUsersById,
  searchUsersByDisplayName,
  updateCurrentUser,
  discoverUsers,
} from "$lib/api-client/users";
import { fetchApi, fetchApiWithAuth } from "$lib/api-client/base";

// Mock the base module
vi.mock("$lib/api-client/base", () => ({
  fetchApi: vi.fn(),
  fetchApiWithAuth: vi.fn(),
}));

describe("Users API Client", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe("getUserByUserName", () => {
    it("should fetch user by username", async () => {
      const mockUser = {
        id: "1",
        user_name: "testuser",
        display_name: "Test User",
      };
      vi.mocked(fetchApi).mockResolvedValue(mockUser);

      const result = await getUserByUserName("testuser");

      expect(fetchApi).toHaveBeenCalledWith("/users/by-username/testuser");
      expect(result).toEqual(mockUser);
    });

    it("should throw error if user not found", async () => {
      vi.mocked(fetchApi).mockRejectedValue(new Error("User not found"));

      await expect(getUserByUserName("nonexistent")).rejects.toThrow(
        "User not found",
      );
    });
  });

  describe("resolveUsersById", () => {
    it("should resolve user and return array", async () => {
      const mockUser = { id: "1", user_name: "testuser" };
      vi.mocked(fetchApi).mockResolvedValue(mockUser);

      const result = await resolveUsersById("testuser");

      expect(fetchApi).toHaveBeenCalledWith(
        "/users/resolve-users-id?user_name=testuser",
      );
      expect(result).toEqual([mockUser]);
    });

    it("should return empty array on error", async () => {
      vi.mocked(fetchApi).mockRejectedValue(new Error("Not found"));

      const result = await resolveUsersById("nonexistent");

      expect(result).toEqual([]);
    });

    it("should properly encode username in URL", async () => {
      const mockUser = { id: "1", user_name: "test@user" };
      vi.mocked(fetchApi).mockResolvedValue(mockUser);

      await resolveUsersById("test@user");

      expect(fetchApi).toHaveBeenCalledWith(
        "/users/resolve-users-id?user_name=test%40user",
      );
    });
  });

  describe("searchUsersByDisplayName", () => {
    it("should search users with default limit", async () => {
      const mockUsers = [
        { id: "1", user_name: "user1" },
        { id: "2", user_name: "user2" },
      ];
      vi.mocked(fetchApi).mockResolvedValue(mockUsers);

      const result = await searchUsersByDisplayName("test");

      expect(fetchApi).toHaveBeenCalledWith(
        "/users/search/users?q=test&limit=10",
      );
      expect(result).toEqual(mockUsers);
    });

    it("should search users with custom limit", async () => {
      const mockUsers = [{ id: "1", user_name: "user1" }];
      vi.mocked(fetchApi).mockResolvedValue(mockUsers);

      const result = await searchUsersByDisplayName("test", 5);

      expect(fetchApi).toHaveBeenCalledWith(
        "/users/search/users?q=test&limit=5",
      );
      expect(result).toEqual(mockUsers);
    });

    it("should return empty array on error", async () => {
      vi.mocked(fetchApi).mockRejectedValue(new Error("Search failed"));

      const result = await searchUsersByDisplayName("test");

      expect(result).toEqual([]);
    });

    it("should properly encode search query", async () => {
      vi.mocked(fetchApi).mockResolvedValue([]);

      await searchUsersByDisplayName("test query with spaces");

      expect(fetchApi).toHaveBeenCalledWith(
        "/users/search/users?q=test%20query%20with%20spaces&limit=10",
      );
    });
  });

  describe("updateCurrentUser", () => {
    it("should update current user with provided data", async () => {
      const updateData = { display_name: "New Name", bio: "New bio" };
      const updatedUser = {
        id: "1",
        user_name: "testuser",
        display_name: "New Name",
        bio: "New bio",
      };
      vi.mocked(fetchApiWithAuth).mockResolvedValue(updatedUser);

      const result = await updateCurrentUser(updateData);

      expect(fetchApiWithAuth).toHaveBeenCalledWith("/users/me", {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(updateData),
      });
      expect(result).toEqual(updatedUser);
    });

    it("should throw error on update failure", async () => {
      const updateData = { display_name: "New Name" };
      vi.mocked(fetchApiWithAuth).mockRejectedValue(new Error("Update failed"));

      await expect(updateCurrentUser(updateData)).rejects.toThrow(
        "Update failed",
      );
    });
  });

  describe("discoverUsers", () => {
    it("should discover users with default parameters", async () => {
      const mockUsers = [
        { id: "1", user_name: "user1" },
        { id: "2", user_name: "user2" },
      ];
      vi.mocked(fetchApiWithAuth).mockResolvedValue(mockUsers);

      const result = await discoverUsers();

      expect(fetchApiWithAuth).toHaveBeenCalledWith(
        "/users/discover?type=recommend&limit=10&offset=0",
      );
      expect(result).toEqual(mockUsers);
    });

    it("should discover users with activity type", async () => {
      const mockUsers = [{ id: "1", user_name: "active_user" }];
      vi.mocked(fetchApiWithAuth).mockResolvedValue(mockUsers);

      const result = await discoverUsers("activity");

      expect(fetchApiWithAuth).toHaveBeenCalledWith(
        "/users/discover?type=activity&limit=10&offset=0",
      );
      expect(result).toEqual(mockUsers);
    });

    it("should discover users with random type", async () => {
      const mockUsers = [{ id: "1", user_name: "random_user" }];
      vi.mocked(fetchApiWithAuth).mockResolvedValue(mockUsers);

      const result = await discoverUsers("random");

      expect(fetchApiWithAuth).toHaveBeenCalledWith(
        "/users/discover?type=random&limit=10&offset=0",
      );
      expect(result).toEqual(mockUsers);
    });

    it("should discover users with custom limit and offset", async () => {
      const mockUsers = [{ id: "1", user_name: "user1" }];
      vi.mocked(fetchApiWithAuth).mockResolvedValue(mockUsers);

      const result = await discoverUsers("recommend", 5, 10);

      expect(fetchApiWithAuth).toHaveBeenCalledWith(
        "/users/discover?type=recommend&limit=5&offset=10",
      );
      expect(result).toEqual(mockUsers);
    });

    it.skip("should return empty array on error", async () => {
      vi.mocked(fetchApiWithAuth).mockRejectedValueOnce(
        new Error("Discover failed"),
      );

      const result = await discoverUsers();

      expect(fetchApiWithAuth).toHaveBeenCalledWith(
        "/users/discover?type=recommend&limit=10&offset=0",
      );
      expect(result).toEqual([]);
    });
  });

  // Test URL parameter encoding edge cases
  describe("URL encoding", () => {
    it("should properly encode special characters in resolveUsersById", async () => {
      vi.mocked(fetchApi).mockResolvedValue({ id: "1", user_name: "test" });

      await resolveUsersById("user@domain.com");

      expect(fetchApi).toHaveBeenCalledWith(
        "/users/resolve-users-id?user_name=user%40domain.com",
      );
    });

    it("should properly encode special characters in searchUsersByDisplayName", async () => {
      vi.mocked(fetchApi).mockResolvedValue([]);

      await searchUsersByDisplayName("name with spaces & symbols");

      expect(fetchApi).toHaveBeenCalledWith(
        "/users/search/users?q=name%20with%20spaces%20%26%20symbols&limit=10",
      );
    });
  });

  // Test boundary conditions
  describe("boundary conditions", () => {
    it("should handle empty search query", async () => {
      vi.mocked(fetchApi).mockResolvedValue([]);

      const result = await searchUsersByDisplayName("");

      expect(fetchApi).toHaveBeenCalledWith("/users/search/users?q=&limit=10");
      expect(result).toEqual([]);
    });

    it("should handle zero limit in discoverUsers", async () => {
      vi.mocked(fetchApiWithAuth).mockResolvedValue([]);

      const result = await discoverUsers("recommend", 0, 0);

      expect(fetchApiWithAuth).toHaveBeenCalledWith(
        "/users/discover?type=recommend&limit=0&offset=0",
      );
      expect(result).toEqual([]);
    });
  });
});
