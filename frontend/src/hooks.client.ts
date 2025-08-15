import { handleErrorWithSentry, init, trace } from "@sentry/sveltekit";
import { PUBLIC_SENTRY_DSN, PUBLIC_ENVIRONMENT } from "$env/static/public";

init({
  dsn: PUBLIC_SENTRY_DSN,
  integrations: [],
  tracesSampleRate: 0.1,
  replaysSessionSampleRate: 0.1,
  replaysOnErrorSampleRate: 1.0,
  environment: PUBLIC_ENVIRONMENT || "development",
});

// If you have custom error handling, you can wrap it with handleErrorWithSentry
export const handleError = handleErrorWithSentry();

export const handleFetch = trace.handleFetch();
