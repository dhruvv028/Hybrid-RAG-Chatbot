// //index.tsx
// import { useState, useEffect } from "react";
// import { ChatSidebar, type BotType } from "@/components/ChatSidebar";
// import { ChatInterface } from "@/components/ChatInterface";
// import { ModelSelector, type LLMModel } from "@/components/ModelSelector";

// interface ChatSummary {
//   id: string;
//   title: string;
//   timestamp: string;
//   originalPrompt: string;
// }

// const Index = () => {
//   const [selectedBot, setSelectedBot] = useState<BotType>("knowledge");
//   const [selectedChatId, setSelectedChatId] = useState<string>();
//   const [selectedModel, setSelectedModel] = useState<LLMModel>("gpt-4");
//   const [isCollapsed, setIsCollapsed] = useState(false);
//   const [chatHistory, setChatHistory] = useState<any[]>([]); // <-- dynamic

//   // ---------------- Fetch chat list dynamically ----------------
//   const fetchChatList = async () => {
//     try {
//       const res = await fetch("http://127.0.0.1:8000/list-chats");
//       const data = await res.json();
//       setChatHistory(data.chats || []);
//     } catch (err) {
//       console.error("Failed to fetch chat list:", err);
//     }
//   };

//   useEffect(() => {
//     fetchChatList();
//     const interval = setInterval(fetchChatList, 5000); // refresh every 5s
//     return () => clearInterval(interval);
//   }, []);

//   const handleChatSelect = async (chatId: string) => {
//     setSelectedChatId(chatId);

//     try {
//       const res = await fetch(`http://127.0.0.1:8000/chat-history/${chatId}`);
//       const data = await res.json();

//       const formattedMessages = data.messages.map((msg: any, idx: number) => ({
//         id: idx.toString(),
//         role: msg.role === "user" ? "user" : "assistant",
//         bot: msg.bot,
//         content: msg.response || msg.request,
//         images: msg.images || [],
//         documents: msg.documents || [],
//         timestamp: msg.timestamp || new Date().toLocaleTimeString(),
//       }));

//       window.dispatchEvent(
//         new CustomEvent("loadChatHistory", { detail: { messages: formattedMessages } })
//       );
//     } catch (error) {
//       console.error("Error fetching chat history:", error);
//     }
//   };

//   // ---------------- Create new chat ----------------
//   const handleNewChat = async () => {
//     try {
//       const res = await fetch("http://127.0.0.1:8000/new-chat", { method: "POST" });
//       const data = await res.json();
//       setSelectedChatId(data.chat_id);
  
//       // Refresh chat list immediately
//       await fetchChatList();
  
//       // Reset chat interface
//       window.dispatchEvent(new CustomEvent("loadChatHistory", { detail: { messages: [] } }));
//     } catch (err) {
//       console.error("Failed to create new chat:", err);
//     }
//   };

//   return (
//     <div className="min-h-screen bg-background flex">
//       <ChatSidebar
//         selectedBot={selectedBot}
//         onBotChange={setSelectedBot}
//         chatHistory={chatHistory}       // <-- dynamic
//         onChatSelect={handleChatSelect}
//         selectedChatId={selectedChatId}
//         isCollapsed={isCollapsed}
//         onToggleCollapse={() => setIsCollapsed(!isCollapsed)}
//       />
//       <div className="flex-1 flex flex-col">
//         <ChatInterface 
//           selectedBot={selectedBot} 
//           selectedModel={selectedModel}
//           selectedModelSelector={
//             <ModelSelector 
//               selectedModel={selectedModel}
//               onModelChange={setSelectedModel}
//             />
//           }
//           onPromptFromHistory={handleChatSelect}
//         />
//       </div>
//     </div>
//   );
// };


// export default Index;
// index.tsx
import { useState, useEffect } from "react";
import { ChatSidebar, type BotType } from "@/components/ChatSidebar";
import { ChatInterface } from "@/components/ChatInterface";
import { ModelSelector, type LLMModel } from "@/components/ModelSelector";

interface ChatSummary {
  id: string;
  title: string;
  timestamp: string;
  originalPrompt: string;
}

const Index = () => {
  const [selectedBot, setSelectedBot] = useState<BotType>("knowledge");
  const [selectedChatId, setSelectedChatId] = useState<string>();
  const [selectedModel, setSelectedModel] = useState<LLMModel>("gpt-4");
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [chatHistory, setChatHistory] = useState<ChatSummary[]>([]);

  // ---------------- Fetch chat list dynamically ----------------
  const fetchChatList = async () => {
    try {
      const res = await fetch("http://127.0.0.1:8000/list-chats");
      const data = await res.json();
      if (data.chats) setChatHistory(data.chats);
    } catch (err) {
      console.error("Failed to fetch chat list:", err);
    }
  };

  useEffect(() => {
    fetchChatList();

    // Optional: poll for new chats every 5 seconds
    const interval = setInterval(fetchChatList, 60000);
    return () => clearInterval(interval);
  }, []);

  // ---------------- Handle chat selection ----------------
  const handleChatSelect = async (chatId: string) => {
    setSelectedChatId(chatId);

    try {
      const res = await fetch(`http://127.0.0.1:8000/chat-history/${chatId}`);
      const data = await res.json();

      const formattedMessages = (data.messages || []).map((msg: any, idx: number) => ({
        id: idx.toString(),
        role: msg.role === "user" ? "user" : "assistant",
        bot: msg.bot,
        content: msg.response || msg.request,
        images: msg.images || [],
        documents: msg.documents || [],
        timestamp: msg.timestamp || new Date().toLocaleTimeString(),
      }));

      window.dispatchEvent(
        new CustomEvent("loadChatHistory", { detail: { messages: formattedMessages } })
      );
    } catch (error) {
      console.error("Error fetching chat history:", error);
    }
  };

  // ---------------- Create new chat ----------------
  const handleNewChat = async () => {
    try {
      const res = await fetch("http://127.0.0.1:8000/new-chat", { method: "POST" });
      const data = await res.json();
      setSelectedChatId(data.chat_id);

      // Refresh chat list immediately
      await fetchChatList();

      // Reset chat interface
      window.dispatchEvent(
        new CustomEvent("loadChatHistory", { detail: { messages: [] } })
      );
    } catch (err) {
      console.error("Failed to create new chat:", err);
    }
  };

  return (
    <div className="min-h-screen bg-background flex">
      {/* Sidebar */}
      <ChatSidebar
        selectedBot={selectedBot}
        onBotChange={setSelectedBot}
        chatHistory={chatHistory}
        onChatSelect={handleChatSelect}
        selectedChatId={selectedChatId}
        isCollapsed={isCollapsed}
        onToggleCollapse={() => setIsCollapsed(!isCollapsed)}
        onNewChat={handleNewChat} // pass new chat function
      />

      {/* Chat Interface */}
      <div className="flex-1 flex flex-col">
        <ChatInterface
          selectedBot={selectedBot}
          selectedModel={selectedModel}
          selectedModelSelector={
            <ModelSelector
              selectedModel={selectedModel}
              onModelChange={setSelectedModel}
            />
          }
          onPromptFromHistory={handleChatSelect}
        />
      </div>
    </div>
  );
};

export default Index;
