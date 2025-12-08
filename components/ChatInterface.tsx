import React, { useRef, useEffect, useState } from 'react';
import { Message, MessageRole, Attachment } from '../types';
import { Send, Bot, User, Mic, MicOff, Paperclip, FileText, X } from 'lucide-react';
import ReactMarkdown from 'react-markdown';

interface ChatInterfaceProps {
  messages: Message[];
  onSendMessage: (text: string, attachments: Attachment[]) => void;
  isGenerating: boolean;
}

const ChatInterface: React.FC<ChatInterfaceProps> = ({ messages, onSendMessage, isGenerating }) => {
  const [input, setInput] = useState('');
  const [isListening, setIsListening] = useState(false);
  const [attachments, setAttachments] = useState<Attachment[]>([]);
  const scrollRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  
  // Auto-scroll to bottom
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSend = () => {
    if (!input.trim() && attachments.length === 0) return;
    onSendMessage(input, attachments);
    setInput('');
    setAttachments([]);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const files = Array.from(e.target.files);
      const newAttachments: Attachment[] = [];

      const readFile = (file: File): Promise<void> => {
        return new Promise((resolve) => {
            const reader = new FileReader();
            reader.onloadend = () => {
                const base64String = reader.result as string;
                // Split to get just the base64 data
                const base64Data = base64String.split(',')[1];
                
                // Fallback mime type for code files that might be empty
                let mimeType = file.type;
                if (!mimeType) {
                    if (file.name.match(/\.(js|jsx|ts|tsx|json|css|html|md|txt|py|java|c|cpp|h)$/i)) {
                        mimeType = 'text/plain';
                    } else {
                        mimeType = 'application/octet-stream';
                    }
                }

                newAttachments.push({
                    mimeType: mimeType,
                    data: base64Data,
                    fileName: file.name
                });
                resolve();
            };
            reader.readAsDataURL(file);
        });
      };

      await Promise.all(files.map(readFile));
      setAttachments(prev => [...prev, ...newAttachments]);
    }
    // Reset input so same file can be selected again
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const removeAttachment = (index: number) => {
    setAttachments(prev => prev.filter((_, i) => i !== index));
  };

  // Basic Speech Recognition setup
  const toggleListening = () => {
    if (isListening) {
      setIsListening(false);
      return;
    }

    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (SpeechRecognition) {
      const recognition = new SpeechRecognition();
      recognition.lang = 'en-US';
      recognition.continuous = false;
      
      recognition.onstart = () => setIsListening(true);
      recognition.onend = () => setIsListening(false);
      recognition.onresult = (event: any) => {
        const transcript = event.results[0][0].transcript;
        setInput((prev) => prev + (prev ? ' ' : '') + transcript);
      };
      
      recognition.start();
    } else {
      alert("Speech recognition not supported in this browser.");
    }
  };

  const renderAttachmentPreview = (att: Attachment, idx: number, isInput = false) => {
     const isImage = att.mimeType.startsWith('image/');
     
     if (isImage) {
         return (
             <img 
                key={idx}
                src={`data:${att.mimeType};base64,${att.data}`} 
                alt={att.fileName || "attachment"} 
                className={`${isInput ? 'h-16 w-16' : 'w-32 h-auto'} object-cover rounded-lg border border-gray-600`} 
             />
         );
     }

     return (
         <div key={idx} className={`${isInput ? 'h-16 w-16' : 'p-3'} bg-gray-800 border border-gray-600 rounded-lg flex ${isInput ? 'flex-col justify-center items-center text-[8px]' : 'items-center gap-2'} overflow-hidden`}>
             <FileText size={isInput ? 20 : 20} className="text-gray-400" />
             <span className={`${isInput ? 'w-full text-center truncate px-1' : 'text-xs text-gray-300 font-mono'}`}>
                 {att.fileName || 'File'}
             </span>
         </div>
     );
  };

  return (
    <div className="flex flex-col h-full bg-gray-900 rounded-xl overflow-hidden border border-gray-800 shadow-2xl">
      {/* Header */}
      <div className="bg-gray-800 p-4 border-b border-gray-700 flex items-center gap-3">
        <div className="p-2 bg-indigo-600 rounded-lg">
          <Bot className="text-white" size={20} />
        </div>
        <div>
          <h2 className="font-semibold text-white">Gemini Architect</h2>
          <p className="text-xs text-gray-400">Powered by Gemini 2.5 Flash</p>
        </div>
      </div>

      {/* Messages Area */}
      <div ref={scrollRef} className="flex-1 overflow-y-auto p-4 space-y-6">
        {messages.length === 0 && (
          <div className="text-center text-gray-500 mt-20">
            <Bot size={48} className="mx-auto mb-4 opacity-20" />
            <p className="text-lg font-medium">Start building your mobile app.</p>
            <p className="text-sm">Try "Create a login screen" or upload a wireframe.</p>
          </div>
        )}
        
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex gap-4 ${msg.role === MessageRole.User ? 'flex-row-reverse' : ''}`}
          >
            <div
              className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                msg.role === MessageRole.User ? 'bg-indigo-500 text-white' : 'bg-gray-700 text-green-400'
              }`}
            >
              {msg.role === MessageRole.User ? <User size={16} /> : <Bot size={16} />}
            </div>
            
            <div className={`flex flex-col max-w-[85%] ${msg.role === MessageRole.User ? 'items-end' : 'items-start'}`}>
              {/* Render Attachments */}
              {msg.attachments && msg.attachments.length > 0 && (
                 <div className="flex flex-wrap gap-2 mb-2 justify-end">
                    {msg.attachments.map((att, idx) => renderAttachmentPreview(att, idx))}
                 </div>
              )}

              <div
                className={`rounded-2xl p-4 text-sm leading-6 ${
                  msg.role === MessageRole.User
                    ? 'bg-indigo-600 text-white rounded-tr-none'
                    : 'bg-gray-800 text-gray-200 rounded-tl-none border border-gray-700'
                }`}
              >
                <ReactMarkdown 
                  components={{
                      code({node, className, children, ...props}) {
                          return <code className="bg-black/30 px-1 py-0.5 rounded text-indigo-300 font-mono" {...props}>{children}</code>
                      }
                  }}
                >
                  {msg.content}
                </ReactMarkdown>
              </div>
            </div>
          </div>
        ))}
        {isGenerating && (
          <div className="flex gap-4">
             <div className="w-8 h-8 rounded-full bg-gray-700 flex items-center justify-center">
               <Bot size={16} className="text-green-400 animate-pulse" />
             </div>
             <div className="bg-gray-800 px-4 py-3 rounded-2xl rounded-tl-none border border-gray-700 flex items-center gap-2">
                <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></span>
                <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-75"></span>
                <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-150"></span>
             </div>
          </div>
        )}
      </div>

      {/* Input Area */}
      <div className="p-4 bg-gray-800 border-t border-gray-700">
        {/* Attachment Previews */}
        {attachments.length > 0 && (
          <div className="flex gap-3 mb-3 overflow-x-auto pb-2">
            {attachments.map((att, idx) => (
              <div key={idx} className="relative group flex-shrink-0">
                {renderAttachmentPreview(att, idx, true)}
                <button 
                  onClick={() => removeAttachment(idx)}
                  className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full p-0.5 shadow-md hover:bg-red-600 z-10"
                >
                  <X size={12} />
                </button>
              </div>
            ))}
          </div>
        )}

        <div className="relative flex items-center gap-2">
          <input 
            type="file" 
            ref={fileInputRef}
            onChange={handleFileSelect}
            className="hidden"
            multiple
          />
          <button 
            onClick={() => fileInputRef.current?.click()}
            className="p-3 bg-gray-700 text-gray-400 hover:text-white rounded-xl transition-colors hover:bg-gray-600"
            title="Attach file"
          >
             <Paperclip size={20} />
          </button>
          
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Describe your mobile app component..."
            className="flex-1 bg-gray-900 border border-gray-700 text-white rounded-xl px-4 py-3 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-all placeholder-gray-500"
            disabled={isGenerating}
          />
          <button 
            onClick={toggleListening}
            className={`p-3 rounded-xl transition-colors ${isListening ? 'bg-red-500/20 text-red-500' : 'bg-gray-700 text-gray-400 hover:text-white'}`}
            title="Voice input"
          >
             {isListening ? <MicOff size={20} /> : <Mic size={20} />}
          </button>
          <button
            onClick={handleSend}
            disabled={(!input.trim() && attachments.length === 0) || isGenerating}
            className="bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed text-white p-3 rounded-xl transition-colors"
          >
            <Send size={20} />
          </button>
        </div>
        <p className="text-[10px] text-gray-500 mt-2 text-center">
            AI can make mistakes. Verify code before production use.
        </p>
      </div>
    </div>
  );
};

export default ChatInterface;