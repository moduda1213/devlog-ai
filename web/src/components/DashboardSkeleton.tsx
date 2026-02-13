import React from 'react';
import { Skeleton } from './common/Skeleton';

export const DashboardSkeleton: React.FC = () => {
  return (
    <div className="max-w-5xl mx-auto py-8 px-6 space-y-8">
      {/* Hero Section Skeleton */}
      <div className="bg-white dark:bg-github-subtle border border-gray-200 dark:border-github-border rounded-xl p-6 shadow-sm">
        <div className="space-y-4">
          <div className="flex items-center gap-2">
            <Skeleton className="h-5 w-24 rounded-full" />
            <Skeleton className="h-4 w-32" />
          </div>
          <Skeleton className="h-10 w-3/4" />
          <Skeleton className="h-4 w-1/2" />
          <div className="pt-4">
            <Skeleton className="h-12 w-48 rounded-lg" />
          </div>
        </div>
      </div>

      {/* List Section Skeleton */}
      <div className="space-y-4">
        <div className="flex items-center justify-between mb-4">
          <Skeleton className="h-6 w-40" />
        </div>
        
        {[1, 2, 3].map((i) => (
          <div key={i} className="bg-white dark:bg-github-subtle border border-gray-200 dark:border-github-border rounded-lg p-5">
            <div className="flex justify-between items-start">
              <div className="space-y-3 flex-1">
                <Skeleton className="h-4 w-24" />
                <Skeleton className="h-5 w-full" />
                <div className="flex gap-4">
                  <Skeleton className="h-3 w-20" />
                  <Skeleton className="h-3 w-20" />
                </div>
              </div>
              <Skeleton className="h-5 w-5 ml-4" />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
