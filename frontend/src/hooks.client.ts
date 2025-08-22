import { handleErrorWithSentry, init } from "@sentry/sveltekit";
import { PUBLIC_SENTRY_DSN, PUBLIC_ENVIRONMENT } from "$env/static/public";
import { getCsrfToken } from "$lib/api-client/auth";

init({
  dsn: PUBLIC_SENTRY_DSN,
  integrations: [],
  tracesSampleRate: 0.1,
  replaysSessionSampleRate: 0.1,
  replaysOnErrorSampleRate: 1.0,
  environment: PUBLIC_ENVIRONMENT || "development",
});

// CSRFトークンを初期化時に取得
if (typeof window !== "undefined") {
  getCsrfToken().catch((error) => {
    console.warn("初期CSRFトークン取得に失敗:", error);
  });
}

// If you have custom error handling, you can wrap it with handleErrorWithSentry
export const handleError = handleErrorWithSentry();
