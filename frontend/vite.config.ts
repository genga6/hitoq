import tailwindcss from "@tailwindcss/vite";
import { sveltekit } from "@sveltejs/kit/vite";
import { defineConfig } from "vite";
import { sentrySvelteKit } from "@sentry/sveltekit";

export default defineConfig({
  plugins: [
    // 本番環境でのみSentryを有効化
    ...(process.env.NODE_ENV === "production"
      ? [
          sentrySvelteKit({
            sourceMapsUploadOptions: {
              org: "your-org",
              project: "hitoq-frontend",
              url: "https://sentry.io/",
              telemetry: false,
            },
          }),
        ]
      : []),
    tailwindcss(),
    sveltekit(),
  ],
  server: {
    // https://ja.vite.dev/config/server-options
    host: "0.0.0.0",
    port: 5173,
    strictPort: true,
    watch: {
      usePolling: true,
      interval: 1000, // 100ms -> 1000ms (10倍軽量化)
    },
  },
  test: {
    projects: [
      {
        extends: "./vite.config.ts",
        test: {
          name: "client",
          environment: "browser",
          browser: {
            enabled: true,
            provider: "playwright",
            instances: [{ browser: "chromium" }],
          },
          include: ["src/**/*.svelte.{test,spec}.{js,ts}"],
          exclude: ["src/lib/server/**"],
          setupFiles: ["./vitest-setup-client.ts"],
        },
      },
      {
        extends: "./vite.config.ts",
        test: {
          name: "server",
          environment: "node",
          include: ["src/**/*.{test,spec}.{js,ts}"],
          exclude: ["src/**/*.svelte.{test,spec}.{js,ts}"],
          setupFiles: ["./src/lib/tests/setup/setup.ts"],
        },
      },
    ],
  },
});
