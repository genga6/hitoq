import {
  handleErrorWithSentry,
  init,
  browserTracingIntegration,
} from "@sentry/sveltekit";
import { PUBLIC_SENTRY_DSN, PUBLIC_ENVIRONMENT } from "$env/static/public";
import { getCsrfToken } from "$lib/api-client/base";

init({
  dsn: PUBLIC_SENTRY_DSN,
  integrations: [
    browserTracingIntegration({
      // Disable automatic navigation tracking to avoid conflicts with SvelteKit
      enableLongTask: false,
      enableInp: false,
      enableUserTiming: false,
      // Let SvelteKit handle navigation tracking
      beforeNavigate: undefined,
    }),
  ],
  tracesSampleRate: 0.1,
  replaysSessionSampleRate: 0.1,
  replaysOnErrorSampleRate: 1.0,
  environment: PUBLIC_ENVIRONMENT || "development",
  // Disable automatic instrumentation that might conflict with SvelteKit
  instrumentNavigation: false,
});

// CSRFトークンを初期化時に取得
if (typeof window !== "undefined") {
  getCsrfToken().catch((error) => {
    console.warn("初期CSRFトークン取得に失敗:", error);
  });
}

// If you have custom error handling, you can wrap it with handleErrorWithSentry
export const handleError = handleErrorWithSentry();
