import React, { useState } from 'react';
import { FileText, Upload } from 'lucide-react';

interface InputPanelProps {
  onInferTasks: (content: string, source: string) => Promise<void>;
  isLoading: boolean;
}

export const InputPanel: React.FC<InputPanelProps> = ({ onInferTasks, isLoading }) => {
  const [textContent, setTextContent] = useState('');
  const [dragActive, setDragActive] = useState(false);

  const handleInferClick = async () => {
    if (!textContent.trim()) {
      alert('Please paste some text first!');
      return;
    }
    await onInferTasks(textContent, 'manual_text');
    setTextContent(''); // Clear after successful inference
  };

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = async (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    const files = Array.from(e.dataTransfer.files);
    const file = files[0];

    if (!file) return;

    // Check file type
    const validTypes = ['text/plain', 'application/pdf'];
    if (!validTypes.includes(file.type) && !file.name.endsWith('.txt') && !file.name.endsWith('.pdf')) {
      alert('Please upload a .txt or .pdf file');
      return;
    }

    // Read text file
    if (file.type === 'text/plain' || file.name.endsWith('.txt')) {
      const text = await file.text();
      setTextContent(text);
      alert(`Loaded ${file.name}. Click "Infer Tasks" to process.`);
    } else if (file.type === 'application/pdf' || file.name.endsWith('.pdf')) {
      // For PDF, we'll need to upload to backend for parsing
      const formData = new FormData();
      formData.append('file', file);

      try {
        const response = await fetch('http://localhost:8000/api/upload-file', {
          method: 'POST',
          body: formData,
        });

        if (!response.ok) {
          throw new Error('Failed to upload PDF');
        }

        const data = await response.json();
        setTextContent(data.extracted_text);
        alert(`Extracted text from ${file.name}. Click "Infer Tasks" to process.`);
      } catch (error) {
        console.error('Error uploading PDF:', error);
        alert('Failed to process PDF. Backend endpoint may not be ready yet.');
      }
    }
  };

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Same logic as handleDrop
    if (file.type === 'text/plain' || file.name.endsWith('.txt')) {
      const text = await file.text();
      setTextContent(text);
      alert(`Loaded ${file.name}. Click "Infer Tasks" to process.`);
    } else if (file.type === 'application/pdf' || file.name.endsWith('.pdf')) {
      const formData = new FormData();
      formData.append('file', file);

      try {
        const response = await fetch('http://localhost:8000/api/upload-file', {
          method: 'POST',
          body: formData,
        });

        if (!response.ok) {
          throw new Error('Failed to upload PDF');
        }

        const data = await response.json();
        setTextContent(data.extracted_text);
        alert(`Extracted text from ${file.name}. Click "Infer Tasks" to process.`);
      } catch (error) {
        console.error('Error uploading PDF:', error);
        alert('Failed to process PDF. Backend endpoint may not be ready yet.');
      }
    }
  };

  return (
    <div className="w-full max-w-4xl mx-auto p-6 space-y-4">
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex items-center gap-2 mb-4">
          <FileText className="w-5 h-5 text-gray-600" />
          <h2 className="text-xl font-semibold text-gray-800">Manual Task Input</h2>
        </div>

        <p className="text-sm text-gray-600 mb-4">
          Paste Slack messages, emails, or meeting notes below. Our AI will automatically infer tasks.
        </p>

        {/* Textarea for manual input */}
        <textarea
          value={textContent}
          onChange={(e) => setTextContent(e.target.value)}
          placeholder="Paste your Slack messages, emails, or meeting notes here...&#10;&#10;Example:&#10;Hey! Can you send me the Q4 report by tomorrow? The board meeting is on Wednesday.&#10;&#10;Also, could you review my PR when you get a chance? It's for the new auth feature."
          className="w-full h-64 p-4 border border-gray-300 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 font-mono text-sm"
          disabled={isLoading}
        />

        {/* Character count */}
        <div className="flex justify-between items-center mt-2 text-sm text-gray-500">
          <span>{textContent.length} characters</span>
          {textContent.length > 10000 && (
            <span className="text-orange-600">⚠ Very long text may take longer to process</span>
          )}
        </div>

        {/* Infer Tasks button */}
        <button
          onClick={handleInferClick}
          disabled={isLoading || !textContent.trim()}
          className={`mt-4 w-full py-3 px-6 rounded-lg font-medium transition-colors ${
            isLoading || !textContent.trim()
              ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
              : 'bg-blue-600 text-white hover:bg-blue-700 active:bg-blue-800'
          }`}
        >
          {isLoading ? (
            <span className="flex items-center justify-center gap-2">
              <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                  fill="none"
                />
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                />
              </svg>
              Inferring Tasks...
            </span>
          ) : (
            'Infer Tasks'
          )}
        </button>
      </div>

      {/* File upload dropzone */}
      <div
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        className={`bg-white rounded-lg shadow-md p-8 border-2 border-dashed transition-colors ${
          dragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300'
        }`}
      >
        <div className="flex flex-col items-center justify-center text-center">
          <Upload className={`w-12 h-12 mb-4 ${dragActive ? 'text-blue-500' : 'text-gray-400'}`} />
          <h3 className="text-lg font-semibold text-gray-700 mb-2">Upload Meeting Transcripts</h3>
          <p className="text-sm text-gray-500 mb-4">
            Drag and drop .txt or .pdf files here, or click to browse
          </p>
          <input
            type="file"
            accept=".txt,.pdf,text/plain,application/pdf"
            onChange={handleFileSelect}
            className="hidden"
            id="file-upload"
            disabled={isLoading}
          />
          <label
            htmlFor="file-upload"
            className={`px-6 py-2 rounded-lg font-medium transition-colors cursor-pointer ${
              isLoading
                ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            Choose File
          </label>
          <p className="text-xs text-gray-400 mt-4">Supported: .txt, .pdf (max 10MB)</p>
        </div>
      </div>

      {/* Instructions */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h4 className="font-semibold text-blue-900 mb-2">💡 Tips for Best Results</h4>
        <ul className="text-sm text-blue-800 space-y-1 list-disc list-inside">
          <li>Include context: dates, people involved, project names</li>
          <li>Paste entire conversation threads (not just single messages)</li>
          <li>Clear action verbs help: "send," "review," "schedule," "update"</li>
          <li>Multiple messages/emails in one paste work great!</li>
        </ul>
      </div>
    </div>
  );
};
