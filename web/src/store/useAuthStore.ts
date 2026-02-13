import { create } from 'zustand';
import { devtools } from 'zustand/middleware'

interface AuthState {
    accessToken: string | null;
    setAccessToken: (token: string | null) => void;
}

export const useAuthStore = create<AuthState>()(
    devtools( // ✅ 감싸기
        (set) => ({
            accessToken: null,
            setAccessToken: (token) => set({ accessToken: token }),
        }),
        { name: 'AuthStore' } // DevTools에 표시될 이름
    )
);

(window as any).useAuthStore = useAuthStore;