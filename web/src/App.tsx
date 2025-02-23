import React, { useState } from 'react';
import { PromptSection } from './components/PromptSection';
import { DataTable } from './components/DataTable';
import { ModelConfig, RunDetails, TestResult } from './types';

function App() {
  const [config, setConfig] = useState<ModelConfig>({
    params: {
      model: '',
      temperature: 0.7,
      max_tokens: 10000,
    },
    system_prompt: '',
    end_call_enabled: true
  });

  const [isLoading, setIsLoading] = useState(false);
  const [testResults, setTestResults] = useState<TestResult[]>([]);

  const handleSave = () => {
    // TODO: Implement save functionality
    console.log('Saving configuration:', config);
  };

  const handleRun = async () => {
    setIsLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/rerun', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          config,
          test_results: testResults,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to re-run evaluations');
      }

      const data = await response.json();
      
      // Convert tests object to array for the table and cast to TestResult[]
      const testsArray = Object.values(data.results) as TestResult[];
      setTestResults(testsArray);

      alert('Evaluations re-run successfully');
    } catch (error) {
      console.error('Error re-running evaluations:', error);
      alert('Failed to re-run evaluations');
    } finally {
      setIsLoading(false);
    }
  };

  const handleFileUpload = (file: File) => {
    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const runDetails: RunDetails = JSON.parse(e.target?.result as string);
        
        // Set the service configuration from the first test
        const firstTest = Object.values(runDetails.tests)[0];
        if (firstTest) {
          setConfig(firstTest.service_config);
        }

        // Convert tests object to array for the table
        const testsArray = Object.values(runDetails.tests);
        setTestResults(testsArray);
      } catch (error) {
        console.error('Error parsing JSON:', error);
      }
    };
    reader.readAsText(file);
  };

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-2xl font-bold text-gray-900 mb-8">Model Evaluation</h1>
        
        <PromptSection
          config={config}
          onConfigChange={setConfig}
          onSave={handleSave}
          onRun={handleRun}
          isLoading={isLoading}
        />

        <DataTable
          data={testResults}
          onFileUpload={handleFileUpload}
        />
      </div>
    </div>
  );
}

export default App;