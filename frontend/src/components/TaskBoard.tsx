import React from 'react';
import { CheckCircle2, Circle, Clock } from 'lucide-react';
import { Task } from '../api/client';

interface TaskBoardProps {
  tasks: Task[];
  onTaskUpdate: (id: number, updates: Partial<Task>) => Promise<void>;
}

export const TaskBoard: React.FC<TaskBoardProps> = ({ tasks, onTaskUpdate }) => {
  const todoTasks = tasks.filter((t) => t.status === 'todo');
  const inProgressTasks = tasks.filter((t) => t.status === 'in_progress');
  const doneTasks = tasks.filter((t) => t.status === 'done');

  const handleStatusChange = async (task: Task, newStatus: 'todo' | 'in_progress' | 'done') => {
    await onTaskUpdate(task.id, {
      status: newStatus,
      completed_at: newStatus === 'done' ? new Date().toISOString() : null,
    });
  };

  const getConfidenceColor = (score: number) => {
    if (score >= 80) return 'text-green-600 bg-green-100';
    if (score >= 70) return 'text-yellow-600 bg-yellow-100';
    return 'text-orange-600 bg-orange-100';
  };

  const getPriorityLabel = (priority: number | null) => {
    if (!priority) return '';
    const labels = ['🔴 Urgent', '🟠 High', '🟡 Medium', '🟢 Low', '⚪ Minimal'];
    return labels[priority - 1] || '';
  };

  const TaskCard: React.FC<{ task: Task }> = ({ task }) => {
    const isNewlyInferred = new Date(task.inferred_at).getTime() > Date.now() - 60000; // Last minute

    return (
      <div
        className={`bg-white rounded-lg shadow-sm border p-4 mb-3 transition-all hover:shadow-md ${
          isNewlyInferred ? 'ring-2 ring-blue-500 animate-pulse' : 'border-gray-200'
        }`}
      >
        <div className="flex items-start justify-between mb-2">
          <h3 className="font-medium text-gray-900 flex-1">{task.title}</h3>
          {isNewlyInferred && (
            <span className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded-full ml-2">
              NEW
            </span>
          )}
        </div>

        {task.description && (
          <p className="text-sm text-gray-600 mb-3">{task.description}</p>
        )}

        {task.context && (
          <div className="bg-gray-50 rounded p-2 mb-3">
            <p className="text-xs text-gray-500 italic">{task.context}</p>
          </div>
        )}

        <div className="flex items-center justify-between flex-wrap gap-2">
          <div className="flex items-center gap-2 flex-wrap">
            {/* Confidence score */}
            <span
              className={`text-xs px-2 py-1 rounded-full font-medium ${getConfidenceColor(
                task.confidence_score
              )}`}
            >
              {task.confidence_score.toFixed(0)}% confident
            </span>

            {/* Priority */}
            {task.priority && (
              <span className="text-xs text-gray-600">{getPriorityLabel(task.priority)}</span>
            )}

            {/* Source */}
            <span className="text-xs text-gray-400">
              {task.source_type === 'manual_text' ? '📝 Manual' : `📧 ${task.source_type}`}
            </span>
          </div>

          {/* Status change buttons */}
          <div className="flex gap-1">
            {task.status !== 'todo' && (
              <button
                onClick={() => handleStatusChange(task, 'todo')}
                className="p-1.5 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded transition-colors"
                title="Move to To Do"
              >
                <Circle className="w-4 h-4" />
              </button>
            )}
            {task.status !== 'in_progress' && (
              <button
                onClick={() => handleStatusChange(task, 'in_progress')}
                className="p-1.5 text-blue-400 hover:text-blue-600 hover:bg-blue-50 rounded transition-colors"
                title="Move to In Progress"
              >
                <Clock className="w-4 h-4" />
              </button>
            )}
            {task.status !== 'done' && (
              <button
                onClick={() => handleStatusChange(task, 'done')}
                className="p-1.5 text-green-400 hover:text-green-600 hover:bg-green-50 rounded transition-colors"
                title="Mark as Done"
              >
                <CheckCircle2 className="w-4 h-4" />
              </button>
            )}
          </div>
        </div>

        {task.due_date && (
          <div className="mt-2 text-xs text-gray-500">
            📅 Due: {new Date(task.due_date).toLocaleDateString()}
          </div>
        )}
      </div>
    );
  };

  const Column: React.FC<{ title: string; icon: React.ReactNode; tasks: Task[]; color: string }> = ({
    title,
    icon,
    tasks,
    color,
  }) => (
    <div className="flex-1 min-w-[300px]">
      <div className={`flex items-center gap-2 mb-4 pb-2 border-b-2 ${color}`}>
        {icon}
        <h2 className="font-semibold text-gray-800">
          {title} <span className="text-gray-500 text-sm">({tasks.length})</span>
        </h2>
      </div>
      <div className="space-y-3">
        {tasks.length === 0 ? (
          <p className="text-sm text-gray-400 italic text-center py-8">No tasks</p>
        ) : (
          tasks.map((task) => <TaskCard key={task.id} task={task} />)
        )}
      </div>
    </div>
  );

  return (
    <div className="w-full max-w-7xl mx-auto p-6">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-900">🪷 Lotus Task Board</h1>
        <div className="text-sm text-gray-500">
          {tasks.length} total task{tasks.length !== 1 ? 's' : ''}
        </div>
      </div>

      <div className="flex gap-6 overflow-x-auto pb-4">
        <Column
          title="To Do"
          icon={<Circle className="w-5 h-5 text-gray-600" />}
          tasks={todoTasks}
          color="border-gray-300"
        />
        <Column
          title="In Progress"
          icon={<Clock className="w-5 h-5 text-blue-600" />}
          tasks={inProgressTasks}
          color="border-blue-300"
        />
        <Column
          title="Done"
          icon={<CheckCircle2 className="w-5 h-5 text-green-600" />}
          tasks={doneTasks}
          color="border-green-300"
        />
      </div>
    </div>
  );
};
