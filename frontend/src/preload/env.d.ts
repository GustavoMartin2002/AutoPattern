// Electron API Type Definition
import { ElectronAPI } from "./env";

declare global {
  interface Window {
    electron: ElectronAPI;
  }
}

export {};
