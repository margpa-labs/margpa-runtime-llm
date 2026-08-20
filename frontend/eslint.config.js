import js from "@eslint/js";
import tseslint from "typescript-eslint";
import globals from "globals";
import reactHooks from "eslint-plugin-react-hooks";
import reactRefresh from "eslint-plugin-react-refresh";

export default tseslint.config(
  { ignores: ["**/web/static/**", "dist/**"] },
  js.configs.recommended,
  {
    files: ["src/**/*.{ts,tsx}", "vite.config.ts"],
    extends: [...tseslint.configs.strictTypeChecked, reactHooks.configs.flat["recommended-latest"]],
    languageOptions: {
      globals: globals.browser,
      parserOptions: {
        project: "./tsconfig.json",
        tsconfigRootDir: import.meta.dirname,
      },
    },
    plugins: {
      "react-refresh": reactRefresh,
    },
    rules: {
      "@typescript-eslint/no-unused-vars": ["error", { argsIgnorePattern: "^_" }],
      "react-refresh/only-export-components": "warn",
      // noUncheckedIndexedAccess (tsconfig) plus manual bounds-checked loops
      // (e.g. the safeMarkdown parser) make `!` the natural way to express
      // "this index was already verified in range" — a standard pairing.
      "@typescript-eslint/no-non-null-assertion": "off",
    },
  },
);
