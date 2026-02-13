import React, { useState } from 'react';
import { ArrowLeft, Edit2, Trash2, Save, X, Lightbulb, CheckSquare, GitCommit, AlertTriangle, FileText, Code } from 'lucide-react';
import { Journal } from '../types';

interface JournalDetailProps {
  journal: Journal;
  onBack: () => void;
  onUpdate: (updatedJournal: Journal) => void;
  onDelete: (id: string) => void;
}

export const JournalDetail: React.FC<JournalDetailProps> = ({ journal, onBack, onUpdate, onDelete }) => {
  const [isEditing, setIsEditing] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [editedJournal, setEditedJournal] = useState<Journal>(journal);

  const handleSave = () => {
    onUpdate(editedJournal);
    setIsEditing(false);
  };

  const handleTextChange = (field: keyof Journal, value: string) => {
    setEditedJournal(prev => ({ ...prev, [field]: value }));
  };

  const handleArrayChange = (field: 'main_tasks' | 'learned_things', index: number, value: string) => {
    const newArray = [...(editedJournal[field] || [])];
    newArray[index] = value;
    setEditedJournal(prev => ({ ...prev, [field]: newArray }));
  };

  return (
    <>
      <div className="h-[calc(100vh-4rem)] flex flex-col bg-gray-50 dark:bg-github-bg">
        {/* Header Navigation - Fixed */}
        <div className="flex-none px-6 py-4 bg-white dark:bg-github-bg border-b border-gray-200 dark:border-github-border flex items-center justify-between z-20 shadow-sm">
          <button 
            onClick={onBack}
            className="flex items-center gap-2 text-gray-500 dark:text-github-muted hover:text-github-accent transition-colors flex-shrink-0"
          >
            <ArrowLeft size={18} />
            <span className="hidden xs:inline">Back to Dashboard</span>
            <span className="xs:hidden">Back</span>
          </button>
          
          <div className="flex items-center gap-2 sm:gap-3">
            {isEditing ? (
              <>
                <button 
                  onClick={() => setIsEditing(false)}
                  className="px-3 sm:px-4 py-2 text-sm font-medium text-gray-600 dark:text-github-text hover:bg-gray-100 dark:hover:bg-github-border rounded-md transition-colors"
                >
                  Cancel
                </button>
                <button 
                  onClick={handleSave}
                  className="flex items-center gap-2 px-3 sm:px-4 py-2 text-sm font-medium text-white bg-github-btn hover:bg-github-btn-hover rounded-md shadow-sm transition-all"
                >
                  <Save size={16} />
                  <span className="hidden xs:inline">Save Changes</span>
                  <span className="xs:hidden">Save</span>
                </button>
              </>
            ) : (
              <>
                <button 
                  onClick={() => setIsEditing(true)}
                  className="flex items-center gap-2 px-3 sm:px-4 py-2 text-sm font-medium text-gray-600 dark:text-github-text border border-gray-300 dark:border-github-border hover:bg-gray-100 dark:hover:bg-github-border rounded-md transition-colors"
                >
                  <Edit2 size={16} />
                  <span className="hidden xs:inline">Edit</span>
                </button>
                <button 
                  onClick={() => setShowDeleteModal(true)}
                  className="flex items-center gap-2 px-3 sm:px-4 py-2 text-sm font-medium text-red-600 hover:text-white border border-gray-300 dark:border-github-border hover:bg-red-600 hover:border-red-600 rounded-md transition-all"
                >
                  <Trash2 size={16} />
                  <span className="hidden xs:inline">Delete</span>
                </button>
              </>
            )}
          </div>
        </div>

        {/* Main Content Area - Scrollable */}
        <div className="flex-1 overflow-y-auto scroll-smooth">
          <div className="max-w-4xl mx-auto p-6 pb-20">
            <div className="bg-white dark:bg-github-subtle border border-gray-200 dark:border-github-border rounded-xl shadow-sm overflow-hidden">
              {/* Date Header */}
              <div className="px-8 py-6 border-b border-gray-200 dark:border-github-border bg-gray-50 dark:bg-github-bg/50">
                <h1 className="text-xl sm:text-2xl font-bold text-gray-900 dark:text-github-text font-mono truncate">
                  Journal: {journal.date}
                </h1>
                <div className="mt-3 flex flex-wrap items-center gap-x-6 gap-y-2 text-sm text-gray-500 dark:text-github-muted">
                  <div className="flex items-center gap-2">
                    <GitCommit size={14} />
                    <span>{journal.commit_count || 0} <span className="hidden xs:inline">commits</span><span className="xs:hidden">cmt</span></span>
                  </div>
                  <div className="flex items-center gap-1.5 text-green-600 dark:text-green-400">
                    <Code size={14} />
                    <span>+{journal.lines_added} <span className="hidden xs:inline">lines</span></span>
                  </div>
                  <div className="flex items-center gap-1.5 text-red-600 dark:text-red-400">
                    <Code size={14} />
                    <span>-{journal.lines_deleted} <span className="hidden xs:inline">lines</span></span>
                  </div>
                  <div className="flex items-center gap-2">
                    <FileText size={14} />
                    <span>{journal.files_changed} <span className="hidden xs:inline">files</span><span className="xs:hidden">fl</span></span>
                  </div>
                </div>
              </div>

              <div className="p-8 space-y-8">
                {/* Summary Section */}
                <section>
                  <h2 className="text-lg font-semibold text-gray-900 dark:text-github-text mb-4 flex items-center gap-2">
                    <span className="text-xl">📝</span> Summary
                  </h2>
                  {isEditing ? (
                    <textarea
                      value={editedJournal.summary}
                      onChange={(e) => handleTextChange('summary', e.target.value)}
                      className="w-full h-32 p-4 bg-white dark:bg-github-bg border border-gray-300 dark:border-github-border rounded-lg focus:ring-2 focus:ring-github-accent focus:border-transparent outline-none text-gray-900 dark:text-github-text leading-relaxed resize-none"
                    />
                  ) : (
                    <p className="text-gray-700 dark:text-gray-300 leading-relaxed text-lg">
                      {journal.summary}
                    </p>
                  )}
                </section>

                <div className="h-px bg-gray-200 dark:bg-github-border"></div>

                {/* Tasks Section */}
                <section>
                  <h2 className="text-lg font-semibold text-gray-900 dark:text-github-text mb-4 flex items-center gap-2">
                    <CheckSquare size={20} className="text-green-500" />
                    Completed Tasks
                  </h2>
                  <div className="space-y-3">
                    {(isEditing ? editedJournal.main_tasks : journal.main_tasks)?.map((task, idx) => (
                      <div key={idx} className="flex items-start gap-3">
                        <div className="mt-1 min-w-[20px] text-green-500">•</div>
                        {isEditing ? (
                          <input
                            type="text"
                            value={task}
                            onChange={(e) => handleArrayChange('main_tasks', idx, e.target.value)}
                            className="flex-1 bg-white dark:bg-github-bg border border-gray-300 dark:border-github-border rounded px-3 py-1.5 text-gray-900 dark:text-github-text focus:ring-1 focus:ring-github-accent outline-none"
                          />
                        ) : (
                          <span className="text-gray-700 dark:text-gray-300">{task}</span>
                        )}
                      </div>
                    ))}
                  </div>
                </section>

                <div className="h-px bg-gray-200 dark:bg-github-border"></div>

                {/* Learnings Section */}
                <section>
                  <h2 className="text-lg font-semibold text-gray-900 dark:text-github-text mb-4 flex items-center gap-2">
                    <Lightbulb size={20} className="text-yellow-500" />
                    Key Learnings
                  </h2>
                  <div className="bg-blue-50 dark:bg-blue-900/10 border border-blue-100 dark:border-blue-900/30 rounded-lg p-5">
                    <ul className="space-y-3">
                      {(isEditing ? editedJournal.learned_things : journal.learned_things)?.map((learning, idx) => (
                        <li key={idx} className="flex items-start gap-3">
                          <span className="mt-1.5 w-1.5 h-1.5 rounded-full bg-blue-500 flex-shrink-0"></span>
                          {isEditing ? (
                            <input
                              type="text"
                              value={learning}
                              onChange={(e) => handleArrayChange('learned_things', idx, e.target.value)}
                              className="flex-1 bg-white dark:bg-github-bg border border-gray-300 dark:border-github-border rounded px-3 py-1.5 text-gray-900 dark:text-github-text focus:ring-1 focus:ring-github-accent outline-none"
                            />
                          ) : (
                            <span className="text-gray-800 dark:text-gray-200">{learning}</span>
                          )}
                        </li>
                      ))}
                    </ul>
                  </div>
                </section>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Delete Confirmation Modal */}
      {showDeleteModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm animate-in fade-in duration-200">
          <div className="w-full max-w-sm bg-white dark:bg-github-subtle border border-gray-200 dark:border-github-border rounded-xl shadow-2xl p-6 transform transition-all scale-100">
            <div className="flex items-center gap-4 mb-4">
              <div className="p-3 bg-red-100 dark:bg-red-900/30 rounded-full text-red-600 dark:text-red-400">
                <AlertTriangle size={24} />
              </div>
              <div>
                <h3 className="text-lg font-bold text-gray-900 dark:text-github-text">Delete Journal?</h3>
                <p className="text-sm text-gray-500 dark:text-github-muted">This action cannot be undone.</p>
              </div>
            </div>
            
            <p className="text-gray-600 dark:text-gray-300 mb-6 text-sm leading-relaxed">
              Are you sure you want to permanently delete the journal for <span className="font-mono font-semibold">{journal.date}</span>?
            </p>
            
            <div className="flex items-center justify-end gap-3">
              <button 
                onClick={() => setShowDeleteModal(false)}
                className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-github-text bg-gray-100 dark:bg-github-bg border border-gray-200 dark:border-github-border rounded-md hover:bg-gray-200 dark:hover:bg-github-border transition-colors"
              >
                Cancel
              </button>
              <button 
                onClick={() => {
                  onDelete(journal.id);
                  setShowDeleteModal(false);
                }}
                className="px-4 py-2 text-sm font-medium text-white bg-red-600 hover:bg-red-700 rounded-md shadow-sm transition-colors flex items-center gap-2"
              >
                <Trash2 size={16} />
                Delete Permanently
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};