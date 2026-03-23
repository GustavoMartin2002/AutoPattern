// Interface que define a estrutura de erro retornada pela API
export default interface ApiError {
  detail: string | Array<{ loc: string[]; msg: string; type: string }>;
  message?: string;
}
