import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import { RepoSelection } from '../components/RepoSelection';
import { useRepos, useSelectRepo } from '../hooks/queries/useRepos';
import { Repository } from '../types';

export default function RepoSelectionPage() {
  const navigate = useNavigate();
  const { data: repositories, isLoading } = useRepos();
  const selectRepoMutation = useSelectRepo();

  const handleSelect = (repo: Repository) => {
    selectRepoMutation.mutate(repo, {
      onSuccess: () => {
        toast.success(`${repo.name || repo.repo_name} 저장소가 선택되었습니다.`);
        // 선택 성공 시 대시보드로 이동
        navigate('/');
      },
      onError: (error) => {
        console.error("Failed to select repository:", error);
        toast.error("저장소 선택에 실패했습니다. 다시 시도해주세요.");
      }
    });
  };

  // 현재 선택된 저장소 찾기
  const selectedRepo = repositories?.find(r => r.is_selected);

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-github-bg flex items-center justify-center">
      <RepoSelection
        repositories={repositories || []}
        isLoading={isLoading}
        onSelect={handleSelect}
        selectedRepoId={selectedRepo?.id}
      />
    </div>
  );
}