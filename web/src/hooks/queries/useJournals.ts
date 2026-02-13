import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { 
  getDailyStatus,
  getJournals, 
  createJournal, 
  updateJournal, 
  deleteJournal, 
  getJournalDetail 
} from '../../api/journals';
import { Journal } from '../../types';

export const JOURNAL_KEYS = {
  all: ['journals'] as const,
  list: (params: Record<string, any>) => [...JOURNAL_KEYS.all, 'list', params] as const,
  detail: (id: string) => [...JOURNAL_KEYS.all, 'detail', id] as const,
  status: (date?: string, repoId?: string) => [...JOURNAL_KEYS.all, 'status', date, repoId] as const,
};

// 저장소 커밋 내역 유무 확인 Hook
export const useDailyStatus = (date?: string, repoId?: string) => {
  return useQuery({
    queryKey: JOURNAL_KEYS.status(date, repoId), // repoId가 바뀌면 캐시 키도 바뀜 -> 새 요청 발생
    queryFn: () => getDailyStatus(date),
    staleTime: 1000 * 60 * 5, // 5분 캐시
    enabled: !!repoId, // repoId가 있을 때만 실행 (안전장치)
  });
};
// 일지 목록 조회 Hook
export const useJournals = (page = 1, size = 10, repoId?: string) => {
  return useQuery({
    queryKey: JOURNAL_KEYS.list({ page, size, repoId }),
    queryFn: () => {
      if (!repoId) return Promise.reject(new Error("Repository ID is required"));
      return getJournals({ page, size, repository_id: repoId });
    },
    staleTime: 1000 * 60, // 1분간 캐시 유지
    placeholderData: (previousData) => previousData, // repoId가 변경되면 이전 데이터를 유지하면서 새 데이터를 가져옴 (UX 향상)
    enabled: !!repoId,
  });
};

// 일지 상세 조회 Hook
export const useJournalDetail = (id: string) => {
  return useQuery({
    queryKey: JOURNAL_KEYS.detail(id),
    queryFn: () => getJournalDetail(id),
    enabled: !!id, // ID가 있을 때만 실행
  });
};

// 일지 생성 Hook (AI)
export const useGenerateJournal = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (overwrite: boolean = true) => createJournal(overwrite),
    onSuccess: () => {
      // 생성 후 목록 갱신
      queryClient.invalidateQueries({ queryKey: JOURNAL_KEYS.all });
    },
  });
};

// 일지 수정 Hook
export const useUpdateJournal = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<Journal> }) => 
      updateJournal(id, data),
    onSuccess: (updatedJournal) => {
      // 목록 및 상세 쿼리 갱신
      queryClient.invalidateQueries({ queryKey: JOURNAL_KEYS.all });
      queryClient.setQueryData(JOURNAL_KEYS.detail(updatedJournal.id), updatedJournal);
    },
  });
};

// 일지 삭제 Hook
export const useDeleteJournal = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => deleteJournal(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: JOURNAL_KEYS.all });
    },
  });
};