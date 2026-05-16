import js from "@eslint/js";
import importX from "eslint-plugin-import-x";
import pluginReact from "eslint-plugin-react";
import pluginReactHooks from "eslint-plugin-react-hooks";
import pluginReactRefresh from "eslint-plugin-react-refresh";
import globals from "globals";
import tseslint from "typescript-eslint";

/**
 * ESLint Flat Config - AutoPattern Frontend (Electron + Vite + React)
 *
 * Zonas:
 *  1. Ignorados globais
 *  2. Regras base JS (todos os arquivos)
 *  3. Regras estritas TypeScript (todos .ts/.tsx)
 *  4. Regras React + JSX (apenas renderer)
 *  5. Regras Electron main/preload (Contexto Node.js)
 *  6. Arquivos de configuração (vite, electron-vite, tailwind, etc.)
 *  7. Organização de importações
 */
export default tseslint.config(
  // 1. Ignorados Globais
  {
    ignores: [
      "dist/**",
      "out/**",
      "node_modules/**",
      "coverage/**",
      "*.config.js",
      "*.config.mjs",
      "*.md",
    ],
  },

  // 2. Recomendado Base JS
  js.configs.recommended,

  // 3. TypeScript - Estrito + Estilístico
  ...tseslint.configs.strictTypeChecked,
  ...tseslint.configs.stylisticTypeChecked,
  {
    languageOptions: {
      parserOptions: {
        projectService: true,
        tsconfigRootDir: import.meta.dirname,
      },
    },
    rules: {
      // Relaxa regras excessivamente estritas para um contexto de aplicativo desktop
      "@typescript-eslint/restrict-template-expressions": [
        "error",
        { allowNumber: true, allowBoolean: true },
      ],
      "@typescript-eslint/no-unused-vars": [
        "error",
        {
          argsIgnorePattern: "^_",
          varsIgnorePattern: "^_",
          caughtErrorsIgnorePattern: "^_",
        },
      ],
      "@typescript-eslint/consistent-type-imports": [
        "error",
        { prefer: "type-imports", fixStyle: "inline-type-imports" },
      ],
      "@typescript-eslint/consistent-type-definitions": ["error", "interface"],
      "@typescript-eslint/no-misused-promises": [
        "error",
        { checksVoidReturn: { attributes: false } },
      ],
    },
  },

  // 4. React - Processo Renderer
  {
    files: ["src/renderer/**/*.{ts,tsx}"],
    ...pluginReact.configs.flat.recommended,
  },
  {
    files: ["src/renderer/**/*.{ts,tsx}"],
    ...pluginReact.configs.flat["jsx-runtime"],
  },
  {
    files: ["src/renderer/**/*.{ts,tsx}"],
    plugins: {
      "react-hooks": pluginReactHooks,
      "react-refresh": pluginReactRefresh,
    },
    languageOptions: {
      globals: {
        ...globals.browser,
      },
    },
    settings: {
      react: {
        version: "detect",
      },
    },
    rules: {
      ...pluginReactHooks.configs.recommended.rules,

      // Vite HMR: garante que os componentes sejam exportáveis para Fast Refresh
      "react-refresh/only-export-components": [
        "warn",
        { allowConstantExport: true },
      ],

      // React 19+ com JSX transform - não precisa importar React
      "react/react-in-jsx-scope": "off",
      "react/prop-types": "off",

      // Melhores práticas para componentes
      "react/self-closing-comp": "error",
      "react/jsx-no-target-blank": "error",
      "react/jsx-curly-brace-presence": [
        "error",
        { props: "never", children: "never" },
      ],
      "react/hook-use-state": "error",
      "react/jsx-boolean-value": ["error", "never"],
      "react/jsx-fragments": ["error", "syntax"],
      "react/no-array-index-key": "warn",
    },
  },

  // 5. Electron Main + Preload - Contexto Node.js
  {
    files: ["src/main/**/*.ts", "src/preload/**/*.ts"],
    languageOptions: {
      globals: {
        ...globals.node,
      },
    },
    rules: {
      // Específico para Node: permitir require() no processo principal se necessário
      "@typescript-eslint/no-require-imports": "off",
    },
  },

  // 6. Arquivos de Configuração (não fazem parte do projeto com type-check rígido)
  {
    files: [
      "*.config.ts",
      "*.config.mts",
      "postcss.config.*",
      "tailwind.config.*",
      "jest.config.*",
      "jest.setup.ts",
      "src/**/tests/**/*",
    ],
    ...tseslint.configs.disableTypeChecked,
  },

  // 7. Organização de Importações
  {
    files: ["**/*.{ts,tsx,mts}"],
    plugins: {
      "import-x": importX,
    },
    rules: {
      "import-x/order": [
        "error",
        {
          groups: [
            "builtin",
            "external",
            "internal",
            "parent",
            "sibling",
            "index",
            "type",
          ],
          "newlines-between": "always",
          alphabetize: {
            order: "asc",
            caseInsensitive: true,
          },
        },
      ],
      "import-x/no-duplicates": "error",
      "import-x/no-useless-path-segments": "error",
    },
  },
);
