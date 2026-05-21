import { describe, it, expect, beforeEach, jest } from "@jest/globals";

import { uploadAndProcess, connectWebSocket } from "../services/ApiService";

import type ProcessOptions from "../interfaces/ProcessOptions";

// Inicializa o mock do fetch nativo no escopo global para interceptação dos testes
const mockFetch = jest.fn<typeof fetch>();
global.fetch = mockFetch;

describe("ApiService", () => {
  beforeEach(() => {
    mockFetch.mockReset();
  });

  it("should successfully upload and process data", async () => {
    const mockFileBuffer = new Uint8Array([1, 2, 3]);
    const mockFileName = "test.xml";
    const mockOptions: ProcessOptions = {
      tags: ["tag1", "tag2"],
      exportExcel: true,
      exportPdf: false,
      exportPath: "/path/to/export",
    };

    const mockResponse = {
      success: true,
      message: "Processing started",
      generated_files: [],
    };

    mockFetch.mockResolvedValueOnce({
      ok: true,
      status: 200,
      json: async () => mockResponse,
    } as unknown as Response);

    const result = await uploadAndProcess(
      mockFileBuffer,
      mockFileName,
      mockOptions,
    );

    expect(result).toEqual(mockResponse);
    expect(mockFetch).toHaveBeenCalledTimes(1);

    // Verifica as chaves obrigatórias enviadas no Multipart FormData
    const fetchArgs = mockFetch.mock.calls[0];
    const formData = fetchArgs[1]?.body as FormData;
    expect(formData.has("file")).toBe(true);
    expect(formData.get("tags")).toBe("tag1,tag2");
    expect(formData.get("formats")).toBe("xlsx");
    expect(formData.get("output_path")).toBe("/path/to/export");
  });

  it("should throw an error with backend detail message on failure", async () => {
    const mockFileBuffer = new Uint8Array([1, 2, 3]);

    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 400,
      json: async () => ({ detail: "Invalid XML format" }),
    } as unknown as Response);

    await expect(
      uploadAndProcess(mockFileBuffer, "test.xml", {
        tags: null,
        exportExcel: false,
        exportPdf: false,
        exportPath: "",
      }),
    ).rejects.toThrow("Invalid XML format");
  });

  it("should throw simple HTTP error on failure if JSON is unparseable", async () => {
    const consoleSpy = jest
      .spyOn(console, "error")
      .mockImplementation(() => undefined);
    const mockFileBuffer = new Uint8Array([1, 2, 3]);

    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 500,
      json: async () => {
        throw new Error("Not JSON");
      },
    } as unknown as Response);

    await expect(
      uploadAndProcess(mockFileBuffer, "test.xml", {
        tags: null,
        exportExcel: false,
        exportPdf: false,
        exportPath: "",
      }),
    ).rejects.toThrow("Erro HTTP! Status: 500");

    consoleSpy.mockRestore();
  });

  it("should catch and rethrow network errors", async () => {
    const mockFileBuffer = new Uint8Array([1, 2, 3]);

    mockFetch.mockRejectedValueOnce(new Error("Network Error"));

    await expect(
      uploadAndProcess(mockFileBuffer, "test.xml", {
        tags: null,
        exportExcel: false,
        exportPdf: false,
        exportPath: "",
      }),
    ).rejects.toThrow("Network Error");
  });
});

// Mock da classe WebSocket para espelhar comportamentos em background
class MockWebSocket implements Partial<WebSocket> {
  url: string;
  onmessage: ((event: MessageEvent) => void) | null = null;

  constructor(url: string) {
    this.url = url;
  }
}

global.WebSocket = MockWebSocket as unknown as typeof WebSocket;

describe("ApiService - WebSocket", () => {
  it("connects to websocket and triggers callback on message", () => {
    const mockCallback = jest.fn();

    const ws = connectWebSocket(mockCallback) as unknown as MockWebSocket;
    expect(ws.url).toContain("/api/ws");

    if (ws.onmessage) {
      ws.onmessage(
        new MessageEvent("message", {
          data: JSON.stringify({ progress: 50 }),
        }),
      );
    }

    expect(mockCallback).toHaveBeenCalledWith({ progress: 50 });
  });
});
