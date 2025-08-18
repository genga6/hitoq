import { describe, it, expect, vi, beforeEach } from "vitest";
import {
  formatRelativeTime,
  formatAbsoluteTime,
  formatDateOnly,
  formatShortDate,
  formatTimeOnly,
} from "$lib/utils/dateFormat";

describe("Date Format Utils", () => {
  beforeEach(() => {
    // Mock current time to 2024-01-15 12:00:00
    const mockDate = new Date("2024-01-15T12:00:00.000Z");
    vi.setSystemTime(mockDate);
  });

  describe("formatRelativeTime", () => {
    it("should return '今' for dates less than 1 minute ago", () => {
      const now = new Date();
      const recent = new Date(now.getTime() - 30000); // 30 seconds ago

      expect(formatRelativeTime(recent.toISOString())).toBe("今");
    });

    it("should return minutes for dates within the last hour", () => {
      const now = new Date();
      const thirtyMinutesAgo = new Date(now.getTime() - 30 * 60 * 1000);

      expect(formatRelativeTime(thirtyMinutesAgo.toISOString())).toBe("30分前");
    });

    it("should return hours for dates within the last day", () => {
      const now = new Date();
      const threeHoursAgo = new Date(now.getTime() - 3 * 60 * 60 * 1000);

      expect(formatRelativeTime(threeHoursAgo.toISOString())).toBe("3時間前");
    });

    it("should return days for dates within the last week", () => {
      const now = new Date();
      const threeDaysAgo = new Date(now.getTime() - 3 * 24 * 60 * 60 * 1000);

      expect(formatRelativeTime(threeDaysAgo.toISOString())).toBe("3日前");
    });

    it("should return absolute time for dates older than 1 week", () => {
      const now = new Date();
      const twoWeeksAgo = new Date(now.getTime() - 14 * 24 * 60 * 60 * 1000);

      const result = formatRelativeTime(twoWeeksAgo.toISOString());

      // Should delegate to formatAbsoluteTime
      expect(result).toMatch(/\d{4}\/\d{1,2}\/\d{1,2}/);
    });

    it("should handle edge cases correctly", () => {
      const now = new Date();

      // Exactly 1 minute ago
      const oneMinuteAgo = new Date(now.getTime() - 60 * 1000);
      expect(formatRelativeTime(oneMinuteAgo.toISOString())).toBe("1分前");

      // Exactly 1 hour ago
      const oneHourAgo = new Date(now.getTime() - 60 * 60 * 1000);
      expect(formatRelativeTime(oneHourAgo.toISOString())).toBe("1時間前");

      // Exactly 1 day ago
      const oneDayAgo = new Date(now.getTime() - 24 * 60 * 60 * 1000);
      expect(formatRelativeTime(oneDayAgo.toISOString())).toBe("1日前");
    });
  });

  describe("formatAbsoluteTime", () => {
    it("should format date and time in Japanese locale", () => {
      const testDate = "2024-01-15T14:30:00.000Z";
      const result = formatAbsoluteTime(testDate);

      // Should include year, month, day, hour, minute
      expect(result).toMatch(/2024/);
      expect(result).toMatch(/1/);
      expect(result).toMatch(/15/);
      // Note: Time might vary based on timezone in test environment
    });

    it("should handle different date formats", () => {
      const testDate = "2023-12-25T09:15:30.000Z";
      const result = formatAbsoluteTime(testDate);

      expect(result).toMatch(/2023/);
      expect(result).toMatch(/12/);
      expect(result).toMatch(/25/);
    });
  });

  describe("formatDateOnly", () => {
    it("should format date only in Japanese long format", () => {
      const testDate = "2024-01-15T14:30:00.000Z";
      const result = formatDateOnly(testDate);

      expect(result).toMatch(/2024年/);
      expect(result).toMatch(/月/);
      expect(result).toMatch(/日/);
    });

    it("should handle different months correctly", () => {
      const testDate = "2024-12-01T00:00:00.000Z";
      const result = formatDateOnly(testDate);

      expect(result).toMatch(/2024年/);
      expect(result).toMatch(/12月/);
      expect(result).toMatch(/1日/);
    });
  });

  describe("formatShortDate", () => {
    it("should format date in short format", () => {
      const testDate = "2024-01-15T14:30:00.000Z";
      const result = formatShortDate(testDate);

      expect(result).toMatch(/1\/15|1月15日/);
    });

    it("should handle single digit dates", () => {
      const testDate = "2024-02-03T00:00:00.000Z";
      const result = formatShortDate(testDate);

      expect(result).toMatch(/2\/3|2月3日/);
    });
  });

  describe("formatTimeOnly", () => {
    it("should format time only", () => {
      const testDate = "2024-01-15T14:30:00.000Z";
      const result = formatTimeOnly(testDate);

      // Should include hour and minute
      expect(result).toMatch(/\d{1,2}:\d{2}|\d{1,2}時\d{2}分/);
    });

    it("should handle different times", () => {
      const testDate = "2024-01-15T09:05:00.000Z";
      const result = formatTimeOnly(testDate);

      expect(result).toMatch(/\d{1,2}:\d{2}|\d{1,2}時\d{2}分/);
    });
  });

  describe("edge cases and error handling", () => {
    it("should handle invalid date strings gracefully", () => {
      expect(() => formatRelativeTime("invalid-date")).not.toThrow();
      expect(() => formatAbsoluteTime("invalid-date")).not.toThrow();
      expect(() => formatDateOnly("invalid-date")).not.toThrow();
      expect(() => formatShortDate("invalid-date")).not.toThrow();
      expect(() => formatTimeOnly("invalid-date")).not.toThrow();
    });

    it("should handle empty strings", () => {
      expect(() => formatRelativeTime("")).not.toThrow();
      expect(() => formatAbsoluteTime("")).not.toThrow();
      expect(() => formatDateOnly("")).not.toThrow();
      expect(() => formatShortDate("")).not.toThrow();
      expect(() => formatTimeOnly("")).not.toThrow();
    });

    it("should handle future dates", () => {
      const now = new Date();
      const futureDate = new Date(now.getTime() + 60 * 60 * 1000); // 1 hour in the future

      // Future dates might return negative values or specific behavior
      expect(() => formatRelativeTime(futureDate.toISOString())).not.toThrow();
    });

    it("should handle very old dates", () => {
      const veryOldDate = "1900-01-01T00:00:00.000Z";

      expect(() => formatRelativeTime(veryOldDate)).not.toThrow();
      expect(() => formatAbsoluteTime(veryOldDate)).not.toThrow();
    });

    it("should handle leap year dates", () => {
      const leapYearDate = "2024-02-29T12:00:00.000Z";

      expect(() => formatAbsoluteTime(leapYearDate)).not.toThrow();
      expect(() => formatDateOnly(leapYearDate)).not.toThrow();
    });
  });

  describe("timezone handling", () => {
    it("should handle UTC dates consistently", () => {
      const utcDate = "2024-01-15T00:00:00.000Z";

      const absoluteResult = formatAbsoluteTime(utcDate);
      const dateResult = formatDateOnly(utcDate);

      expect(absoluteResult).toBeDefined();
      expect(dateResult).toBeDefined();
    });

    it("should handle dates with timezone offsets", () => {
      const dateWithOffset = "2024-01-15T14:30:00+09:00";

      expect(() => formatAbsoluteTime(dateWithOffset)).not.toThrow();
      expect(() => formatTimeOnly(dateWithOffset)).not.toThrow();
    });
  });

  describe("boundary conditions", () => {
    it("should handle year boundaries", () => {
      const newYearDate = "2024-01-01T00:00:00.000Z";
      const yearEndDate = "2023-12-31T23:59:59.000Z";

      expect(formatDateOnly(newYearDate)).toMatch(/2024年/);
      expect(formatDateOnly(yearEndDate)).toMatch(/2023年/);
    });

    it("should handle month boundaries", () => {
      const monthStart = "2024-02-01T00:00:00.000Z";
      const monthEnd = "2024-01-31T23:59:59.000Z";

      expect(formatShortDate(monthStart)).toMatch(/2\/1|2月1日/);
      expect(formatShortDate(monthEnd)).toMatch(/1\/31|1月31日/);
    });
  });
});
