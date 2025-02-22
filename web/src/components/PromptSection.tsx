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
              readOnly
              className="bg-muted"
            />
          </div>
          <div className="space-y-2">
            <Label>Temperature</Label>
            <Input
              value={config.params.temperature}
              readOnly
              className="bg-muted"
            />
          </div>
          <div className="space-y-2">
            <Label>Max Tokens</Label>
            <Input
              value={config.params.max_tokens}
              readOnly
              className="bg-muted"
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
            {isLoading ? 'Running...' : 'Run Evaluation'}
          </Button>
        </div>
      </div>
    </div>
  );
}