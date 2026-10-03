"use client";

import Header from "@/components/layout/Header";
import ChatInterface from "@/components/chat/ChatInterface";

export default function ChatPage() {
  return (
    <div className="h-screen max-h-screen flex flex-col bg-grid overflow-hidden">
      <Header
        title="AI Conversation"
        description="Multi-turn conversational code archaeology & general programming assistant powered by Sarvam AI"
      />

      <div className="flex-1 min-h-0 px-4 sm:px-8 py-4 w-full flex flex-col overflow-hidden">
        <ChatInterface />
      </div>
    </div>
  );
}
