import React, { useRef } from "react";
import FileSelectorProps from "@renderer/interfaces/FileSelectorProps";

// Componente responsável pela seleção de arquivos XML
const FileSelector: React.FC<FileSelectorProps> = ({
  filePath,
  onSelectFile,
}) => {
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Função responsável por selecionar arquivos XML no modo desktop
  const handleClick = (e: React.MouseEvent) => {
    e.preventDefault();
    if (window.electron) {
      onSelectFile();
    } else {
      fileInputRef.current?.click();
    }
  };

  // Função responsável por selecionar arquivos XML no modo web
  const handleWebFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) onSelectFile(file);
  };

  return (
    <section className="bg-white dark:bg-[#111927] p-8 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm">
      <header className="flex items-center gap-2 mb-4">
        <span className="flex items-center justify-center w-7 h-7 rounded-full bg-primary text-white text-base font-bold select-none">
          1.
        </span>
        <h2 className="text-slate-900 dark:text-white text-lg font-bold">
          Seleção de Arquivo
        </h2>
      </header>
      <div className="flex flex-col gap-4">
        <p className="text-slate-700 dark:text-slate-300 text-sm font-medium italic">
          Arquivo XML de Origem
        </p>
        <label className="flex flex-col gap-2">
          <div className="flex w-full items-stretch group">
            <input
              type="text"
              readOnly
              value={filePath || ""}
              placeholder="Selecione um arquivo..."
              className="flex-1 rounded-l-lg border border-slate-300 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 px-4 text-slate-900 dark:text-slate-100 focus:ring-1 focus:ring-primary outline-none select-none"
            />
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleWebFileChange}
              className="hidden"
              accept=".xml"
            />
            <button
              onClick={handleClick}
              className="flex items-center justify-center px-4 rounded-r-lg text-white transition-colors bg-primary hover:bg-primary/80 select-none"
            >
              Selecionar
            </button>
          </div>
        </label>
      </div>
    </section>
  );
};

export default FileSelector;
