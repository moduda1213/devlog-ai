import axios from 'axios';
import { useAuthStore } from '../store/useAuthStore';

const baseURL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const apiClient = axios.create({
    baseURL,
    withCredentials: true,
    headers: {
        'Content-Type': 'application/json',
    },
});

apiClient.interceptors.request.use(
    (config) => {
        const token = useAuthStore.getState().accessToken;
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => Promise.reject(error)
);

// 중복 갱신 방지를 위한 변수
let isRefreshing = false;
let refreshPromise: Promise<string> | null = null;

apiClient.interceptors.response.use(
    (response) => response,
    async (error) => {
        const originalRequest = error.config;

        // Refresh 요청 자체가 실패한 경우 -> 즉시 종료
        if (originalRequest.url?.includes('/auth/refresh')) {
            useAuthStore.getState().setAccessToken(null);
            return Promise.reject(error);
        }

        // 401 에러이고, 아직 재시도 안 했을 때
        if (error.response?.status === 401 && !originalRequest._retry) {
            originalRequest._retry = true;

            // 이미 갱신 중이라면? -> 진행 중인 Promise 결과를 기다림 (요청 중복 방지)
            if (isRefreshing && refreshPromise) {
                try {
                    const newToken = await refreshPromise;
                    originalRequest.headers.Authorization = `Bearer ${newToken}`;
                    return apiClient(originalRequest);
                } catch (e) {
                    return Promise.reject(error);
                }
            }

            // 갱신 시작 (Lock 걸기)
            isRefreshing = true;

            refreshPromise = (async () => {
                try {
                    const { data } = await axios.post(
                        `${baseURL}/api/v1/auth/refresh`,
                        {},
                        { withCredentials: true }
                    );
                    const newToken = data.access_token;
                    useAuthStore.getState().setAccessToken(newToken);
                    return newToken;
                } catch (refreshError) {
                    useAuthStore.getState().setAccessToken(null);
                    throw refreshError;
                } finally {
                    isRefreshing = false;
                    refreshPromise = null; // Lock 해제
                }
            })();

            try {
                const newToken = await refreshPromise;
                originalRequest.headers.Authorization = `Bearer ${newToken}`;
                return apiClient(originalRequest);
            } catch (e) {
                return Promise.reject(error);
            }
        }
        return Promise.reject(error);
    }
);