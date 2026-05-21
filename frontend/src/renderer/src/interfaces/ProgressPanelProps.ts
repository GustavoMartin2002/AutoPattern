// Interface que define as propriedades do componente de painel de progresso
export default interface ProgressPanelProps {
  isProcessing: boolean;
  progress: number;
  statusText: string;
  onExecute: () => void;
}
