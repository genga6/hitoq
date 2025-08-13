import type { Handle } from "@sveltejs/kit";
import { dev } from "$app/environment";
import * as Sentry from "@sentry/sveltekit";
import { PUBLIC_SENTRY_DSN, PUBLIC_ENVIRONMENT } from "$env/static/public";

Sentry.init({
  dsn: PUBLIC_SENTRY_DSN,
  tracesSampleRate: 0.1,
  environment: PUBLIC_ENVIRONMENT || "development",
});

const customHandle: Handle = async ({ event, resolve }) => {
  // HTTPS enforcement in production
  if (!dev) {
    const proto = event.request.headers.get("x-forwarded-proto");
    const host = event.request.headers.get("host");

    // If not HTTPS in production, redirect to HTTPS
    if (proto === "http" && host) {
      const url = new URL(event.request.url);
      return new Response(null, {
        status: 301,
        headers: {
          location: `https://${host}${url.pathname}${url.search}`,
        },
      });
    }
  }

  // Set security headers
  const response = await resolve(event);

  response.headers.set("X-Frame-Options", "DENY");
  response.headers.set("X-Content-Type-Options", "nosniff");
  response.headers.set("Referrer-Policy", "strict-origin-when-cross-origin");
  response.headers.set(
    "Permissions-Policy",
    "geolocation=(), microphone=(), camera=()",
  );

  // Only set HSTS in production with HTTPS
  if (!dev && event.request.headers.get("x-forwarded-proto") === "https") {
    response.headers.set(
      "Strict-Transport-Security",
      "max-age=31536000; includeSubDomains",
    );
  }

  return response;
};

export const handle = Sentry.sentryHandle(customHandle);
export const handleError = Sentry.handleErrorWithSentry();
