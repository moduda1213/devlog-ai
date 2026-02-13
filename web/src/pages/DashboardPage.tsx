import { useState, useMemo, useCallback } from 'react';
import { Navigate, useNavigate } from 'react-router-dom';
import { Loader2 } from 'lucide-react';
import toast from 'react-hot-toast';
import { Dashboard } from '../components/Dashboard';
import { DashboardSkeleton } from '../components/DashboardSkeleton';
import { JournalDetail } from '../components/JournalDetail';
import { QueryErrorView } from '../components/common/QueryErrorView';
import { useRepos } from '../hooks/queries/useRepos';
import { 
  useDailyStatus,
  useJournals, 
  useGenerateJournal, 
  useUpdateJournal, 
  useDeleteJournal 
} from '../hooks/queries/useJournals';
import { Journal } from '../types';
import { useAuth } from '../hooks/useAuth';

export default function DashboardPage() {
  const navigate = useNavigate();
  
  // State
  const [selectedJournal, setSelectedJournal] = useState<Journal | null>(null);
  
  const { data: user } = useAuth();

  // Queries
  const { 
    data: repos, 
    isLoading: isReposLoading, 
    isError: isReposError,
    refetch: refetchRepos 
  } = useRepos();
  
  // Computed Values
  const currentRepo = useMemo(() => {
    // User 정보에 selected_repo_id가 있으면 그걸로 찾기 (ID 매칭이 가장 정확)
    if (user?.selected_repo_id && repos) {
        // repos의 id는 string | number 이므로 비교 시 주의
        const found = repos.find(r => String(r.id) === user.selected_repo_id);
        if (found) return found;
    }
    // fallback: 기존 방식 (is_selected 플래그)
    return repos?.find(r => r.is_selected);
  }, [repos, user]);
  
  // user.selected_repo_id를 우선 사용
  // currentRepo가 없을 수도 있으므로 안전하게 처리
  const repoIdToUse = user?.selected_repo_id || (currentRepo?.id ? String(currentRepo.id) : undefined);
  
  const { data: dailyStatus, isLoading: isStatusLoading } = useDailyStatus(undefined, repoIdToUse);

  const { 
    data: journalData, 
    isLoading: isJournalsLoading, 
    isError: isJournalsError,
    refetch: refetchJournals 
  } = useJournals(1, 10, repoIdToUse);
  
  // Mutations
  const generateMutation = useGenerateJournal();
  const updateMutation = useUpdateJournal();
  const deleteMutation = useDeleteJournal();

  const journals = useMemo(() => {
    return journalData?.items || [];
  }, [journalData]);

  // 오늘 날짜 일지가 있는지 확인 (YYYY-MM-DD)
  const hasCommits = dailyStatus?.has_commits || false;

  // Handlers
  const handleRetry = useCallback(() => {
    refetchRepos();
    refetchJournals();
  }, [refetchRepos, refetchJournals]);

  const handleGenerate = useCallback(() => {
    if (!currentRepo) {
      toast.error("먼저 저장소를 선택해주세요.");
      return;
    }
    
    const loadingToast = toast.loading("AI가 일지를 생성하고 있습니다...");
    
    generateMutation.mutate(true, {
      onSuccess: () => {
        toast.success("일지가 생성되었습니다!", { id: loadingToast });
      },
      onError: (error) => {
        console.error("Generate failed:", error);
        toast.error("일지 생성에 실패했습니다.", { id: loadingToast });
      }
    });
  }, [currentRepo, generateMutation]);

  const handleUpdate = useCallback((updatedJournal: Journal) => {
    updateMutation.mutate(
      { id: updatedJournal.id, data: updatedJournal },
      {
        onSuccess: () => {
          toast.success("일지가 수정되었습니다.");
          setSelectedJournal(null);
        },
        onError: () => {
          toast.error("일지 수정에 실패했습니다.");
        }
      }
    );
  }, [updateMutation]);

  const handleDelete = useCallback((id: string) => {
    if (!window.confirm("정말 이 일지를 삭제하시겠습니까?")) return;

    deleteMutation.mutate(id, {
      onSuccess: () => {
        toast.success("일지가 삭제되었습니다.");
        setSelectedJournal(null);
      },
      onError: () => {
        toast.error("일지 삭제에 실패했습니다.");
      }
    });
  }, [deleteMutation]);

  const handleChangeRepo = useCallback(() => {
    navigate('/repo-select');
  }, [navigate]);

  const handleViewJournal = useCallback((journal: Journal) => {
    setSelectedJournal(journal);
  }, []);

  const handleBackToList = useCallback(() => {
    setSelectedJournal(null);
  }, []);

  // Loading View
  if (isReposLoading || isJournalsLoading) {
    return <DashboardSkeleton />;
  }

  // Error View
  if (isReposError || isJournalsError) {
    return (
      <div className="flex h-[calc(100vh-4rem)] items-center justify-center bg-gray-50 dark:bg-github-bg">
        <QueryErrorView onRetry={handleRetry} />
      </div>
    );
  }

  // Repo Selection Needed View
  if (!currentRepo) {
    return <Navigate to="/repo-select" replace />;
  }

  // Detail View
  if (selectedJournal) {
    return (
      <JournalDetail
        journal={selectedJournal}
        onBack={handleBackToList}
        onUpdate={handleUpdate}
        onDelete={handleDelete}
      />
    );
  }

  // Main Dashboard View
  return (
    <>
      <Dashboard
        journals={journals}
        hasCommits={hasCommits}
        onGenerate={handleGenerate}
        onViewJournal={handleViewJournal}
        onChangeRepo={handleChangeRepo}
        currentRepo={currentRepo}
      />
      
      {/* Loading Overlay (Generating) */}
      {generateMutation.isPending && (
        <div className="fixed inset-0 z-50 flex flex-col items-center justify-center bg-black/50 backdrop-blur-sm">
          <Loader2 className="h-12 w-12 animate-spin text-white mb-4" />
          <p className="text-white font-medium text-lg animate-pulse">
            AI가 오늘의 개발 일지를 작성하고 있습니다...
          </p>
        </div>
      )}
    </>
  );
}