// Interface que define as propriedades do componente de seleção de arquivos
export default interface FileSelectorProps {
  filePath: string;
  onSelectFile: (file?: File) => void;
}
