import { defineConfig } from "vitest/config";
import { svelte } from "@sveltejs/vite-plugin-svelte";
import path from "path";

export default defineConfig({
  plugins: [svelte({ hot: !process.env.VITEST })],
  resolve: {
    alias: {
      $lib: path.resolve("./src/lib"),
      $routes: path.resolve("./src/routes"),
      "$env/static/public": path.resolve("./test/setup/mock-env.ts"),
      "$app/environment": path.resolve("./test/setup/mock-app-environment.ts"),
    },
  },
  test: {
    globals: true,
    environment: "happy-dom",
    setupFiles: ["./test/setup/setup.ts"],
    include: ["test/**/*.{test,spec}.{js,ts}"],
    coverage: {
      reporter: ["text", "html", "lcov"],
      exclude: ["node_modules/", "test/", "**/*.d.ts", "**/*.config.{js,ts}"],
    },
  },
});
