import React from "react";
import ProgressPanelProps from "@renderer/interfaces/ProgressPanelProps";

// Componente responsável por gerenciar o progresso e a execução
const ProgressPanel: React.FC<ProgressPanelProps> = ({
  isProcessing,
  progress,
  statusText,
  onExecute,
}) => {
  return (
    <section className="bg-[#1e293b] dark:bg-[#111927] text-white p-8 rounded-2xl border border-slate-700/50 shadow-2xl flex flex-col gap-6 relative overflow-hidden">
      <header className="sr-only">
        <h2>Painel de Progresso e Execução</h2>
      </header>
      <div className="relative z-10 flex flex-col gap-6">
        <button
          onClick={onExecute}
          disabled={isProcessing}
          className={`
            w-full h-16 text-primary uppercase font-black text-xl rounded-lg transition-all transform flex items-center justify-center gap-2 shadow-lg select-none cursor-pointer tracking-wider
            ${isProcessing
              ? "bg-slate-300 cursor-not-allowed opacity-80"
              : "bg-white hover:scale-[1.03] active:scale-95"
            }`
          }
        >
          {isProcessing ? "PROCESSANDO..." : "GERAR AUTOMAÇÃO"}
        </button>

        {/* Status do Progresso */}
        <div className="flex flex-col gap-3 select-none">
          <div className="flex justify-between items-end">
            <div className="flex flex-col">
              <span className="text-slate-400 text-xs font-medium uppercase tracking-widest">
                Status Atual
              </span>
              <span className="text-white text-sm font-semibold">
                {statusText || "Aguardando ação..."}
              </span>
            </div>
            <span className="text-white text-sm font-bold">{progress}%</span>
          </div>
          <div className="w-full bg-white/10 rounded-full h-3">
            <div
              className="bg-white h-3 rounded-full transition-all duration-500"
              style={{ width: `${progress}%` }}
            ></div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default ProgressPanel;
