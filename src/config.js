// 1. 개별 export만 남깁니다. (export default 삭제 권장)
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'https://pinjzwk0qi.execute-api.us-east-1.amazonaws.com/prod';
export const WS_URL = import.meta.env.VITE_WS_URL || 'wss://23ubxp2xcj.execute-api.us-east-1.amazonaws.com/prod';

export const IS_DEVELOPMENT = import.meta.env.DEV;
export const IS_PRODUCTION = import.meta.env.PROD;

export const DEFAULT_ENGINE = "11";
export const STORAGE_PREFIX = "tem_";

export const ADMIN_EMAIL = import.meta.env.VITE_ADMIN_EMAIL;
export const COMPANY_DOMAIN = import.meta.env.VITE_COMPANY_DOMAIN || 'sedaily.com'; 

// 맨 밑에 있던 "export default { ... }" 이 부분을 아예 지우세요.