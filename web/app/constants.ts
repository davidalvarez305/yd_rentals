const isProd = process.env.NODE_ENV === 'production';

// Server Routes
export const API_ROOT = isProd ? '' : 'http://127.0.0.1:8000';
export const ORDERS_ENDPOINT = `${API_ROOT}/api/v1/orders`;