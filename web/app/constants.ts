import { getEnvVar } from "@/utils";

export const API_ROOT = getEnvVar('NEXT_PUBLIC_API_ROOT');

export const ORDERS_ENDPOINT = `${API_ROOT}/api/v1/order`;