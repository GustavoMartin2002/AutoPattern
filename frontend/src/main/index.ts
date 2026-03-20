import { app, shell, BrowserWindow, ipcMain, dialog } from "electron";
import { electronApp, optimizer, is } from "@electron-toolkit/utils";
import { join } from "path";
import * as fs from "fs";

function createWindow(): void {
  // Cria a janela do Software.
  const mainWindow = new BrowserWindow({
    width: 1280,
    height: 1024,
    minWidth: 800,
    minHeight: 600,
    icon: join(__dirname, "../../resources/icon.png"),
    show: false,
    backgroundColor: "#0b0f17",
    autoHideMenuBar: true,
    webPreferences: {
      preload: join(__dirname, "../preload/index.mjs"),
      sandbox: false,
    },
  });

  mainWindow.on("ready-to-show", () => {
    mainWindow.maximize();
    mainWindow.show();
  });

  mainWindow.webContents.setWindowOpenHandler((details) => {
    shell.openExternal(details.url);
    return { action: "deny" };
  });

  // HMR (Hot Module Replacement) para o renderer baseado no cli do electron-vite.
  // Carrega a URL remota para desenvolvimento ou o arquivo html local para produção.
  if (is.dev && process.env["ELECTRON_RENDERER_URL"]) {
    mainWindow.loadURL(process.env["ELECTRON_RENDERER_URL"]);
  } else {
    mainWindow.loadFile(join(__dirname, "../renderer/index.html"));
  }
}

// Este método será chamado quando o Electron terminar de inicializar e estiver pronto para criar janelas do navegador.
// Algumas APIs só podem ser usadas após este evento ocorrer.
app.whenReady().then(() => {
  // Define o id do modelo de usuário do app para janelas
  electronApp.setAppUserModelId("com.autopattern");

  // Abre ou fecha DevTools por padrão com F12 em desenvolvimento e ignora Command ou Control + R em produção.
  app.on("browser-window-created", (_, window) => {
    optimizer.watchWindowShortcuts(window);
  });

  // IPC Handlers (Comunicação entre renderer e main)
  ipcMain.handle("dialog:openFile", async (event) => {
    const webContents = event.sender;
    const win = BrowserWindow.fromWebContents(webContents);
    const { canceled, filePaths } = await dialog.showOpenDialog(win!, {
      properties: ["openFile"],
      filters: [{ name: "XML Files", extensions: ["xml"] }],
    });
    if (!canceled) {
      return filePaths[0];
    }
    return null;
  });

  ipcMain.handle("dialog:openDirectory", async (event) => {
    const webContents = event.sender;
    const win = BrowserWindow.fromWebContents(webContents);
    const { canceled, filePaths } = await dialog.showOpenDialog(win!, {
      properties: ["openDirectory"],
    });
    if (!canceled) {
      return filePaths[0];
    }
    return null;
  });

  ipcMain.handle("file:read", async (_event, filePath: string) => {
    try {
      const fileBuffer = fs.readFileSync(filePath);
      return fileBuffer;
    } catch (error) {
      console.error("Failed to read file:", error);
      return null;
    }
  });

  createWindow();

  app.on("activate", function () {
    // Em macOS é comum recriar uma janela no app quando o icone é clicado e não há outras janelas abertas.
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

// Fecha todas as janelas quando o usuário fecha o app, exceto no macOS.
// É comum que o app e a barra de menu permaneçam ativos até que o usuário encerre o app explicitamente com Command ou Control + Q.
app.on("window-all-closed", () => {
  if (process.platform !== "darwin") {
    app.quit();
  }
});
