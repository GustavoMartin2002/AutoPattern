import { useEffect, useRef } from "react";

import type LogConsoleProps from "@renderer/interfaces/LogConsoleProps";
import type LogEntry from "@renderer/interfaces/LogEntry";
import type React from "react";

// Componente responsável por exibir os logs
const LogConsole: React.FC<LogConsoleProps> = ({ logs }) => {
  const containerRef = useRef<HTMLDivElement>(null);

  // Hook responsável por garantir o Auto-Scroll do console acompanhando os mais recentes logs registrados
  useEffect(() => {
    if (containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight;
    }
  }, [logs]);

  // Função responsável por definir as cores dos logs
  const getColorClasses = (type: LogEntry["type"]) => {
    switch (type) {
      case "success":
        return "text-emerald-400";
      case "error":
        return "text-red-400";
      case "warning":
        return "text-amber-400";
      case "process":
        return "text-sky-400";
      case "info":
        return "text-slate-300/90";
      default:
        return "text-slate-400";
    }
  };

  return (
    <aside
      ref={containerRef}
      className="bg-slate-900/80 backdrop-blur-sm rounded-xl p-5 font-mono text-[13px] leading-relaxed border border-slate-800 h-40 overflow-y-auto"
      aria-label="Console de Logs"
    >
      {logs.map((log) => (
        <p key={log.id} className={getColorClasses(log.type)}>
          [{log.type.toUpperCase()}] {log.message}
        </p>
      ))}
      {logs.length === 0 && (
        <p className="text-slate-500 italic">
          [SYSTEM] Aguardando inicialização...
        </p>
      )}
    </aside>
  );
};

export default LogConsole;
