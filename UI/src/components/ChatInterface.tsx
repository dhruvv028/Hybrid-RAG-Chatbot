//ChatInterface.tsx
import { useState, useRef, useEffect } from "react";
import { Send, Loader2, Sparkles, User, Bot as BotIcon } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Card } from "@/components/ui/card";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import type { BotType } from "./ChatSidebar";
import ReactMarkdown from "react-markdown";
import rehypeRaw from "rehype-raw";

interface Message {
  id: string;
  content: string;
  sender: "user" | "bot";
  timestamp: string;
  botType?: BotType;
  images?: string[];  
}

interface ChatInterfaceProps {
  selectedBot: BotType;
  selectedModel: string;
  isSidebarCollapsed?: boolean;
  onPromptFromHistory?: (prompt: string) => void;
  selectedModelSelector?: React.ReactNode;
}

export function ChatInterface({
  selectedBot,
  selectedModel,
  isSidebarCollapsed = false,
  onPromptFromHistory,
  selectedModelSelector
}: ChatInterfaceProps) {
  const [inputValue, setInputValue] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [chatId, setChatId] = useState<string | null>(null);  

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    const handleLoadHistory = (event: any) => {
      const { messages } = event.detail;
      
      // If your messages are in a single array
      // setBotMessages(messages);
  
      // If your code stores separately:
      const userMsgs = messages.filter((m: any) => m.role === "user").map((m: any) => m.content);
      const botMsgs = messages.filter((m: any) => m.role === "assistant").map((m: any) => m.content);
  
      // Assuming you already have these states:
      // setUserMessage(userMsgs[userMsgs.length - 1] || "");
      setMessages(botMsgs);
    };
  
    window.addEventListener("loadChatHistory", handleLoadHistory);
    return () => window.removeEventListener("loadChatHistory", handleLoadHistory);
  }, [setMessages]);

  
  const getBotDisplayName = (botType: BotType) => {
    switch (botType) {
      case "knowledge":
        return "Knowledge Bot";
      case "support":
        return "Support Bot";
      case "both":
        return "Hybrid Assistant";
      default:
        return "Assistant";
    }
  };

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;
  
    const userMessage: Message = {
      id: Date.now().toString(),
      content: inputValue.trim(),
      sender: "user",
      timestamp: new Date().toLocaleTimeString(),
    };
  
    setMessages(prev => [...prev, userMessage]);
    setInputValue("");
    setIsLoading(true);
  
    try {
      const res = await fetch(`http://127.0.0.1:8000/chat?chat_id=${chatId}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          question: userMessage.content,
          bot_type: selectedBot,
        }),
      });
  
      const data = await res.json();
      if (!chatId && data.chat_id) {
        setChatId(data.chat_id);   // <-- set new chat session
      }
  
      if (selectedBot === "both" && data.responses) {
        const botMessages = data.responses.map((r: any) => ({
          id: Date.now().toString() + Math.random(),
          content: r.text,
          sender: "bot",
          timestamp: new Date().toLocaleTimeString(),
          botType: r.bot.toLowerCase().includes("knowledge") ? "knowledge" : "support",
          images: r.images || [],
        }));
        setMessages(prev => [...prev, ...botMessages]);
      } else {
        const botMessage: Message = {
          id: (Date.now() + 1).toString(),
          content: data.text,
          sender: "bot",
          timestamp: new Date().toLocaleTimeString(),
          botType: selectedBot,
          images: data.images || [], 
        };
        setMessages(prev => [...prev, botMessage]);
      }
    } catch (err) {
      console.error("Error fetching bot response", err);
    } finally {
      setIsLoading(false);
    }
  };
  
  
  // ------------------------------------------------------------

  const getBotResponse = (userInput: string, botType: BotType): string => {
    const responses = {
      knowledge: [
        "Based on our knowledge base, here's what I found...",
        "I can help you with that information. According to our documentation...",
        "Great question! Our knowledge base indicates that...",
      ],
      support: [
        "I'll connect you with our support team right away.",
        "Let me escalate this to our technical support specialists.",
        "Our support team will assist you with this issue.",
      ],
      both: [
        "I'm combining knowledge base information with support insights...",
        "Let me provide you with comprehensive assistance using both knowledge and support resources...",
        "Drawing from our knowledge base and support expertise...",
      ],
    };

    const botResponses = responses[botType];
    return botResponses[Math.floor(Math.random() * botResponses.length)];
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const suggestedQuestions = [
    "Explanation of Provider Payments",
    "Virtual Card Payment",
    "Life Cycle of a Virtual Card Payment  ",
    "What is Draft Number",
    "Whats the definition of ECHO Payment Method",
  ];

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
    <div className="border-b border-border bg-gradient-header">
        <div className="flex items-center justify-between p-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-white/20 backdrop-blur-sm rounded-lg">
              <Sparkles className="h-5 w-5 text-white" />
            </div>
            <div>
              <h1 className="text-lg font-semibold text-white">
                RAG BOT (Retrieval-Augmented Generation)
              </h1>
            </div>
          </div>
          <div className="flex items-center gap-3">
          <Button
            size="sm"
            variant="outline"
            onClick={async () => {
              try {
                const res = await fetch("http://127.0.0.1:8000/new-chat", {
                  method: "POST"
                });
                const data = await res.json();

                setMessages([]);
                setChatId(data.chat_id); // <-- new id from backend
                console.log("New chat created:", data.chat_id);
              } catch (err) {
                console.error("Failed to create new chat:", err);
              }
            }}
            className="bg-white/10 text-white border-white/20 hover:bg-white/20"
          >
            New Chat
          </Button>
            <Badge
              variant="secondary"
              className="bg-success/20 text-success border-success/30"
            >
              <div className="w-2 h-2 bg-success rounded-full mr-2"></div>
              Online
            </Badge>
            {/* {selectedModelSelector} */}
          </div>
        </div>
      </div>
  
      {/* Scrollable Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 ? (
          <div className="flex-1 flex items-center justify-center">
            <div className="text-center max-w-md">
              <div className="p-4 bg-gradient-header rounded-full w-16 h-16 mx-auto mb-4 flex items-center justify-center">
                <BotIcon className="h-8 w-8 text-white" />
              </div>
              <h3 className="text-xl font-semibold text-foreground mb-2">
                Welcome to RAG Assistant
              </h3>
              <p className="text-muted-foreground mb-6">
                I'm here to help you with payment solutions and technical
                support. Ask me anything about our platform!
              </p>
  
              {/* Suggested Questions */}
              <div className="grid grid-cols-1 gap-2">
                <h4 className="text-sm font-medium text-foreground mb-3">
                  Try asking:
                </h4>
                {suggestedQuestions.map((question, index) => (
                  <Button
                    key={index}
                    variant="outline"
                    size="sm"
                    className="text-left justify-start h-auto p-3 text-wrap border-border hover:border-primary/50 hover:bg-accent/50 transition-colors"
                    onClick={() => setInputValue(question)}
                  >
                    <Sparkles className="h-3 w-3 mr-2 text-primary shrink-0" />
                    <span className="text-xs">{question}</span>
                  </Button>
                ))}
              </div>
            </div>
          </div>
        ) : (
          <>
            {messages.map((message) => (
              <div
                key={message.id}
                className={cn(
                  "flex gap-4 max-w-4xl animate-fade-in",
                  message.sender === "user"
                    ? "ml-auto flex-row-reverse"
                    : "mr-auto"
                )}
              >
                <Avatar className="flex-shrink-0 w-8 h-8">
                  <AvatarFallback
                    className={cn(
                      "text-white font-medium",
                      message.sender === "user" ? "bg-primary" : "bg-accent"
                    )}
                  >
                    {message.sender === "user" ? (
                      <User className="h-4 w-4" />
                    ) : (
                      <BotIcon className="h-4 w-4" />
                    )}
                  </AvatarFallback>
                </Avatar>
  
                <Card
                  className={cn(
                    "p-3 max-w-[80%] shadow-sm",
                    message.sender === "user"
                      ? "bg-primary text-primary-foreground"
                      : "bg-card text-card-foreground border-border"
                  )}
                >
                  <div className="flex items-center gap-2 mb-1">
                      <span className="text-xs font-medium">
                        {message.sender === "user"
                          ? "You"
                          : getBotDisplayName(message.botType || selectedBot)}
                      </span>
                      <span className="text-xs opacity-70">{message.timestamp}</span>
                    </div>

                    {/* Text response */}
                    {/* <div className="text-sm leading-relaxed space-y-1">
                        {message.content.includes("- ") ? (
                          <ul className="list-disc ml-5 space-y-1">
                            {message.content.split("\n").map((line, idx) =>
                              line.trim().startsWith("-") ? (
                                <li key={idx}>{line.replace(/^-/, "").trim()}</li>
                              ) : (
                                <p key={idx}>{line}</p>
                              )
                            )}
                          </ul>
                        ) : (
                          <p>{message.content}</p>
                        )}
                      </div> */}
                      <div className="text-sm leading-relaxed space-y-1">
                        {message.content.includes("- ") ? (
                          <ul className="list-disc ml-5 space-y-1">
                            {message.content.split("\n").map((line, idx) =>
                              line.trim().startsWith("-") ? (
                                <li key={idx}>
                                  <div className="inline prose prose-sm max-w-none">
                                    <ReactMarkdown>{line.replace(/^-/, "").trim()}</ReactMarkdown>
                                  </div>
                                </li>
                              ) : (
                                <div key={idx} className="prose prose-sm max-w-none">
                                  <ReactMarkdown>{line}</ReactMarkdown>
                                </div>
                              )
                            )}
                          </ul>
                        ) : (
                          // <div className="prose prose-sm max-w-none">
                          //   <ReactMarkdown>{message.content}</ReactMarkdown>
                          // </div>
                          <div className="prose prose-sm max-w-none">
                            <ReactMarkdown rehypePlugins={[rehypeRaw]}>
                              {message.content}
                            </ReactMarkdown>
                          </div>
                        )}
                      </div>

                    {/* Images */}
                    {message.images && message.images.length > 0 && (
                    <div className="mt-2 space-y-2">
                      {message.images.map((img, idx) => {
                        const imageUrl = img.startsWith("http")
                          ? img
                          : `http://127.0.0.1:8000${img}`;

                        return (
                          <img
                            key={idx}
                            src={imageUrl}
                            alt={`related-${idx}`}
                            className="rounded-lg max-w-full border border-border"
                            onError={(e) => {
                              e.currentTarget.style.display = "none"; // Hide if broken
                            }}
                          />
                        );
                      })}
                    </div>
                  )}
                  </Card>
              </div>
            ))}
  
            {isLoading && (
              <div className="flex gap-3 max-w-4xl mr-auto">
                <Avatar className="flex-shrink-0 w-8 h-8">
                  <AvatarFallback className="bg-accent text-white">
                    <BotIcon className="h-4 w-4" />
                  </AvatarFallback>
                </Avatar>
                <Card className="p-3 bg-card text-foreground shadow-sm">
                  <div className="flex items-center gap-2">
                    <Loader2 className="h-4 w-4 animate-spin text-primary" />
                    <span className="text-sm">Thinking...</span>
                  </div>
                </Card>
              </div>
            )}
            <div ref={messagesEndRef} />
          </>
        )}
      </div>
  
      {/* Fixed Input */}
      <div className="border-t border-border bg-card sticky bottom-0">
        <div className="max-w-4xl mx-auto p-4">
          <div className="flex gap-3">
            <div className="flex-1 relative">
              <Textarea
                ref={textareaRef}
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Ask your question..."
                className="min-h-[60px] max-h-[120px] resize-none pr-12 bg-background border-border focus:border-primary/50 transition-colors text-sm"
                disabled={isLoading}
              />
              <div className="absolute bottom-2 right-2 text-xs text-muted-foreground">
                Enter to send
              </div>
            </div>
            <Button
              onClick={handleSendMessage}
              disabled={!inputValue.trim() || isLoading}
              size="sm"
              className="px-4 py-2 bg-primary hover:bg-primary/90 text-primary-foreground"
            >
              {isLoading ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Send className="h-4 w-4" />
              )}
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
  
}
