import React from 'react';
import { Github, Terminal } from 'lucide-react';

interface LoginProps {
  onLogin: () => void;
}

export const Login: React.FC<LoginProps> = ({ onLogin }) => {
  return (
    <div className="flex items-center justify-center min-h-[calc(100vh-4rem)]">
      <div className="w-full max-w-md bg-white dark:bg-github-subtle border border-gray-200 dark:border-github-border rounded-xl shadow-xl p-8 text-center animate-in fade-in zoom-in duration-300">
        <div className="mx-auto w-16 h-16 bg-gray-100 dark:bg-github-bg rounded-full flex items-center justify-center mb-6 border border-gray-200 dark:border-github-border">
          <Terminal size={32} className="text-github-btn" />
        </div>
        <h1 className="text-2xl font-bold mb-2 text-gray-900 dark:text-github-text">Welcome to DevLog AI</h1>
        <p className="text-gray-500 dark:text-github-muted mb-8">Turn your Git commits into meaningful engineering journals automatically with Gemini.</p>
        
        <button
          onClick={onLogin}
          className="w-full bg-[#24292f] hover:bg-[#333] dark:bg-github-btn dark:hover:bg-github-btn-hover text-white font-semibold py-3 px-4 rounded-lg flex items-center justify-center gap-3 transition-all transform active:scale-95"
        >
          <Github size={20} />
          <span>Sign in with GitHub</span>
        </button>
        
        <p className="mt-6 text-xs text-gray-400 dark:text-github-muted">
          By signing in, you accept our Terms of Service and Privacy Policy.
        </p>
      </div>
    </div>
  );
};
