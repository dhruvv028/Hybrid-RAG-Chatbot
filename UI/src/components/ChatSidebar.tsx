import { useState } from "react";
import { Bot, MessageSquare, Users, ChevronDown, ChevronRight, Menu, X, Home, Settings } from "lucide-react";
import { cn } from "@/lib/utils";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";

export type BotType = "knowledge" | "support" | "both";

interface ChatSidebarProps {
  selectedBot: BotType;
  onBotChange: (bot: BotType) => void;
  chatHistory: Array<{ id: string; title: string; timestamp: string; originalPrompt: string }>;
  onChatSelect: (chatId: string) => void;
  selectedChatId?: string;
  isCollapsed: boolean;
  onToggleCollapse: () => void;
  className?: string;
  onNewChat?: () => void; 
}

export function ChatSidebar({ 
  selectedBot, 
  onBotChange, 
  chatHistory, 
  onChatSelect, 
  selectedChatId,
  isCollapsed,
  onToggleCollapse,
  onNewChat  
}: ChatSidebarProps) {
  const [isHistoryExpanded, setIsHistoryExpanded] = useState(true);

  const botOptions = [
    {
      type: "knowledge" as BotType,
      label: "Knowledge Bot",
      description: "Get instant answers from our knowledge base",
      icon: Bot,
      shortLabel: "Knowledge"
    },
    {
      type: "support" as BotType,
      label: "Support Bot", 
      description: "Connect with our support team",
      icon: MessageSquare,
      shortLabel: "Support"
    },
    {
      type: "both" as BotType,
      label: "Hybrid Assistant",
      description: "Best of both knowledge and support",
      icon: Users,
      shortLabel: "Hybrid"
    }
  ];

  return (
    <TooltipProvider>
      <div className={cn(
        "bg-gradient-subtle border-r border-sidebar-border flex flex-col h-full transition-all duration-300 overflow-hidden",
        isCollapsed ? "w-16" : "w-80"
      )}>
        {/* Header */}
        <div className={cn(
          "border-b border-sidebar-border bg-gradient-header",
          isCollapsed ? "p-4" : "p-6"
        )}>
          <div className="flex items-center gap-3">
            <Button
              variant="ghost"
              size="sm"
              onClick={onToggleCollapse}
              className="text-white hover:bg-white/20 shrink-0"
            >
              {isCollapsed ? <Menu className="h-5 w-5" /> : <X className="h-5 w-5" />}
            </Button>
            {!isCollapsed && (
              <>
                <div className="p-2 bg-white/20 backdrop-blur-sm rounded-lg">
                  <Bot className="h-5 w-5 text-white" />
                </div>
                <div>
                  <h2 className="text-base font-semibold text-white">Choose Assistant</h2>
                  <p className="text-xs text-white/80">Select your bot</p>
                </div>
              </>
            )}
          </div>
        </div>

        {/* Bot Selection */}
        <div className={cn("flex-1 overflow-hidden", isCollapsed ? "p-2" : "p-4")}>
          {botOptions.map((option) => {
            const Icon = option.icon;
            const isSelected = selectedBot === option.type;
            
            if (isCollapsed) {
              return (
                <Tooltip key={option.type}>
                  <TooltipTrigger asChild>
                    <Button
                      variant={isSelected ? "default" : "ghost"}
                      size="sm"
                      className={cn(
                        "w-full h-12 p-0",
                        isSelected ? "bg-primary text-primary-foreground" : "hover:bg-accent"
                      )}
                      onClick={() => onBotChange(option.type)}
                    >
                      <Icon className="h-5 w-5" />
                    </Button>
                  </TooltipTrigger>
                  <TooltipContent side="right">
                    <p>{option.label}</p>
                  </TooltipContent>
                </Tooltip>
              );
            }
            
            return (
              <Card
                key={option.type}
                className={cn(
                  "p-3 cursor-pointer transition-all duration-200 border",
                  isSelected 
                    ? "border-primary bg-primary/5" 
                    : "border-border hover:border-primary/50 hover:bg-accent/50"
                )}
                onClick={() => onBotChange(option.type)}
              >
                <div className="flex items-center gap-3">
                  <div className={cn(
                    "p-2 rounded-lg flex-shrink-0",
                    isSelected 
                      ? "bg-primary text-primary-foreground" 
                      : "bg-muted"
                  )}>
                    <Icon className="h-4 w-4" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <h3 className="font-medium text-sm text-foreground">{option.label}</h3>
                      {isSelected && (
                        <Badge variant="secondary" className="text-xs bg-success/20 text-success">
                          Active
                        </Badge>
                      )}
                    </div>
                    <p className="text-xs text-muted-foreground mt-1">
                      {option.description}
                    </p>
                  </div>
                </div>
              </Card>
            );
          })}
        </div>

        {/* Selected Bot Display */}
        {!isCollapsed && (
          <div className="px-4 py-3">
            <div className="bg-success/10 border border-success/30 rounded-lg p-3">
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-success rounded-full"></div>
                <span className="text-sm font-medium text-foreground">
                  Active: {botOptions.find(b => b.type === selectedBot)?.shortLabel}
                </span>
              </div>
            </div>
          </div>
        )}

{/* Chat History */}
<div className={cn("flex-1", isCollapsed ? "p-2" : "p-4")}>
  {isCollapsed ? (
    <Tooltip>
      <TooltipTrigger asChild>
        <Button
          variant="ghost"
          size="sm"
          className="w-full h-12"
          onClick={() => setIsHistoryExpanded(!isHistoryExpanded)}
        >
          <MessageSquare className="h-5 w-5" />
        </Button>
      </TooltipTrigger>
      <TooltipContent side="right">
        <p>Recent Conversations</p>
      </TooltipContent>
    </Tooltip>
  ) : (
    <>
      <Button
        variant="ghost"
        className="w-full justify-between p-2 h-auto mb-3"
        onClick={() => setIsHistoryExpanded(!isHistoryExpanded)}
      >
        <div className="flex items-center gap-2">
          <MessageSquare className="h-4 w-4" />
          <span className="font-medium text-sm">Recent Conversations</span>
        </div>
        {isHistoryExpanded ? (
          <ChevronDown className="h-4 w-4" />
        ) : (
          <ChevronRight className="h-4 w-4" />
        )}
      </Button>

      {/* ✅ Add New Chat button */}
      {isHistoryExpanded && onNewChat && (
        <Button
          variant="outline"
          size="sm"
          className="w-full mb-2"
          onClick={onNewChat}
        >
          + New Chat
        </Button>
      )}

      {isHistoryExpanded && (
        <div className="space-y-1 max-h-96 overflow-y-auto">
          {chatHistory.length === 0 ? (
            <div className="text-center py-6">
              <MessageSquare className="h-6 w-6 text-muted-foreground mx-auto mb-2" />
              <p className="text-xs text-muted-foreground">No conversations yet</p>
            </div>
          ) : (
            chatHistory.map((chat) => (
              <div
                key={chat.id}
                className={cn(
                  "p-2 rounded-md cursor-pointer transition-colors text-left",
                  selectedChatId === chat.id 
                    ? "bg-primary/10 border border-primary/20" 
                    : "hover:bg-accent/50"
                )}
                onClick={() => onChatSelect(chat.id)}
              >
                <h4 className="text-xs font-medium text-foreground truncate">
                  {chat.title}
                </h4>
                <p className="text-xs text-muted-foreground mt-1">
                  {chat.timestamp}
                </p>
              </div>
            ))
          )}
        </div>
      )}
    </>
  )}
</div>
      </div>
    </TooltipProvider>
  );
}