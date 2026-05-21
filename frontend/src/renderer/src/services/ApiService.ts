import type ApiError from "@renderer/interfaces/ApiError";
import type ApiResponse from "@renderer/interfaces/ApiResponse";
import type ProcessOptions from "@renderer/interfaces/ProcessOptions";
import type WebSocketMessage from "@renderer/interfaces/WebSocketMessage";

// Verifica se a aplicação está rodando em ambiente Electron
const isElectron = Boolean(window.electron);

// Adota Proxy Relativo automático do Vite durante simulações no navegador web
const API_URL = isElectron
  ? (process.env.VITE_API_URL ?? "http://localhost:8000")
  : "";

// Estabelece conexão WebSocket com o Backend
const WS_URL = isElectron
  ? API_URL.replace(/^http/, "ws")
  : `${window.location.protocol.replace("http", "ws")}//${window.location.host}`;

/**
 * Realiza o envio via Multipart do XML junto com as regras de extração à API
 * @param fileBuffer O conteúdo do arquivo convertido e serializado em binário seguro
 * @param fileName O nome do arquivo em escopo de payload HTTP
 * @param options O contrato gerado pelo Client contendo as tags e caminhos para a API processar
 * @returns Promessa contendo tipagem fechada e validadora do Response esperado
 * @throws {Error} Repassa via throws instâncias de erro padronizadas aos Hook Clients baseadas nas regras de Negócio
 */
export async function uploadAndProcess(
  fileBuffer: Uint8Array,
  fileName: string,
  options: ProcessOptions,
): Promise<ApiResponse> {
  const formData = new FormData();
  const blob = new Blob([new Uint8Array(fileBuffer)], {
    type: "application/xml",
  });

  formData.append("file", blob, fileName);
  if (options.tags && options.tags.length > 0)
    formData.append("tags", options.tags.join(","));

  const formats: string[] = [];
  if (options.exportExcel) formats.push("xlsx");
  if (options.exportPdf) formats.push("pdf");
  if (formats.length > 0) formData.append("formats", formats.join(","));
  if (options.exportPath) formData.append("output_path", options.exportPath);

  try {
    const response = await fetch(`${API_URL}/api/upload`, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      let errorMessage = `Erro HTTP! Status: ${response.status}`;
      try {
        const errorData = (await response.json()) as ApiError;
        if (errorData.detail) {
          errorMessage =
            typeof errorData.detail === "string"
              ? errorData.detail
              : JSON.stringify(errorData.detail);
        } else if (errorData.message) {
          errorMessage = errorData.message;
        }
      } catch (e) {
        // Fallback passivo: Uma mensagem padrão HTTP será mantida em caso de falha de parser interno de Load
        console.error("Falha ao parsear resposta de erro", e);
      }
      throw new Error(errorMessage);
    }

    const data = (await response.json()) as ApiResponse;
    return data;
  } catch (error) {
    // Garante exceção estrita e repassa em arvore de erro à camada de UI (Hook Controller) para renderização limpa
    throw error instanceof Error
      ? error
      : new Error("Falha desconhecida de rede ou servidor");
  }
}

/**
 * Estabelece canal WebSocket assíncrono para leitura do processador no Backend
 * Usado principalmente para manter o Controller informado via Stream garantindo uma UX assíncrona
 * @param onMessage Callback despachado quando um novo binário contendo o Update Message é recebido do FastAPI
 * @returns Intância de WS isolada de UI
 */
export function connectWebSocket(
  onMessage: (data: WebSocketMessage) => void,
): WebSocket {
  const ws = new WebSocket(`${WS_URL}/api/ws`);

  ws.onmessage = (event: MessageEvent) => {
    try {
      const data = JSON.parse(event.data as string) as WebSocketMessage;
      onMessage(data);
    } catch (err) {
      console.error("Falha ao parsear mensagem WebSocket", err);
    }
  };

  return ws;
}
