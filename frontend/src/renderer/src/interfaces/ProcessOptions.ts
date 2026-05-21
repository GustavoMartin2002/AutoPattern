// Interface que define as opções de processamento
export default interface ProcessOptions {
  tags: string[] | null;
  exportExcel: boolean;
  exportPdf: boolean;
  exportPath: string;
}
