// Electron API Type Definition
import { type ElectronAPI } from "./env";

declare global {
  interface Window {
    electron: ElectronAPI;
  }
}

export {};
