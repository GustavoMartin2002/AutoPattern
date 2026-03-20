import { contextBridge, ipcRenderer } from "electron";
import { electronAPI } from "@electron-toolkit/preload";

export interface ElectronAPI {
  openFile: () => Promise<string | null>;
  openDirectory: () => Promise<string | null>;
  readFile: (filePath: string) => Promise<Uint8Array | null>;
}

// APIs personalizadas para o renderer
const api: ElectronAPI = {
  openFile: () => ipcRenderer.invoke("dialog:openFile"),
  openDirectory: () => ipcRenderer.invoke("dialog:openDirectory"),
  readFile: (filePath) => ipcRenderer.invoke("file:read", filePath),
};

// Usa as APIs `contextBridge` para expor as APIs do Electron ao renderer somente se o isolamento de contexto estiver habilitado.
// Caso contrário apenas adiciona ao DOM global.
if (process.contextIsolated) {
  try {
    contextBridge.exposeInMainWorld("electron", {
      ...electronAPI,
      openFile: api.openFile,
      openDirectory: api.openDirectory,
      readFile: api.readFile,
    });
    contextBridge.exposeInMainWorld("api", api);
  } catch (error) {
    console.error(error);
  }
} else {
  // @ts-ignore (define in dts)
  window.electron = {
    ...electronAPI,
    openFile: api.openFile,
    openDirectory: api.openDirectory,
    readFile: api.readFile,
  };
  // @ts-ignore (define in dts)
  window.api = api;
}
