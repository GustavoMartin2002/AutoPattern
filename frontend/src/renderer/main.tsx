import React from "react";
import ReactDOM from "react-dom/client";
import Home from "./src/presentation/pages/Home";
import "./src/presentation/styles/global.css";

// Renderiza o componente Home na DOM
ReactDOM.createRoot(document.getElementById("root") as HTMLElement).render(
  <React.StrictMode>
    <Home />
  </React.StrictMode>
);
