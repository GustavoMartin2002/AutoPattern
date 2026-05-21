import { useState } from "react";

import type TagManagerProps from "@renderer/interfaces/TagManagerProps";
import type React from "react";

// Componente responsável por gerenciar as tags XML
const TagManager: React.FC<TagManagerProps> = ({
  tags,
  onAddTag,
  onRemoveTag,
}) => {
  const [newTag, setNewTag] = useState("");

  // Função responsável por adicionar tags
  const handleAdd = () => {
    if (newTag.trim()) {
      const splitTags = newTag
        .split(",")
        .map((t) => t.trim())
        .filter((t) => t !== "");

      splitTags.forEach((tag) => {
        // limite de 30 tags deferido para handleExecute
        onAddTag(tag);
      });
      setNewTag("");
    }
  };

  // Função responsável por adicionar tags ao pressionar Enter
  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      e.preventDefault();
      handleAdd();
    }
  };

  return (
    <section className="bg-white dark:bg-[#111927] p-8 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm">
      <header className="flex items-center gap-2 mb-4">
        <span className="flex items-center justify-center w-7 h-7 rounded-full bg-primary text-white text-base font-bold select-none">
          2.
        </span>
        <h2 className="text-slate-900 dark:text-white text-lg font-bold">
          Mapeamento de Tags
        </h2>
      </header>
      <div className="flex flex-col gap-4">
        <p className="text-slate-700 dark:text-slate-300 text-sm font-medium italic">
          Adicione o nome das tags XML que deseja extrair os dados
        </p>
        <div className="flex gap-2">
          <input
            type="text"
            value={newTag}
            onChange={(e) => {
              setNewTag(e.target.value);
            }}
            onKeyDown={handleKeyDown}
            disabled={(tags ?? []).length >= 30}
            placeholder={
              (tags ?? []).length >= 30
                ? "Limite máximo de tags (30) atingido"
                : "Ex: Código, Nome, Valor..."
            }
            className="flex-1 rounded-lg border border-slate-300 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 px-4 text-slate-900 dark:text-slate-100 focus:ring-2 focus:ring-primary/50 focus:border-primary outline-none transition-all select-none disabled:opacity-50 disabled:cursor-not-allowed"
          />
          <button
            onClick={handleAdd}
            disabled={(tags ?? []).length >= 30}
            className="flex items-center justify-center w-12 h-12 rounded-lg bg-primary/10 dark:bg-primary text-primary dark:text-white hover:bg-primary/20 hover:scale-105 active:scale-95 transition-all border border-primary/20 dark:border-primary focus-visible:ring-2 focus-visible:ring-primary outline-none text-base select-none disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100"
          >
            +
          </button>
        </div>
        <div className="flex flex-wrap gap-2 mt-2">
          {(tags ?? []).map((tag) => (
            <span
              key={tag}
              className="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-100 dark:bg-primary/50 text-slate-700 dark:text-slate-300 text-xs font-medium border border-slate-200 dark:border-primary select-none"
            >
              {tag}
              <span
                className="text-[14px] text-slate-700 dark:text-slate-300 opacity-60 cursor-pointer hover:opacity-100 select-none"
                onClick={() => {
                  onRemoveTag(tag);
                }}
              >
                X
              </span>
            </span>
          ))}
        </div>
      </div>
    </section>
  );
};

export default TagManager;
