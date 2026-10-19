import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Porta 5173 é a origem liberada no CORS do back-end.
export default defineConfig({
  plugins: [react()],
  server: { port: 5173, strictPort: true },
});
