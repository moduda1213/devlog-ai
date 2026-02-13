import { apiClient } from './axios';
import { Journal } from '../types';

export interface JournalStatus {
  date: string;
  has_journal: boolean;
  has_commits: boolean;
  can_generate: boolean;
}

interface GetJournalsParams {
  page?: number;
  size?: number;
  start_date?: string;
  end_date?: string;
  repository_id?: string; 
}

interface JournalListResponse {
  items: Journal[];
  total: number;
  page: number;
  size: number;
}

// 저장소 커밋 내역 유무 확인
export const getDailyStatus = async (date?: string): Promise<JournalStatus> => {
  const params = date ? { date } : {};
  const { data } = await apiClient.get('/api/v1/journals/daily-status', { params });
  return data;
};

// 일지 목록 조회
export const getJournals = async (params: GetJournalsParams = {}): Promise<JournalListResponse> => {
  const { data } = await apiClient.get<JournalListResponse>('/api/v1/journals', { params });
  return data;
};

// 일지 상세 조회
export const getJournalDetail = async (id: string): Promise<Journal> => {
  const { data } = await apiClient.get<Journal>(`/api/v1/journals/${id}`);
  return data;
};

// 일지 생성 (AI)
export const createJournal = async (overwrite = true): Promise<Journal> => {
  const { data } = await apiClient.post<Journal>('/api/v1/journals/', null, {
    params: { overwrite },
  });
  return data;
};

// 일지 수정
export const updateJournal = async (id: string, journal: Partial<Journal>): Promise<Journal> => {
  const { data } = await apiClient.patch<Journal>(`/api/v1/journals/${id}`, journal);
  return data;
};

// 일지 삭제
export const deleteJournal = async (id: string): Promise<void> => {
  await apiClient.delete(`/api/v1/journals/${id}`);
};