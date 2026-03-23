// Interface que define as propriedades do componente de gerenciamento de tags
export default interface TagManagerProps {
  tags: string[] | null;
  onAddTag: (tag: string) => void;
  onRemoveTag: (tag: string) => void;
}
