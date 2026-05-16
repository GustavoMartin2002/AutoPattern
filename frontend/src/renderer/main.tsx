import React from "react";
import ReactDOM from "react-dom/client";

import Home from "./src/presentation/pages/Home";
import "./src/presentation/styles/global.css";

// Renderiza o componente Home na DOM
const rootElement = document.getElementById("root");
if (!rootElement) throw new Error("Falha ao encontrar o elemento raiz do DOM.");

ReactDOM.createRoot(rootElement).render(
  <React.StrictMode>
    <Home />
  </React.StrictMode>,
);
