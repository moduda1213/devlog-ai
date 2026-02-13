import { useQuery } from '@tanstack/react-query';
import { fetchCurrentUser } from '../api/auth';
import { useAuthStore } from '../store/useAuthStore';

export const useAuth = () => {
    const accessToken = useAuthStore((state) => state.accessToken); // 토큰 상태 구독

    return useQuery({
        queryKey: ['user'],
        queryFn: fetchCurrentUser,
        retry: false,
        staleTime: Infinity,
        enabled: !!accessToken, // 토큰이 있을 때만 쿼리 실행
    });
};