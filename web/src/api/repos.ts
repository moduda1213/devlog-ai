import { apiClient } from './axios';
import { Repository } from '../types';

interface GetReposParams {
  page?: number;
  size?: number;
}

// 저장소 목록 조회
export const getRepositories = async ({ page = 1, size = 10 }: GetReposParams = {}): Promise<Repository[]> => {
  const { data } = await apiClient.get<Repository[]>('/api/v1/repositories', {
    params: { page, size },
  });
  return data;
};

// 저장소 선택
export const selectRepository = async (repo: Repository): Promise<Repository> => {
  // 백엔드 스키마(RepositorySelect)에 맞춰 필드 매핑
  const payload = {
    repo_name: repo.full_name || repo.repo_name,
    repo_url: repo.html_url || repo.repo_url,
  };
  
  const { data } = await apiClient.post<Repository>('/api/v1/repositories/select', payload);
  return data;
};