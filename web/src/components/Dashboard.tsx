import React, { memo } from 'react';
import { Calendar, ChevronRight, GitCommit, Zap, BookOpen, Settings } from 'lucide-react';
import { Journal, Repository } from '../types';

interface DashboardProps {
  journals: Journal[];
  hasCommits: boolean;
  onGenerate: () => void;
  onViewJournal: (journal: Journal) => void;
  currentRepo: Repository;
  onChangeRepo: () => void;
}

export const Dashboard: React.FC<DashboardProps> = memo(({ 
  journals, 
  hasCommits, 
  onGenerate, 
  onViewJournal,
  currentRepo,
  onChangeRepo
}) => {
  return (
    <div className="max-w-5xl mx-auto py-8 px-6 space-y-8">
      {/* Hero / Stats Section */}
      <div className="bg-gradient-to-br from-white to-gray-100 dark:from-github-subtle dark:to-github-bg border border-gray-200 dark:border-github-border rounded-xl p-6 shadow-sm relative overflow-hidden">
        <div className="absolute top-0 right-0 w-64 h-64 bg-blue-500/10 dark:bg-github-btn/5 rounded-full blur-3xl -translate-y-1/2 translate-x-1/2 pointer-events-none"></div>
        <div className="relative z-10 flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-2">
              <span className="px-2 py-0.5 rounded-full bg-blue-500/10 text-blue-600 dark:text-blue-400 text-xs font-medium border border-blue-200 dark:border-blue-900/30">
                {currentRepo.name}
              </span>
              <button 
                onClick={onChangeRepo}
                className="flex items-center gap-1 text-xs text-gray-500 dark:text-github-muted hover:text-github-btn transition-colors"
                title="Change repository"
              >
                <Settings size={12} />
                <span>Change</span>
              </button>
              <span className="ml-2 text-xs text-gray-400 dark:text-github-muted/50">Today's Activity</span>
            </div>
            
            {hasCommits ? (
              <>
                <h2 className="text-2xl sm:text-3xl font-bold text-gray-900 dark:text-white mb-2 leading-tight">
                  <span className="text-github-btn">New commits detected.</span>
                </h2>
                <p className="text-sm sm:text-base text-gray-600 dark:text-github-muted max-w-lg">
                  Your work on <strong>{currentRepo.name}</strong> is ready to be logged. Generate a summary now.
                </p>
              </>
            ) : (
              <>
                <h2 className="text-2xl sm:text-3xl font-bold text-gray-900 dark:text-white mb-2 leading-tight">
                  There are no commits yet today.
                </h2>
                <p className="text-sm sm:text-base text-gray-600 dark:text-github-muted max-w-lg">
                  Make some changes to <strong>{currentRepo.name}</strong> to start tracking your daily progress.
                </p>
              </>
            )}
          </div>
          <button 
            onClick={onGenerate}
            disabled={!hasCommits}
            className={`
              flex items-center gap-2 px-6 py-3 rounded-lg font-semibold text-white shadow-lg transition-all
              ${hasCommits
                ? 'bg-github-btn hover:bg-github-btn-hover hover:scale-105 active:scale-95' 
                : 'bg-gray-400 dark:bg-gray-700 cursor-not-allowed opacity-50 grayscale'}
            `}
          >
            <Zap size={18} className={hasCommits ? "fill-current" : ""} />
            Generate Today's Journal
          </button>
        </div>
      </div>

      {/* Journals List */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-github-text flex items-center gap-2">
            <Calendar size={20} className="text-gray-500 dark:text-github-muted" />
            Previous Journals
          </h3>
        </div>

        <div className="space-y-4">
          {journals.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-16 border border-dashed border-gray-300 dark:border-github-border rounded-xl bg-gray-50/50 dark:bg-github-subtle/30">
              <div className="w-16 h-16 bg-gray-100 dark:bg-github-bg rounded-full flex items-center justify-center mb-4 text-gray-400 dark:text-github-muted shadow-sm border border-gray-200 dark:border-github-border">
                <BookOpen size={28} />
              </div>
              <h4 className="text-lg font-bold text-gray-900 dark:text-github-text mb-1">
                No journal entries have been created yet.
              </h4>
              <p className="text-gray-500 dark:text-github-muted">
                Commit and create your first journal entry!
              </p>
            </div>
          ) : (
            journals.map(journal => (
              <div 
                key={journal.id}
                onClick={() => onViewJournal(journal)}
                className="group bg-white dark:bg-github-subtle border border-gray-200 dark:border-github-border hover:border-github-accent dark:hover:border-github-accent rounded-lg p-4 sm:p-5 cursor-pointer transition-all hover:shadow-md"
              >
                <div className="flex items-center justify-between gap-4">
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center gap-3 mb-1.5">
                      <span className="font-mono text-xs sm:text-sm text-github-accent font-semibold">{journal.date}</span>
                    </div>
                    <p className="text-gray-700 dark:text-github-text font-medium line-clamp-1 mb-2 text-sm sm:text-base">{journal.summary}</p>
                    <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-[10px] sm:text-xs text-gray-500 dark:text-github-muted">
                      <span className="flex items-center gap-1">
                        <GitCommit size={14} className="flex-shrink-0" />
                        {journal.commit_count} <span className="hidden xs:inline">commits</span><span className="xs:hidden">cmt</span>
                      </span>
                      <span className="flex items-center gap-1">
                        <span className="w-1.5 h-1.5 rounded-full bg-green-500 flex-shrink-0"></span>
                        {journal.main_tasks?.length || 0} <span className="hidden xs:inline">tasks</span><span className="xs:hidden">tsk</span>
                      </span>
                    </div>
                  </div>
                  <div className="text-gray-300 dark:text-github-border group-hover:text-github-accent transition-colors flex-shrink-0">
                    <ChevronRight size={20} />
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
});