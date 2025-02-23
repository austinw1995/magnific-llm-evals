import React, { useState } from 'react';
import { TestResult } from '../types';
import { Upload } from 'lucide-react';
import { Button } from "@/components/ui/button";

interface DataTableProps {
  data: TestResult[];
  onFileUpload: (file: File) => void;
}

export function DataTable({ data, onFileUpload }: DataTableProps) {
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = React.useRef<HTMLInputElement>(null);
  const [expandedTranscripts, setExpandedTranscripts] = useState<{[key: number]: boolean}>({});

  const handleButtonClick = () => {
    fileInputRef.current?.click();
  };

  const toggleTranscript = (id: number) => {
    setExpandedTranscripts(prev => ({
      ...prev,
      [id]: !prev[id]
    }));
  };

  const truncateTranscript = (transcript: string, expanded: boolean) => {
    const lines = transcript.split('\n');
    if (lines.length <= 5 || expanded) return transcript;
    return lines.slice(0, 5).join('\n') + '\n...';
  };

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    setError(null);
    
    if (file) {
      if (!file.name.endsWith('.json')) {
        setError('Please upload a JSON file');
        return;
      }
      onFileUpload(file);
    }
  };

  return (
    <div className="bg-card text-card-foreground rounded-lg shadow-sm border">
      <div className="p-4 border-b">
        <div className="flex justify-between items-center">
          <h2 className="text-lg font-semibold">Test Results</h2>
          <div className="flex flex-col items-end gap-2">
            <Button 
              variant="outline" 
              className="cursor-pointer"
              onClick={handleButtonClick}
            >
              <Upload className="w-4 h-4 mr-2" />
              Upload JSON
            </Button>
            <input
              type="file"
              accept=".json"
              onChange={handleFileChange}
              className="hidden"
              ref={fileInputRef}
            />
            {error && (
              <p className="text-sm text-destructive">{error}</p>
            )}
          </div>
        </div>
      </div>
      
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-muted">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">
                Test ID
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">
                Type
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">
                Customer Prompt
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">
                Transcript
              </th>
              {data[0]?.evaluation_results.map((result) => (
                <th key={result.name} className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">
                  {result.name} Score
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-border">
            {data.map((row) => (
              <tr key={row.test_id}>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-muted-foreground">
                  {row.test_id}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm">
                  {row.call_type}
                </td>
                <td className="px-6 py-4 text-sm">
                  <pre className="whitespace-pre-wrap font-sans">
                    {row.customer_config.system_prompt}
                  </pre>
                </td>
                <td 
                  className="px-6 py-4 text-sm cursor-pointer hover:bg-muted/50"
                  onClick={() => toggleTranscript(row.test_id)}
                >
                  <pre className="whitespace-pre-wrap font-sans">
                    {truncateTranscript(row.transcript, !!expandedTranscripts[row.test_id])}
                    {!expandedTranscripts[row.test_id] && row.transcript.split('\n').length > 5 && (
                      <span className="text-blue-500 block mt-1">Click to expand</span>
                    )}
                  </pre>
                </td>
                {row.evaluation_results.map((result) => (
                  <td key={result.name} className="px-6 py-4 whitespace-nowrap text-sm">
                    {result.score.toFixed(2)}
                  </td>
                ))}
              </tr>
            ))}
            {data.length === 0 && (
              <tr>
                <td colSpan={5} className="px-6 py-8 text-center text-muted-foreground">
                  No data available. Upload a JSON file to get started.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}