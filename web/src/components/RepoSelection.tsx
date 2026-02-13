import React, { useState } from 'react';
import { GitBranch, Lock, Unlock, Search, CheckCircle, Loader2 } from 'lucide-react';
import { Repository } from '../types';

interface RepoSelectionProps {
  repositories: Repository[];
  onSelect: (repo: Repository) => void;
  isLoading: boolean;
  selectedRepoId?: string | number; // 현재 선택된 저장소 ID
}

export const RepoSelection: React.FC<RepoSelectionProps> = ({ 
  repositories, 
  onSelect, 
  isLoading,
  selectedRepoId 
}) => {
  const [searchTerm, setSearchTerm] = useState('');

  const filteredRepos = repositories.filter(repo => 
    (repo.name || repo.repo_name || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
    (repo.description || '').toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="w-full max-w-2xl mx-auto p-6">
      <div className="text-center mb-8">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-github-text mb-2">Select a Repository</h2>
        <p className="text-gray-500 dark:text-github-muted">
          Choose a GitHub repository to track your daily development journals.
        </p>
      </div>

      {/* Search Bar */}
      <div className="relative mb-6">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 dark:text-gray-500" size={20} />
        <input
          type="text"
          placeholder="Search repositories..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="w-full pl-10 pr-4 py-3 bg-white dark:bg-github-subtle border border-gray-200 dark:border-github-border rounded-lg focus:ring-2 focus:ring-github-accent focus:border-transparent outline-none text-gray-900 dark:text-github-text placeholder-gray-400 transition-all shadow-sm"
        />
      </div>

      {/* Repository List */}
      <div className="space-y-3 max-h-[60vh] overflow-y-auto pr-2 custom-scrollbar">
        {isLoading ? (
          <div className="flex flex-col items-center justify-center py-12 text-gray-400">
            <Loader2 className="w-8 h-8 animate-spin mb-2" />
            <p>Loading repositories...</p>
          </div>
        ) : filteredRepos.length === 0 ? (
          <div className="text-center py-12 text-gray-500 dark:text-github-muted bg-gray-50 dark:bg-github-subtle rounded-lg border border-dashed border-gray-200 dark:border-github-border">
            No repositories found matching "{searchTerm}"
          </div>
        ) : (
          filteredRepos.map((repo) => {
            const isSelected = selectedRepoId === repo.id;
            // Repository 타입 호환성 처리 (GithubRepo vs RepositoryResponse)
            const repoName = repo.name || repo.repo_name || 'Unknown Repo';
            const isPrivate = repo.private ?? false; // optional handling

            return (
              <div
                key={repo.id}
                onClick={() => onSelect(repo)}
                className={`
                  relative flex items-center justify-between p-4 rounded-lg border cursor-pointer transition-all duration-200 group
                  ${isSelected 
                    ? 'bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800 ring-1 ring-blue-200 dark:ring-blue-800' 
                    : 'bg-white dark:bg-github-subtle border-gray-200 dark:border-github-border hover:border-github-accent dark:hover:border-github-accent hover:shadow-md'
                  }
                `}
              >
                <div className="flex items-start gap-3 overflow-hidden">
                  <div className={`mt-1 p-2 rounded-md ${isSelected ? 'bg-blue-100 dark:bg-blue-900/40 text-blue-600 dark:text-blue-400' : 'bg-gray-100 dark:bg-github-bg text-gray-500 dark:text-github-muted group-hover:text-github-accent transition-colors'}`}>
                    <GitBranch size={20} />
                  </div>
                  <div className="min-w-0">
                    <div className="flex items-center gap-2 mb-0.5">
                      <h3 className={`font-semibold text-base truncate ${isSelected ? 'text-blue-700 dark:text-blue-300' : 'text-gray-900 dark:text-github-text'}`}>
                        {repoName}
                      </h3>
                      <span className="flex-shrink-0">
                        {isPrivate ? (
                          <Lock size={12} className="text-gray-400 dark:text-gray-500" />
                        ) : (
                          <Unlock size={12} className="text-gray-400 dark:text-gray-500" />
                        )}
                      </span>
                    </div>
                    {repo.description && (
                      <p className="text-sm text-gray-500 dark:text-github-muted truncate max-w-md">
                        {repo.description}
                      </p>
                    )}
                    <div className="flex items-center gap-3 mt-2 text-xs text-gray-400 dark:text-gray-500">
                      <span>Updated {new Date(repo.created_at || Date.now()).toLocaleDateString()}</span>
                      {repo.language && (
                        <span className="flex items-center gap-1">
                          <span className="w-2 h-2 rounded-full bg-yellow-400"></span>
                          {repo.language}
                        </span>
                      )}
                    </div>
                  </div>
                </div>

                {isSelected && (
                  <div className="absolute right-4 text-blue-500 dark:text-blue-400 animate-in zoom-in duration-200">
                    <CheckCircle size={24} fill="currentColor" className="text-white dark:text-github-bg" />
                  </div>
                )}
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};