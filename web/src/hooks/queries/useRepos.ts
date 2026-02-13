import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getRepositories, selectRepository } from '../../api/repos';
import { Repository } from '../../types';

export const REPO_KEYS = {
  all: ['repos'] as const,
  list: (page: number) => [...REPO_KEYS.all, 'list', page] as const,
};

// 저장소 목록 조회 Hook
export const useRepos = (page = 1) => {
  return useQuery({
    queryKey: REPO_KEYS.list(page),
    queryFn: () => getRepositories({ page }),
    staleTime: 1000 * 60 * 5, // 5분간 캐시 유지
  });
};

// 저장소 선택 Hook
export const useSelectRepo = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (repo: Repository) => selectRepository(repo),
    onSuccess: () => {
      // 선택 변경 시 저장소 목록과 사용자 정보(선택된 repo 정보 포함) 갱신
      queryClient.invalidateQueries({ queryKey: REPO_KEYS.all });
      queryClient.invalidateQueries({ queryKey: ['user'] });
    },
  });
};