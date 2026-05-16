import type React from "react";

const appVersion = import.meta.env.PACKAGE_VERSION as string | undefined;

// Componente responsável por definir o layout da aplicação
const Layout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return (
    <div className="relative flex h-auto min-h-screen w-full flex-col overflow-x-hidden bg-background-light dark:bg-[#0b0f17] text-slate-900 dark:text-slate-100">
      <div className="layout-container flex h-full grow flex-col">
        <header className="flex items-center justify-between whitespace-nowrap border-b border-solid border-slate-200 dark:border-slate-800 px-4 sm:px-8 xl:px-20 py-4 bg-white dark:bg-[#0b0f17]">
          <div className="flex items-center m-auto gap-4">
            <h1 className="text-slate-900 dark:text-white text-4xl font-bold leading-tight tracking-tight select-none">
              AutoPattern
            </h1>
          </div>
        </header>

        <main className="flex-1 flex justify-center py-6 sm:py-8 px-4 sm:px-8 xl:px-20">
          <div className="max-w-[1280px] w-full flex flex-col gap-6 sm:gap-8 overflow-hidden">
            {children}
          </div>
        </main>

        <footer className="px-4 sm:px-8 xl:px-20 py-6 border-t border-slate-200 dark:border-slate-800 flex flex-col sm:flex-row gap-4 justify-between sm:items-center text-slate-500 dark:text-slate-500 text-xs font-medium">
          <span className="text-primary font-bold select-none">
            BETA {`${appVersion}`}
          </span>
          <div className="flex gap-4">
            <a
              href="https://github.com/GustavoMartin2002/AutoPattern/issues"
              target="_blank"
              rel="noopener noreferrer"
              className="text-white/70 underline underline-offset-2 hover:text-primary transition-colors select-none"
            >
              Suporte Técnico
            </a>
            <a
              href="https://github.com/GustavoMartin2002/AutoPattern?tab=readme-ov-file#manual-do-usu%C3%A1rio"
              target="_blank"
              rel="noopener noreferrer"
              className="text-white/70 underline underline-offset-2 hover:text-primary transition-colors select-none"
            >
              Manual do Usuário
            </a>
          </div>
        </footer>
      </div>
    </div>
  );
};

export default Layout;
