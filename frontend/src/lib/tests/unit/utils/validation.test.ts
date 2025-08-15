import { describe, it, expect } from "vitest";
import {
  validateEmail,
  validateUsername,
  validatePassword,
} from "$lib/utils/validation";

describe("Validation Utils", () => {
  describe("validateEmail", () => {
    it.each([
      ["test@example.com", true],
      ["user+tag@domain.co.jp", true],
      ["valid.email@test.org", true],
      ["", false],
      ["invalid-email", false],
      ["@domain.com", false],
      ["user@", false],
    ])('validateEmail("%s") should return %s', (email, expected) => {
      expect(validateEmail(email)).toBe(expected);
    });
  });

  describe("validateUsername", () => {
    it.each([
      ["valid_user", true],
      ["user123", true],
      ["a", true],
      ["a".repeat(15), true],
      ["", false],
      ["a".repeat(16), false],
      ["user space", false],
      ["user-dash", false],
      ["@invalid", false],
    ])('validateUsername("%s") should return %s', (username, expected) => {
      expect(validateUsername(username)).toBe(expected);
    });
  });

  describe("validatePassword", () => {
    it.each([
      ["Valid123!", true],
      ["Short1!", false],
      ["nouppercasepassword123!", false],
      ["NOLOWERCASEPASSWORD123!", false],
      ["NoNumbers!", false],
      ["NoSpecialChars123", false],
    ])('validatePassword("%s") should return %s', (password, expected) => {
      expect(validatePassword(password)).toBe(expected);
    });
  });
});
