import { defineConfig } from "vitest/config";
import { svelte } from "@sveltejs/vite-plugin-svelte";
import path from "path";

export default defineConfig({
  plugins: [svelte({ hot: !process.env.VITEST })],
  resolve: {
    alias: {
      $lib: path.resolve("./src/lib"),
      $routes: path.resolve("./src/routes"),
    },
  },
  test: {
    globals: true,
    environment: "jsdom",
    setupFiles: ["./src/lib/tests/setup/setup.ts"],
    include: ["src/**/*.{test,spec}.{js,ts}"],
    coverage: {
      reporter: ["text", "html", "lcov"],
      exclude: [
        "node_modules/",
        "src/lib/tests/",
        "**/*.d.ts",
        "**/*.config.{js,ts}",
      ],
    },
  },
});
