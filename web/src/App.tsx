import { useEffect, useState, useRef } from 'react';
import { RouterProvider } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Toaster } from 'react-hot-toast';
import { ErrorBoundary } from './components/common/ErrorBoundary';
import { router } from './routes';
import { useAuthStore } from './store/useAuthStore';
import { apiClient } from './api/axios';
import { Loader2 } from 'lucide-react';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

function App() {
  const [isInitializing, setIsInitializing] = useState(true);
  const setAccessToken = useAuthStore((state) => state.setAccessToken);

  // 실행 여부 체크를 위한 Ref
  const initRef = useRef(false);

  useEffect(() => {
    if (initRef.current) return;
    initRef.current = true;
    
    const initAuth = async () => {
      try {
        // 앱 시작 시 Refresh 시도 (쿠키 사용)
        const { data } = await apiClient.post('/api/v1/auth/refresh');
        if (data.access_token) {
          setAccessToken(data.access_token);
          console.log("✅ Session restored.");
        }
      } catch (error) {
        // 실패해도 괜찮음 (비로그인 상태)
        console.log("ℹ️ No active session.");
        setAccessToken(null); // 명시적 초기화
      } finally {
        setIsInitializing(false);
      }
    };

    initAuth();
  }, [setAccessToken]);

  // 초기화 중에는 라우터 렌더링 차단 (useAuth 실행 방지)
  if (isInitializing) {
    return (
      <div className="h-screen flex items-center justify-center bg-white dark:bg-github-bg">
        <Loader2 className="w-10 h-10 animate-spin text-github-btn" />
      </div>
    );
  }

  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <Toaster position="top-center" reverseOrder={false} />
        <RouterProvider router={router} />
      </QueryClientProvider>
    </ErrorBoundary>
  );
}

export default App;