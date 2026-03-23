/// <reference types="vite/client" />

// Interface que referencia a ponte de comunicação entre o renderer e o main process.
interface Window {
  electron: {
    openFile: () => Promise<string | null>;
    openDirectory: () => Promise<string | null>;
    readFile: (filePath: string) => Promise<Uint8Array | null>;
  };
  api: unknown;
}

// Referenciando as variáveis de ambiente do processo principal.
declare const process: {
  env: {
    [key: string]: string | undefined;
  };
};
