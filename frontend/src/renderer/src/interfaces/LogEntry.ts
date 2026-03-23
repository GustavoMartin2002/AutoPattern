// Interface que define a estrutura de uma entrada de log
export default interface LogEntry {
  id: string;
  type: "info" | "error" | "success" | "warning" | "process";
  message: string;
}
