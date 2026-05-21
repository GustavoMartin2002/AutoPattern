// Interface que define as propriedades do componente de opções de exportação
export default interface ExportOptionsProps {
  exportExcel: boolean;
  exportPdf: boolean;
  exportPath: string;
  onToggleExcel: () => void;
  onTogglePdf: () => void;
  onSelectPath: () => void;
}
