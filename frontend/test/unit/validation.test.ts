import { describe, it, expect } from "vitest";
import {
  validateInput,
  ValidationRules,
  sanitizeHtml,
  sanitizeInput,
  type ValidationRule,
} from "$lib/utils/validation";

describe("Validation Utils", () => {
  describe("validateInput", () => {
    describe("required validation", () => {
      const rule: ValidationRule = { required: true };

      it("should pass with valid input", () => {
        const result = validateInput("test", rule);
        expect(result.isValid).toBe(true);
        expect(result.errors).toEqual([]);
      });

      it("should fail with empty string", () => {
        const result = validateInput("", rule);
        expect(result.isValid).toBe(false);
        expect(result.errors).toContain("この項目は必須です");
      });

      it("should fail with whitespace only", () => {
        const result = validateInput("   ", rule);
        expect(result.isValid).toBe(false);
        expect(result.errors).toContain("この項目は必須です");
      });
    });

    describe("length validation", () => {
      it("should pass minLength validation", () => {
        const rule: ValidationRule = { minLength: 3 };
        const result = validateInput("test", rule);
        expect(result.isValid).toBe(true);
        expect(result.errors).toEqual([]);
      });

      it("should fail minLength validation", () => {
        const rule: ValidationRule = { minLength: 5 };
        const result = validateInput("abc", rule);
        expect(result.isValid).toBe(false);
        expect(result.errors).toContain("5文字以上で入力してください");
      });

      it("should pass maxLength validation", () => {
        const rule: ValidationRule = { maxLength: 10 };
        const result = validateInput("test", rule);
        expect(result.isValid).toBe(true);
        expect(result.errors).toEqual([]);
      });

      it("should fail maxLength validation", () => {
        const rule: ValidationRule = { maxLength: 3 };
        const result = validateInput("testing", rule);
        expect(result.isValid).toBe(false);
        expect(result.errors).toContain("3文字以内で入力してください");
      });
    });

    describe("pattern validation", () => {
      const emailRule: ValidationRule = {
        pattern: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
      };

      it("should pass email pattern validation", () => {
        const result = validateInput("test@example.com", emailRule);
        expect(result.isValid).toBe(true);
        expect(result.errors).toEqual([]);
      });

      it("should fail email pattern validation", () => {
        const result = validateInput("invalid-email", emailRule);
        expect(result.isValid).toBe(false);
        expect(result.errors).toContain("入力形式が正しくありません");
      });
    });

    describe("custom validation", () => {
      const customRule: ValidationRule = {
        custom: (value: string) =>
          value === "forbidden" ? "この値は使用できません" : null,
      };

      it("should pass custom validation", () => {
        const result = validateInput("allowed", customRule);
        expect(result.isValid).toBe(true);
        expect(result.errors).toEqual([]);
      });

      it("should fail custom validation", () => {
        const result = validateInput("forbidden", customRule);
        expect(result.isValid).toBe(false);
        expect(result.errors).toContain("この値は使用できません");
      });
    });
  });

  describe("ValidationRules", () => {
    it("should validate display name correctly", () => {
      const result = validateInput(
        "テストユーザー",
        ValidationRules.displayName,
      );
      expect(result.isValid).toBe(true);
    });

    it("should validate email correctly", () => {
      const result = validateInput(
        "test@example.com",
        ValidationRules.contactEmail,
      );
      expect(result.isValid).toBe(true);
    });

    it("should validate QA answer correctly", () => {
      const result = validateInput("これは回答です", ValidationRules.qaAnswer);
      expect(result.isValid).toBe(true);
    });
  });

  describe("sanitizeHtml", () => {
    it("should escape HTML characters", () => {
      const input = '<script>alert("XSS")</script>';
      const expected = "&lt;script&gt;alert(&quot;XSS&quot;)&lt;/script&gt;";
      expect(sanitizeHtml(input)).toBe(expected);
    });

    it("should handle mixed content", () => {
      const input = "Hello & <b>World</b> \"quotes\" 'apostrophes'";
      const expected =
        "Hello &amp; &lt;b&gt;World&lt;/b&gt; &quot;quotes&quot; &#39;apostrophes&#39;";
      expect(sanitizeHtml(input)).toBe(expected);
    });
  });

  describe("sanitizeInput", () => {
    it("should remove control characters except newline", () => {
      const input = "Hello\x00World\nTest\x1F";
      const expected = "HelloWorld\nTest";
      expect(sanitizeInput(input)).toBe(expected);
    });

    it("should preserve normal characters", () => {
      const input = "こんにちは! Hello123";
      expect(sanitizeInput(input)).toBe(input);
    });
  });
});
