import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface UIState {
  isDarkMode: boolean;
  toggleTheme: () => void;
  applyTheme: (isDark: boolean) => void;
}

export const useUIStore = create<UIState>()(
  persist(
    (set, get) => ({
      isDarkMode: window.matchMedia('(prefers-color-scheme: dark)').matches,
      toggleTheme: () => {
        const nextMode = !get().isDarkMode;
        set({ isDarkMode: nextMode });
        get().applyTheme(nextMode);
      },
      applyTheme: (isDark: boolean) => {
        if (isDark) {
          document.documentElement.classList.add('dark');
        } else {
          document.documentElement.classList.remove('dark');
        }
      },
    }),
    {
      name: 'ui-storage',
      onRehydrateStorage: () => (state) => {
        // 로컬 스토리지에서 데이터를 읽어온 후 초기 테마 적용
        if (state) {
          state.applyTheme(state.isDarkMode);
        }
      },
    }
  )
);
