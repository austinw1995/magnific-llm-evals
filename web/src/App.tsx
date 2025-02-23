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
  const [isSyntheticLoading, setIsSyntheticLoading] = useState(false);

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

  const handleGenerateSynthetic = async (numTests: number, maxThreads: number) => {
    setIsSyntheticLoading(true);
    try {
      // First generate synthetic data
      const genResponse = await fetch('http://localhost:8000/api/generate-synthetic', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          service_prompt: config.system_prompt,
          model: config.params.model,
          num_tests: numTests,
          max_threads: maxThreads,
          temperature: config.params.temperature,
        }),
      });

      if (!genResponse.ok) {
        throw new Error('Failed to generate synthetic data');
      }

      const genData = await genResponse.json();
      
      // Now run tests with the synthetic data
      const runResponse = await fetch('http://localhost:8000/api/rerun', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          config,
          test_results: genData.scenarios.map((scenario: any, index: number) => ({
            test_id: index + 1,
            call_type: scenario.type,
            transcript: `Starting ${scenario.type} conversation\n\ncustomer_agent: ${scenario.first_message}`,
            customer_config: {
              params: {
                model: config.params.model,
                temperature: 0.7,
              },
              system_prompt: scenario.customer_prompt,
              end_call_enabled: true,
            },
            // Use the evaluation results from the existing test results
            evaluation_results: testResults[0]?.evaluation_results || []
          }))
        }),
      });

      if (!runResponse.ok) {
        throw new Error('Failed to run tests');
      }

      const runData = await runResponse.json();
      const testsArray = Object.values(runData.results) as TestResult[];
      setTestResults(testsArray);

      alert('Synthetic data generated and tests completed successfully');
    } catch (error) {
      console.error('Error:', error);
      alert('Failed to generate synthetic data or run tests');
    } finally {
      setIsSyntheticLoading(false);
    }
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
          onGenerateSynthetic={handleGenerateSynthetic}
          isLoading={isLoading}
          isSyntheticLoading={isSyntheticLoading}
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