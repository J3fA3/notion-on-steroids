import React, { useState, useEffect } from 'react';
import { InputPanel } from './components/InputPanel';
import { TaskBoard } from './components/TaskBoard';
import { apiClient, Task } from './api/client';

function App() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isLoadingTasks, setIsLoadingTasks] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showSuccessMessage, setShowSuccessMessage] = useState(false);

  // Load tasks on mount
  useEffect(() => {
    loadTasks();
    checkBackendHealth();
  }, []);

  const checkBackendHealth = async () => {
    try {
      await apiClient.healthCheck();
      console.log('✓ Backend connected');
    } catch (error) {
      console.error('Backend health check failed:', error);
      setError(
        'Cannot connect to backend. Please make sure the FastAPI server is running on http://localhost:8000'
      );
    }
  };

  const loadTasks = async () => {
    try {
      setIsLoadingTasks(true);
      const fetchedTasks = await apiClient.getTasks();
      setTasks(fetchedTasks);
      setError(null);
    } catch (error) {
      console.error('Failed to load tasks:', error);
      setError(error instanceof Error ? error.message : 'Failed to load tasks');
    } finally {
      setIsLoadingTasks(false);
    }
  };

  const handleInferTasks = async (content: string, source: string) => {
    try {
      setIsLoading(true);
      setError(null);

      // Call inference endpoint
      const result = await apiClient.inferTasks(content, source);

      // Show success message
      setShowSuccessMessage(true);
      setTimeout(() => setShowSuccessMessage(false), 5000);

      // Reload tasks to show newly inferred ones
      await loadTasks();

      console.log(`✓ Inferred ${result.tasks_inferred} tasks`);
    } catch (error) {
      console.error('Failed to infer tasks:', error);
      const errorMessage = error instanceof Error ? error.message : 'Failed to infer tasks';
      setError(errorMessage);
      alert(`Error: ${errorMessage}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleTaskUpdate = async (id: number, updates: Partial<Task>) => {
    try {
      await apiClient.updateTask(id, updates);
      await loadTasks(); // Reload to show updated task
    } catch (error) {
      console.error('Failed to update task:', error);
      setError(error instanceof Error ? error.message : 'Failed to update task');
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <h1 className="text-2xl font-bold text-gray-900">🪷 Lotus</h1>
              <span className="text-sm text-gray-500">Personal AI Task Companion</span>
            </div>
            {!isLoadingTasks && (
              <button
                onClick={loadTasks}
                className="text-sm text-gray-600 hover:text-gray-900 transition-colors"
              >
                🔄 Refresh
              </button>
            )}
          </div>
        </div>
      </header>

      {/* Success message */}
      {showSuccessMessage && (
        <div className="max-w-7xl mx-auto px-6 mt-4">
          <div className="bg-green-50 border border-green-200 rounded-lg p-4 text-green-800 flex items-center gap-2">
            <CheckCircle className="w-5 h-5" />
            <span>✓ Tasks inferred successfully! Check the board below.</span>
          </div>
        </div>
      )}

      {/* Error message */}
      {error && (
        <div className="max-w-7xl mx-auto px-6 mt-4">
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-800 flex items-center justify-between">
            <span>⚠️ {error}</span>
            <button onClick={() => setError(null)} className="text-red-600 hover:text-red-800">
              ✕
            </button>
          </div>
        </div>
      )}

      {/* Main content */}
      <main className="py-8">
        {/* Input Panel */}
        <section className="mb-12">
          <InputPanel onInferTasks={handleInferTasks} isLoading={isLoading} />
        </section>

        {/* Divider */}
        <div className="max-w-7xl mx-auto px-6 my-8">
          <div className="border-t border-gray-300"></div>
        </div>

        {/* Task Board */}
        <section>
          {isLoadingTasks ? (
            <div className="flex justify-center items-center py-12">
              <div className="text-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
                <p className="text-gray-600">Loading tasks...</p>
              </div>
            </div>
          ) : (
            <TaskBoard tasks={tasks} onTaskUpdate={handleTaskUpdate} />
          )}
        </section>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-12">
        <div className="max-w-7xl mx-auto px-6 py-4 text-center text-sm text-gray-500">
          Built with ❤️ using Claude Code and agentic AI | Phase 1: Manual Input MVP
        </div>
      </footer>
    </div>
  );
}

// CheckCircle component for success message
const CheckCircle: React.FC<{ className?: string }> = ({ className }) => (
  <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth={2}
      d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
    />
  </svg>
);

export default App;
