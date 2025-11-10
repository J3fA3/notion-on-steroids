import axios, { AxiosInstance } from 'axios';

const API_BASE_URL = 'http://localhost:8000';

export interface Task {
  id: number;
  title: string;
  description: string | null;
  context: string | null;
  status: 'todo' | 'in_progress' | 'done';
  priority: number | null;
  confidence_score: number;
  source_type: string;
  source_id: string | null;
  due_date: string | null;
  inferred_at: string;
  completed_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface InferTasksRequest {
  content: string;
  source: string;
}

export interface InferTasksResponse {
  message: string;
  tasks_inferred: number;
  tasks: Task[];
}

class APIClient {
  private client: AxiosInstance;

  constructor(baseURL: string = API_BASE_URL) {
    this.client = axios.create({
      baseURL,
      timeout: 60000, // 60 seconds for LLM inference
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response) {
          // Server responded with error
          const message = error.response.data?.detail?.message || error.response.data?.detail || 'An error occurred';
          console.error('API Error:', message);
          throw new Error(message);
        } else if (error.request) {
          // Request made but no response
          console.error('Network Error:', error.message);
          throw new Error('Cannot connect to backend. Make sure the server is running on http://localhost:8000');
        } else {
          // Something else happened
          console.error('Error:', error.message);
          throw error;
        }
      }
    );
  }

  // Health check
  async healthCheck(): Promise<{ status: string; database: string }> {
    const response = await this.client.get('/health');
    return response.data;
  }

  // Infer tasks from text content
  async inferTasks(content: string, source: string = 'manual_text'): Promise<InferTasksResponse> {
    const response = await this.client.post<InferTasksResponse>('/api/infer-tasks', {
      content,
      source,
    });
    return response.data;
  }

  // Get all tasks
  async getTasks(status?: string): Promise<Task[]> {
    const params = status ? { status } : {};
    const response = await this.client.get<Task[]>('/api/tasks', { params });
    return response.data;
  }

  // Get single task
  async getTask(id: number): Promise<Task> {
    const response = await this.client.get<Task>(`/api/tasks/${id}`);
    return response.data;
  }

  // Update task
  async updateTask(id: number, updates: Partial<Task>): Promise<Task> {
    const response = await this.client.put<Task>(`/api/tasks/${id}`, updates);
    return response.data;
  }

  // Delete task
  async deleteTask(id: number): Promise<void> {
    await this.client.delete(`/api/tasks/${id}`);
  }

  // Upload file (PDF or TXT)
  async uploadFile(file: File): Promise<{ extracted_text: string; filename: string }> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await this.client.post('/api/upload-file', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }
}

export const apiClient = new APIClient();
