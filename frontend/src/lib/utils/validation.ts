// 入力値のバリデーション機能

export interface ValidationResult {
  isValid: boolean;
  errors: string[];
}

export interface ValidationRule {
  required?: boolean;
  minLength?: number;
  maxLength?: number;
  pattern?: RegExp;
  custom?: (value: string) => string | null;
}

export function validateInput(
  value: string,
  rules: ValidationRule,
): ValidationResult {
  const errors: string[] = [];
  const trimmedValue = value.trim();

  // 必須チェック
  if (rules.required && !trimmedValue) {
    errors.push("この項目は必須です");
    return { isValid: false, errors };
  }

  // 空文字の場合、必須でなければOK
  if (!trimmedValue && !rules.required) {
    return { isValid: true, errors: [] };
  }

  // 最小文字数チェック
  if (rules.minLength && trimmedValue.length < rules.minLength) {
    errors.push(`${rules.minLength}文字以上で入力してください`);
  }

  // 最大文字数チェック
  if (rules.maxLength && trimmedValue.length > rules.maxLength) {
    errors.push(`${rules.maxLength}文字以内で入力してください`);
  }

  // パターンチェック
  if (rules.pattern && !rules.pattern.test(trimmedValue)) {
    errors.push("入力形式が正しくありません");
  }

  // カスタムバリデーション
  if (rules.custom) {
    const customError = rules.custom(trimmedValue);
    if (customError) {
      errors.push(customError);
    }
  }

  return {
    isValid: errors.length === 0,
    errors,
  };
}

// 共通のバリデーションルール
export const ValidationRules = {
  // プロフィール項目
  profileLabel: {
    required: true,
    maxLength: 20,
    minLength: 1,
  },
  profileValue: {
    required: true,
    maxLength: 100,
    minLength: 1,
  },

  // Q&A回答
  qaAnswer: {
    required: false,
    maxLength: 500,
    minLength: 1,
  },

  // プロフィール基本情報
  displayName: {
    required: true,
    maxLength: 50,
    minLength: 1,
  },
  bio: {
    required: false,
    maxLength: 200,
  },
  selfIntroduction: {
    required: false,
    maxLength: 500,
  },

  // お問い合わせフォーム
  contactTitle: {
    required: true,
    maxLength: 100,
    minLength: 5,
  },
  contactDescription: {
    required: true,
    maxLength: 2000,
    minLength: 10,
  },
  contactEmail: {
    required: false,
    maxLength: 100,
    pattern: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
  },
} as const;

// HTMLの不正タグをエスケープ
export function sanitizeHtml(input: string): string {
  return input
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

// 改行を除く制御文字を除去
export function sanitizeInput(input: string): string {
  // eslint-disable-next-line no-control-regex
  return input.replace(/[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]/g, "");
}
