import React from 'react';
import { AlertCircle, RefreshCcw } from 'lucide-react';

interface QueryErrorViewProps {
  message?: string;
  onRetry: () => void;
}

export const QueryErrorView: React.FC<QueryErrorViewProps> = ({ 
  message = "데이터를 불러오는 중 오류가 발생했습니다.", 
  onRetry 
}) => {
  return (
    <div className="flex min-h-[400px] w-full flex-col items-center justify-center p-8 text-center">
      <div className="mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-red-100 text-red-600 dark:bg-red-900/20 dark:text-red-400">
        <AlertCircle size={32} />
      </div>
      <h3 className="mb-2 text-xl font-bold text-gray-900 dark:text-white">로딩 실패</h3>
      <p className="mb-6 max-w-xs text-gray-500 dark:text-github-muted">
        {message}
      </p>
      <button
        onClick={onRetry}
        className="flex items-center gap-2 rounded-lg bg-github-btn px-6 py-2.5 font-semibold text-white transition-all hover:bg-github-btn-hover active:scale-95 shadow-md"
      >
        <RefreshCcw size={18} />
        다시 시도
      </button>
    </div>
  );
};
