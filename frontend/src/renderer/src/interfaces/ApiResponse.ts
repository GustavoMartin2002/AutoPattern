// Interface que define a estrutura de resposta da API
export default interface ApiResponse {
  success: boolean;
  message: string;
  generated_files: string[];
}
