import React from 'react';
import { Save, Play } from 'lucide-react';
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
  isLoading: boolean;
}

export function PromptSection({ config, onConfigChange, onSave, onRun, isLoading }: PromptSectionProps) {
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

        <div className="flex justify-end space-x-4">
          <Button
            variant="outline"
            onClick={onSave}
          >
            <Save className="w-4 h-4 mr-2" />
            Save
          </Button>
          <Button
            onClick={onRun}
            disabled={isLoading}
          >
            <Play className="w-4 h-4 mr-2" />
            {isLoading ? 'Running...' : 'Re-Run Evaluation'}
          </Button>
        </div>
      </div>
    </div>
  );
}