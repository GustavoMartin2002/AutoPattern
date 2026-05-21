// Interface para mensagens recebidas via WebSocket durante o processamento
export default interface WebSocketMessage {
  progress?: number;
  message?: string;
}
