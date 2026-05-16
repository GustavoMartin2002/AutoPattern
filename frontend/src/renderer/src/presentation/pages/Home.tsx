import ExportOptions from "../components/ExportOptions";
import FileSelector from "../components/FileSelector";
import Layout from "../components/Layout";
import LogConsole from "../components/LogConsole";
import ProgressPanel from "../components/ProgressPanel";
import TagManager from "../components/TagManager";
import { useProcessFile } from "../hooks/useProcessFile";

import type React from "react";

// Componente principal que orquestra a interface do usuário
const Home: React.FC = () => {
  const {
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
  } = useProcessFile();

  return (
    <Layout>
      <div className="flex flex-col gap-2">
        <h2 className="text-slate-500 dark:text-slate-400 text-start text-2xl">
          Configure o processamento de dados XML e exporte para múltiplos
          formatos
        </h2>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-8">
        {/* Coluna Esquerda: Inputs */}
        <div className="flex flex-col gap-6">
          <FileSelector filePath={filePath} onSelectFile={handleSelectFile} />

          <TagManager
            tags={tags}
            onAddTag={(tag) => {
              setTags((prev) => (prev.includes(tag) ? prev : [...prev, tag]));
            }}
            onRemoveTag={(t) => {
              setTags((prev) => prev.filter((tag) => tag !== t));
            }}
          />
        </div>

        {/* Coluna Direita: Export & Progress */}
        <div className="flex flex-col gap-6">
          <ExportOptions
            exportExcel={exportExcel}
            exportPdf={exportPdf}
            exportPath={exportPath}
            onToggleExcel={() => {
              setExportExcel(!exportExcel);
            }}
            onTogglePdf={() => {
              setExportPdf(!exportPdf);
            }}
            onSelectPath={handleSelectExportPath}
          />

          <ProgressPanel
            isProcessing={isProcessing}
            progress={progress}
            statusText={statusText}
            onExecute={handleExecute}
          />

          <LogConsole logs={logs} />
        </div>
      </div>
    </Layout>
  );
};

export default Home;
