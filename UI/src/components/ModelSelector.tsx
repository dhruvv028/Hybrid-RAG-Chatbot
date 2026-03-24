import { ChevronDown, Cpu, Zap, Brain } from "lucide-react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

export type LLMModel = "gpt-4" | "claude-3.5" | "gemini-pro";

interface ModelSelectorProps {
  selectedModel: LLMModel;
  onModelChange: (model: LLMModel) => void;
}

const models = [
  {
    id: "gpt-4" as LLMModel,
    name: "GPT-4",
    description: "Most capable OpenAI model",
    icon: Brain,
    badge: "Popular"
  },
  {
    id: "claude-3.5" as LLMModel,
    name: "Claude 3.5 Sonnet",
    description: "Advanced reasoning capabilities",
    icon: Zap,
    badge: "Fast"
  },
  {
    id: "gemini-pro" as LLMModel,
    name: "Gemini Pro",
    description: "Google's powerful multimodal model",
    icon: Cpu,
    badge: "Pro"
  }
];

export function ModelSelector({ selectedModel, onModelChange }: ModelSelectorProps) {
  const currentModel = models.find(m => m.id === selectedModel);
  const Icon = currentModel?.icon || Brain;

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button 
          variant="outline" 
          className="gap-2 bg-card border-border hover:bg-accent/50 transition-colors"
        >
          <Icon className="h-4 w-4" />
          <span className="hidden sm:inline">{currentModel?.name}</span>
          <ChevronDown className="h-4 w-4" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent 
        align="end" 
        className="w-72 bg-card border-border shadow-lg"
      >
        {models.map((model) => {
          const ModelIcon = model.icon;
          const isSelected = selectedModel === model.id;
          
          return (
            <DropdownMenuItem
              key={model.id}
              onClick={() => onModelChange(model.id)}
              className={`cursor-pointer p-3 ${
                isSelected ? 'bg-accent/50 text-accent-foreground' : 'hover:bg-accent/30'
              }`}
            >
              <div className="flex items-center gap-3 w-full">
                <ModelIcon className="h-5 w-5 text-primary" />
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <span className="font-medium">{model.name}</span>
                    <Badge variant="secondary" className="text-xs">
                      {model.badge}
                    </Badge>
                  </div>
                  <p className="text-sm text-muted-foreground mt-1">
                    {model.description}
                  </p>
                </div>
                {isSelected && (
                  <div className="w-2 h-2 bg-primary rounded-full" />
                )}
              </div>
            </DropdownMenuItem>
          );
        })}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}