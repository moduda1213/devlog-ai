import React from 'react';
import { Github, Folder, LogOut, Sun, Moon } from 'lucide-react';
import { Repository, User } from '../types';

interface LayoutProps {
  children: React.ReactNode;
  user: User | null;
  currentRepo: Repository | null;
  onLogout: () => void;
  onChangeRepo: () => void;
  isDarkMode: boolean;
  toggleTheme: () => void;
}

export const Layout: React.FC<LayoutProps> = ({ 
  children, 
  user, 
  currentRepo, 
  onLogout, 
  onChangeRepo,
  isDarkMode,
  toggleTheme
}) => {
  return (
    <div className={`min-h-screen flex flex-col transition-colors duration-300 ${isDarkMode ? 'dark' : ''} bg-white dark:bg-github-bg text-gray-900 dark:text-github-text`}>
      {user && (
        <header className="h-16 border-b border-gray-200 dark:border-github-border bg-gray-50 dark:bg-github-subtle flex items-center justify-between px-6 sticky top-0 z-20">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2 font-bold text-lg tracking-tight">
              <div className="bg-github-btn text-white p-1.5 rounded-md">
                <Github size={20} />
              </div>
              <span>DevLog AI</span>
            </div>
            
            {currentRepo && (
              <>
                <div className="h-6 w-px bg-gray-300 dark:bg-github-border mx-2"></div>
                <button 
                  onClick={onChangeRepo}
                  className="flex items-center gap-2 px-3 py-1.5 rounded-md hover:bg-gray-200 dark:hover:bg-github-border/50 text-sm font-medium transition-colors text-gray-600 dark:text-github-muted hover:text-gray-900 dark:hover:text-github-text"
                >
                  <Folder size={16} />
                  <span>{currentRepo.name}</span>
                  <span className="text-xs opacity-50 ml-1">▼</span>
                </button>
              </>
            )}
          </div>

          <div className="flex items-center gap-4">
            <button 
              onClick={toggleTheme}
              className="p-2 rounded-full hover:bg-gray-200 dark:hover:bg-github-border text-gray-600 dark:text-github-muted transition-colors"
            >
              {isDarkMode ? <Sun size={18} /> : <Moon size={18} />}
            </button>
            <div className="flex items-center gap-3 pl-4 border-l border-gray-200 dark:border-github-border">
              <img src={user.avatar_url} alt={user.username} className="w-8 h-8 rounded-full border border-gray-200 dark:border-github-border" />
              <button 
                onClick={onLogout}
                className="text-sm font-medium text-gray-600 dark:text-github-muted hover:text-red-600 dark:hover:text-red-400 transition-colors"
              >
                <LogOut size={18} />
              </button>
            </div>
          </div>
        </header>
      )}
      <main className="flex-1 overflow-auto relative">
        {children}
      </main>
    </div>
  );
};
