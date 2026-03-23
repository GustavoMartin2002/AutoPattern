import { useState } from "react";
import LogEntry from "@renderer/interfaces/LogEntry";
import { ApiService } from "@renderer/services/ApiService";

// Hook responsável por gerenciar o estado e a lógica do processo de upload e processamento de arquivos
export const useProcessFile = () => {
  const [filePath, setFilePath] = useState<string>("");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [tags, setTags] = useState<string[]>(["Exemplo"]);
  const [exportExcel, setExportExcel] = useState<boolean>(true);
  const [exportPdf, setExportPdf] = useState<boolean>(false);
  const [exportPath, setExportPath] = useState<string>("");
  const [isProcessing, setIsProcessing] = useState<boolean>(false);
  const [progress, setProgress] = useState<number>(0);
  const [statusText, setStatusText] = useState<string>("");
  const [logs, setLogs] = useState<LogEntry[]>([
    {
      id: crypto.randomUUID(),
      type: "success",
      message: "Aplicativo iniciado com sucesso.",
    },
  ]);

  // Função responsável por adicionar logs ao estado
  const addLog = (type: LogEntry["type"], message: string) => {
    setLogs((prev) => [...prev, { id: crypto.randomUUID(), type, message }]);
  };

  // Função responsável por selecionar o arquivo XML
  const handleSelectFile = async (webFile?: File) => {
    try {
      if (window.electron) {
        // Dispara o Evento de File System Nativo pelo main process do Electron
        const path = await window.electron.openFile();
        if (path) {
          if (!path.toLowerCase().endsWith(".xml")) {
            addLog("error", "Formato inválido. Selecione um arquivo .xml ativo.");
            return;
          }
          setFilePath(path);
          addLog("success", `Arquivo selecionado: ${path}`);
        }
      } else if (webFile) {
        // Metodo suportado via navegadores no Web Mode
        if (!webFile.name.toLowerCase().endsWith(".xml")) {
          addLog("error", "Formato inválido. Selecione um arquivo .xml ativo.");
          return;
        }
        setFilePath(webFile.name);
        setSelectedFile(webFile);
        addLog("success", `Arquivo ${webFile.name} selecionado para upload.`);
      } else {
        addLog("warning", "API do Electron não disponível. Use o botão de upload.");
      }
    } catch (err) {
      addLog("error", "Falha ao selecionar arquivo.");
    }
  };

  // Função responsável por selecionar o diretório de destino
  const handleSelectExportPath = async () => {
    try {
      // Dispara o Evento de File System Nativo pelo main process do Electron
      if (window.electron) {
        const path = await window.electron.openDirectory();
        if (path) {
          setExportPath(path);
          addLog("success", `Diretório selecionado: ${path}`);
        }
      } else {
        // Metodo suportado via navegadores no Web Mode
        addLog("warning", "API do Electron não disponível na pré-visualização web.");
        setExportPath("C:\\Fake\\Export\\Folder");
      }
    } catch (err) {
      addLog("error", "Falha ao selecionar diretório de destino.");
    }
  };

  // Função responsável por executar o processamento do arquivo
  const handleExecute = async () => {
    // Validação de arquivo
    if (!filePath || !filePath.toLowerCase().endsWith(".xml")) {
      addLog("error", "Arquivo ausente ou inválido. Selecione um .xml primeiro.");
      return;
    }
    // Validação de limite de tags
    if (tags.length > 30) {
      addLog("error", "Limite excedido. O máximo suportado é de 30 tags.");
      return;
    }
    // Validação de formato de exportação
    if (!exportExcel && !exportPdf) {
      addLog("error", "É obrigatório selecionar ao menos um formato (.xlsx ou .pdf).");
      return;
    }

    setIsProcessing(true);
    setProgress(5);
    setStatusText("Lendo arquivo local...");
    addLog("process", `Lendo arquivo: ${filePath}`);

    let ws: WebSocket | null = null;
    try {
      let fileBuffer: Uint8Array | null = null;
      let fileName = "arquivo.xml";

      // Carrega o buffer em binário via chamadas nativas (Electron) ou via Fallback para Desktop Web
      if (window.electron) {
        fileBuffer = await window.electron.readFile(filePath);
        fileName = filePath.split("\\").pop() || "arquivo.xml";
      } else if (selectedFile) {
        const arrayBuffer = await selectedFile.arrayBuffer();
        fileBuffer = new Uint8Array(arrayBuffer);
        fileName = selectedFile.name;
      }

      if (!fileBuffer) throw new Error("Não foi possível ler o arquivo. Certifique-se de ter selecionado um arquivo válido.");

      setProgress(15);
      setStatusText("Conectando ao servidor...");

      // Abre canal interativo via WebSockets para escutar progresso atualizado do Backend em tempo real
      ws = ApiService.connectWebSocket((data: any) => {
        if (data.progress) setProgress(data.progress);
        if (data.message) {
          setStatusText(data.message);
          addLog("info", data.message);
        }
      });

      setStatusText("Enviando dados para processamento...");
      addLog("process", "Iniciando upload e processamento no backend...");

      // Constrói um POST multipart/form-data restrito, validando Buffer do arquivo e Opções de parse do Backend
      const response = await ApiService.uploadAndProcess(fileBuffer, fileName, {
        tags,
        exportExcel,
        exportPdf,
        exportPath: exportPath || "outputs",
      });

      setProgress(100);
      setStatusText("Processo concluído!");
      addLog("success", response.message || "Exportação finalizada com sucesso.");

      const targetFolder = exportPath || "outputs";
      addLog("info", `Verifique a pasta ${targetFolder}`);
    } catch (err: any) {
      console.error(err);

      const errorMessage = "Falha na comunicação com o servidor.";
      addLog("error", errorMessage);
      setStatusText("Erro no processamento");
      setProgress(0);
    } finally {
      setIsProcessing(false);
      // Prevenção de Memory Leak:
      // Assegura o encerramento do stream WebSocket independentemente da execução ter sido bem ou mal sucedida
      if (ws) ws.close();
    }
  };

  return {
    filePath,
    tags,
    setTags,
    exportExcel,
    setExportExcel,
    exportPdf,
    setExportPdf,
    exportPath,
    isProcessing,
    progress,
    statusText,
    logs,
    handleSelectFile,
    handleSelectExportPath,
    handleExecute,
  };
};
