import React, { useState } from 'react';
import { Save, Play, Database } from 'lucide-react';
import { ModelConfig } from '../types';
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";

interface PromptSectionProps {
  config: ModelConfig;
  onConfigChange: (config: ModelConfig) => void;
  onSave: () => void;
  onRun: () => void;
  onGenerateSynthetic: (numTests: number, maxThreads: number) => void;
  isLoading: boolean;
  isSyntheticLoading: boolean;
}

export function PromptSection({ 
  config, 
  onConfigChange, 
  onSave, 
  onRun, 
  onGenerateSynthetic,
  isLoading,
  isSyntheticLoading 
}: PromptSectionProps) {
  const [numTests, setNumTests] = useState(5);
  const [maxThreads, setMaxThreads] = useState(5);

  return (
    <div className="bg-card text-card-foreground rounded-lg shadow-sm border p-6 mb-6">
      <div className="space-y-4">
        <div className="grid grid-cols-3 gap-4">
          <div className="space-y-2">
            <Label>Model Name</Label>
            <Input
              value={config.params.model}
              onChange={(e) => onConfigChange({
                ...config,
                params: { ...config.params, model: e.target.value }
              })}
            />
          </div>
          <div className="space-y-2">
            <Label>Temperature</Label>
            <Input
              type="number"
              value={config.params.temperature}
              onChange={(e) => onConfigChange({
                ...config,
                params: { ...config.params, temperature: parseFloat(e.target.value) }
              })}
              min={0}
              max={1}
              step={0.1}
            />
          </div>
          <div className="space-y-2">
            <Label>Max Tokens</Label>
            <Input
              type="number"
              value={config.params.max_tokens}
              onChange={(e) => onConfigChange({
                ...config,
                params: { ...config.params, max_tokens: parseInt(e.target.value) }
              })}
              min={1}
            />
          </div>
        </div>
        
        <div className="space-y-2">
          <Label>System Prompt</Label>
          <Textarea
            value={config.system_prompt}
            onChange={(e) => onConfigChange({ ...config, system_prompt: e.target.value })}
            rows={3}
            placeholder="Enter system prompt..."
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-2">
            <Label>Number of Test Cases</Label>
            <Input
              type="number"
              value={numTests}
              onChange={(e) => setNumTests(parseInt(e.target.value))}
              min={1}
              max={100}
            />
          </div>
          <div className="space-y-2">
            <Label>Max Threads</Label>
            <Input
              type="number"
              value={maxThreads}
              onChange={(e) => setMaxThreads(parseInt(e.target.value))}
              min={1}
              max={10}
            />
          </div>
        </div>

        <div className="flex justify-end space-x-4">
          <Button
            variant="outline"
            onClick={onSave}
          >
            <Save className="w-4 h-4 mr-2" />
            Save
          </Button>
          <Button
            variant="outline"
            onClick={() => onGenerateSynthetic(numTests, maxThreads)}
            disabled={isSyntheticLoading || isLoading}
          >
            <Database className="w-4 h-4 mr-2" />
            {isSyntheticLoading ? 'Generating...' : 'Generate Synthetic Data'}
          </Button>
          <Button
            onClick={onRun}
            disabled={isLoading || isSyntheticLoading}
          >
            <Play className="w-4 h-4 mr-2" />
            {isLoading ? 'Running...' : 'Re-Run Evaluation'}
          </Button>
        </div>
      </div>
    </div>
  );
}