import type ExportOptionsProps from "@renderer/interfaces/ExportOptionsProps";
import type React from "react";

// Componente responsável por gerenciar as opções de exportação
const ExportOptions: React.FC<ExportOptionsProps> = ({
  exportExcel,
  exportPdf,
  exportPath,
  onToggleExcel,
  onTogglePdf,
  onSelectPath,
}) => {
  // Verifica se está rodando no modo desktop
  const isElectron = !!window.electron;

  return (
    <section className="bg-white dark:bg-[#111927] p-8 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm">
      <header className="flex items-center gap-2 mb-4">
        <span className="flex items-center justify-center w-7 h-7 rounded-full bg-primary text-white text-base font-bold select-none">
          3.
        </span>
        <h2 className="text-slate-900 dark:text-white text-lg font-bold">
          Opções de Exportação
        </h2>
      </header>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <label className="flex items-center gap-3 p-4 rounded-lg border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-800/50 cursor-pointer hover:border-primary/50 hover:bg-slate-100 dark:hover:bg-slate-800 transition-all focus-within:ring-2 focus-within:ring-primary/50">
          <input
            type="checkbox"
            checked={exportExcel}
            onChange={onToggleExcel}
            className="w-5 h-5 rounded border-slate-300 dark:border-slate-700 text-primary accent-blue-600 focus:ring-0"
          />
          <div className="flex flex-col select-none">
            <span className="text-sm font-bold text-slate-900 dark:text-white">
              Excel (.xlsx)
            </span>
            <span className="text-[12px] text-slate-500">
              Planilha Estruturada
            </span>
          </div>
        </label>
        <label className="flex items-center gap-3 p-4 rounded-lg border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-800/50 cursor-pointer hover:border-primary/50 hover:bg-slate-100 dark:hover:bg-slate-800 transition-all focus-within:ring-2 focus-within:ring-primary/50">
          <input
            type="checkbox"
            checked={exportPdf}
            onChange={onTogglePdf}
            className="w-5 h-5 rounded border-slate-300 dark:border-slate-700 text-primary accent-blue-600 focus:ring-0"
          />
          <div className="flex flex-col select-none">
            <span className="text-sm font-bold text-slate-900 dark:text-white">
              PDF (.pdf)
            </span>
            <span className="text-[12px] text-slate-500">Relatório Visual</span>
          </div>
        </label>
      </div>
      <div className="mt-6 flex flex-col gap-2">
        <div className="flex justify-between items-center">
          <span className="text-slate-700 dark:text-slate-300 text-sm font-medium italic">
            Destino da Exportação
          </span>
          <span className="text-[10px] text-primary bg-primary/10 px-2 py-0.5 rounded-full font-bold uppercase tracking-wider select-none">
            {isElectron ? "Desktop Mode" : "Web Mode"}
          </span>
        </div>
        <div className="flex w-full items-stretch group">
          <input
            type="text"
            readOnly
            value={
              isElectron ? exportPath : `Pasta "outputs" na raiz do projeto`
            }
            placeholder={
              isElectron
                ? "Selecione o caminho de exportação"
                : "Sincronizado via Docker"
            }
            className={`
              flex-1 rounded-l-lg border
              ${
                isElectron
                  ? "border-slate-300 dark:border-slate-700 bg-slate-50 dark:bg-slate-800"
                  : "border-slate-200 dark:border-slate-800 bg-slate-100/50 dark:bg-slate-900/50 italic opacity-80"
              }
              px-4 text-slate-900 dark:text-slate-100 focus:ring-2 focus:ring-primary/50 outline-none transition-all select-none`}
          />
          <button
            onClick={onSelectPath}
            disabled={!isElectron}
            className={`
              flex items-center justify-center px-4 rounded-r-lg transition-colors select-none
              ${
                isElectron
                  ? "bg-primary hover:bg-primary/80 text-white"
                  : "bg-slate-200 dark:bg-slate-800 text-slate-400 dark:text-slate-600 cursor-not-allowed"
              }`}
          >
            Selecionar
          </button>
        </div>
      </div>
    </section>
  );
};

export default ExportOptions;
