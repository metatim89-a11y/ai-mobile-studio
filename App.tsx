import React, { useState, useCallback, useEffect, useMemo, useRef, lazy, Suspense } from 'react';
import { Smartphone, Code2, BarChart2, Zap, History, Plus, MessageSquare, Trash2, Edit2, Save, X, Download } from 'lucide-react';
import ChatInterface from './components/ChatInterface';
import { AppState, Message, MessageRole, AnalysisData, Attachment, ChatSession } from './types';
import { sendMessageToGemini, parseGeneratedAssets, parseAnalysisData } from './services/gemini';
import { useDebounce } from './hooks/useDebounce';

// Lazy load heavy components that are not immediately visible
const MobileSimulator = lazy(() => import('./components/MobileSimulator'));
const CodeBlock = lazy(() => import('./components/CodeBlock'));
const AnalysisChart = lazy(() => import('./components/AnalysisChart'));

const INITIAL_PREVIEW_HTML = `
<div class="flex flex-col items-center justify-center h-full bg-gray-900 p-6 text-center">
  <div class="w-16 h-16 bg-indigo-500 rounded-2xl flex items-center justify-center mb-6 shadow-lg shadow-indigo-500/20">
    <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m5 8 6 6"/><path d="m4 14 6-6 2-3"/><path d="M2 5h12"/><path d="M7 2h1"/><path d="m22 22-5-10-5 10"/><path d="M14 17h6"/></svg>
  </div>
  <h1 class="text-2xl font-bold text-white mb-2">AI Mobile Studio</h1>
  <p class="text-gray-400 text-sm">Describe your app idea to generate a live preview and React Native code.</p>
</div>
`;

const INITIAL_ANALYSIS: AnalysisData[] = [
    { name: 'Performance', value: 0, fullMark: 100 },
    { name: 'Accessibility', value: 0, fullMark: 100 },
    { name: 'Best Practices', value: 0, fullMark: 100 },
    { name: 'SEO', value: 0, fullMark: 100 },
    { name: 'PWA', value: 0, fullMark: 100 },
];

const INITIAL_STATE: AppState = {
  messages: [],
  currentCode: '// React Native code will appear here...',
  currentPreviewHtml: INITIAL_PREVIEW_HTML,
  isGenerating: false,
  analysisData: INITIAL_ANALYSIS
};

export default function App() {
  const [activeTab, setActiveTab] = useState<'preview' | 'code' | 'analysis'>('preview');
  const [showHistory, setShowHistory] = useState(false);
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);
  const [isEditingTitle, setIsEditingTitle] = useState<string | null>(null);
  const [editTitleInput, setEditTitleInput] = useState("");

  const [state, setState] = useState<AppState>(INITIAL_STATE);

  // Debounced localStorage save function to prevent excessive writes
  const debouncedSaveToStorage = useDebounce((sessionsToSave: ChatSession[]) => {
    if (sessionsToSave.length > 0) {
      localStorage.setItem('ai_mobile_studio_sessions', JSON.stringify(sessionsToSave));
    }
  }, 500); // Wait 500ms after last change before saving

  // Load sessions from local storage on mount
  useEffect(() => {
    const saved = localStorage.getItem('ai_mobile_studio_sessions');
    if (saved) {
      try {
        const parsed = JSON.parse(saved);
        setSessions(parsed);
      } catch (e) {
        console.error("Failed to load sessions", e);
      }
    }
  }, []);

  // Save sessions to local storage whenever they change (debounced)
  useEffect(() => {
    debouncedSaveToStorage(sessions);
  }, [sessions, debouncedSaveToStorage]);

  // Auto-save current session state - Fixed dependency array
  useEffect(() => {
    if (currentSessionId && !state.isGenerating) {
      setSessions(prev => prev.map(session => 
        session.id === currentSessionId 
          ? { ...session, state: state, timestamp: Date.now() }
          : session
      ));
    }
  }, [state, currentSessionId, state.isGenerating]);

  const startNewSession = useCallback(() => {
    const newId = Date.now().toString();
    const newSession: ChatSession = {
      id: newId,
      title: 'New Project',
      timestamp: Date.now(),
      state: INITIAL_STATE
    };
    
    setSessions(prev => [newSession, ...prev]);
    setCurrentSessionId(newId);
    setState(INITIAL_STATE);
    setShowHistory(false);
  }, []);

  const loadSession = useCallback((session: ChatSession) => {
    setCurrentSessionId(session.id);
    setState(session.state);
    setShowHistory(false);
  }, []);

  const deleteSession = useCallback((e: React.MouseEvent, id: string) => {
    e.stopPropagation();
    setSessions(prev => prev.filter(s => s.id !== id));
    if (currentSessionId === id) {
      setCurrentSessionId(null);
      setState(INITIAL_STATE);
    }
  }, [currentSessionId]);

  const startEditingTitle = useCallback((e: React.MouseEvent, session: ChatSession) => {
    e.stopPropagation();
    setIsEditingTitle(session.id);
    setEditTitleInput(session.title);
  }, []);

  const saveTitle = useCallback((e: React.MouseEvent | React.KeyboardEvent, id: string) => {
    e.stopPropagation();
    if (editTitleInput.trim()) {
      setSessions(prev => prev.map(s => s.id === id ? { ...s, title: editTitleInput } : s));
    }
    setIsEditingTitle(null);
  }, [editTitleInput]);

  const exportProject = useCallback(() => {
    // Determine what to export: current session or create a new wrapper for current state
    const sessionToExport = currentSessionId 
        ? sessions.find(s => s.id === currentSessionId) 
        : { id: 'temp', title: 'Untitled Project', timestamp: Date.now(), state: state };
    
    if (!sessionToExport) return;

    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(sessionToExport, null, 2));
    const downloadAnchorNode = document.createElement('a');
    downloadAnchorNode.setAttribute("href", dataStr);
    downloadAnchorNode.setAttribute("download", `${(sessionToExport.title || 'project').replace(/\s+/g, '_')}_export.json`);
    document.body.appendChild(downloadAnchorNode); // required for firefox
    downloadAnchorNode.click();
    downloadAnchorNode.remove();
  }, [currentSessionId, sessions, state]);

  const handleSendMessage = useCallback(async (text: string, attachments: Attachment[] = []) => {
    // Ensure we have a session
    let sessionId = currentSessionId;
    if (!sessionId) {
       const newId = Date.now().toString();
       const newSession: ChatSession = {
         id: newId,
         title: text.slice(0, 30) || 'New Project',
         timestamp: Date.now(),
         state: INITIAL_STATE
       };
       setSessions(prev => [newSession, ...prev]);
       setCurrentSessionId(newId);
       sessionId = newId;
    }

    // Update UI immediately
    const newUserMessage: Message = {
      id: Date.now().toString(),
      role: MessageRole.User,
      content: text,
      timestamp: new Date(),
      attachments: attachments
    };

    setState(prev => ({
      ...prev,
      messages: [...prev.messages, newUserMessage],
      isGenerating: true
    }));

    try {
      let accumulatedResponse = "";
      
      // Use functional update to access latest state
      const currentMessages = await new Promise<Message[]>(resolve => {
        setState(prev => {
          resolve(prev.messages);
          return prev;
        });
      });

      await sendMessageToGemini(
        [...currentMessages, newUserMessage],
        text,
        attachments,
        (chunk) => {
           accumulatedResponse += chunk;
        }
      );

      const assets = parseGeneratedAssets(accumulatedResponse);
      
      setState(prev => {
        let newPreview = prev.currentPreviewHtml;
        let newCode = prev.currentCode;
        let newAnalysis = prev.analysisData;
        let activeTabOverride = activeTab;

        assets.forEach(asset => {
          if (asset.type === 'preview') {
            newPreview = asset.content;
            activeTabOverride = 'preview'; 
          } else if (asset.type === 'code') {
            newCode = asset.content;
            if (activeTabOverride !== 'preview') activeTabOverride = 'code';
          } else if (asset.type === 'analysis') {
              newAnalysis = parseAnalysisData(asset.content);
              activeTabOverride = 'analysis';
          }
        });
        
        const newBotMessage: Message = {
          id: (Date.now() + 1).toString(),
          role: MessageRole.Model,
          content: accumulatedResponse,
          timestamp: new Date()
        };

        const newState = {
          messages: [...prev.messages, newBotMessage],
          currentPreviewHtml: newPreview,
          currentCode: newCode,
          analysisData: newAnalysis,
          isGenerating: false
        };

        setActiveTab(activeTabOverride);

        // Explicit save after generation ensures "lastCode" is correct in storage
        setSessions(prevSessions => prevSessions.map(s => 
          s.id === sessionId ? { ...s, state: newState, timestamp: Date.now() } : s
        ));

        return newState;
      });

    } catch (error) {
      console.error(error);
      const errorMessage: Message = {
        id: Date.now().toString(),
        role: MessageRole.System,
        content: "Error: Failed to connect to Gemini AI.",
        timestamp: new Date()
      };
      setState(prev => ({
        ...prev,
        messages: [...prev.messages, errorMessage],
        isGenerating: false
      }));
    }
  }, [currentSessionId, activeTab]);

  return (
    <div className="h-screen w-screen bg-[#0f172a] text-white flex overflow-hidden">
      {/* Sidebar / Main Content Area */}
      <div className="flex-1 flex flex-col h-full max-w-2xl border-r border-gray-800 relative">
        <header className="p-4 border-b border-gray-800 flex items-center justify-between">
            <div className="flex items-center gap-2">
                <button 
                    onClick={() => setShowHistory(!showHistory)}
                    className={`p-2 rounded-lg transition-colors ${showHistory ? 'bg-indigo-600 text-white' : 'hover:bg-gray-800 text-gray-400'}`}
                >
                    <History size={20} />
                </button>
                <div className="flex items-center gap-2">
                    <Zap className="text-indigo-500" />
                    <h1 className="text-xl font-bold tracking-tight">AI Mobile Studio</h1>
                </div>
            </div>
            <div className="flex items-center">
                <button 
                    onClick={exportProject}
                    className="flex items-center gap-1 bg-gray-800 hover:bg-gray-700 text-white px-3 py-1.5 rounded-lg text-sm transition-colors border border-gray-700 mr-2"
                    title="Download Project JSON"
                >
                    <Download size={16} />
                    <span className="hidden sm:inline">Export</span>
                </button>
                <button 
                    onClick={startNewSession}
                    className="flex items-center gap-1 bg-indigo-600 hover:bg-indigo-500 text-white px-3 py-1.5 rounded-lg text-sm transition-colors"
                >
                    <Plus size={16} />
                    <span className="hidden sm:inline">New Project</span>
                </button>
            </div>
        </header>

        {/* History Drawer Overlay */}
        {showHistory && (
             <div className="absolute top-[65px] bottom-0 left-0 w-full bg-gray-900 z-20 overflow-y-auto border-r border-gray-800 animate-in slide-in-from-left duration-200">
                <div className="p-4 space-y-2">
                    <h3 className="text-gray-400 text-xs font-semibold uppercase tracking-wider mb-4 pl-2">Project History</h3>
                    {sessions.length === 0 && (
                        <div className="text-center text-gray-500 py-10">No saved projects yet.</div>
                    )}
                    {sessions.map(session => (
                        <div 
                            key={session.id}
                            onClick={() => loadSession(session)}
                            className={`group flex items-center justify-between p-3 rounded-lg cursor-pointer transition-all ${currentSessionId === session.id ? 'bg-indigo-900/40 border border-indigo-500/30' : 'hover:bg-gray-800 border border-transparent'}`}
                        >
                            <div className="flex items-center gap-3 overflow-hidden">
                                <MessageSquare size={16} className={currentSessionId === session.id ? 'text-indigo-400' : 'text-gray-500'} />
                                {isEditingTitle === session.id ? (
                                    <input 
                                        autoFocus
                                        type="text"
                                        value={editTitleInput}
                                        onChange={(e) => setEditTitleInput(e.target.value)}
                                        onClick={(e) => e.stopPropagation()}
                                        onKeyDown={(e) => e.key === 'Enter' && saveTitle(e, session.id)}
                                        onBlur={(e) => saveTitle(e, session.id)}
                                        className="bg-gray-950 border border-gray-700 text-white text-sm rounded px-2 py-1 outline-none focus:border-indigo-500"
                                    />
                                ) : (
                                    <div className="flex flex-col">
                                        <span className="text-sm font-medium truncate w-48 text-gray-200">{session.title}</span>
                                        <span className="text-[10px] text-gray-500">{new Date(session.timestamp).toLocaleDateString()}</span>
                                    </div>
                                )}
                            </div>
                            <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                                <button 
                                    onClick={(e) => startEditingTitle(e, session)}
                                    className="p-1.5 hover:bg-gray-700 rounded-md text-gray-400 hover:text-white"
                                >
                                    <Edit2 size={14} />
                                </button>
                                <button 
                                    onClick={(e) => deleteSession(e, session.id)}
                                    className="p-1.5 hover:bg-red-900/50 rounded-md text-gray-400 hover:text-red-400"
                                >
                                    <Trash2 size={14} />
                                </button>
                            </div>
                        </div>
                    ))}
                </div>
             </div>
        )}

        <div className="flex-1 overflow-hidden p-4">
            <ChatInterface 
                messages={state.messages} 
                onSendMessage={handleSendMessage}
                isGenerating={state.isGenerating}
            />
        </div>
      </div>

      {/* Right Panel: Tools & Preview */}
      <div className="flex-1 flex flex-col bg-[#0d1117]">
        {/* Tabs */}
        <div className="flex border-b border-gray-800">
          <button
            onClick={() => setActiveTab('preview')}
            className={`flex-1 py-4 text-sm font-medium flex items-center justify-center gap-2 transition-colors ${
              activeTab === 'preview' 
                ? 'text-indigo-400 border-b-2 border-indigo-500 bg-gray-900/50' 
                : 'text-gray-400 hover:text-white hover:bg-gray-800/50'
            }`}
          >
            <Smartphone size={16} />
            Live Preview
          </button>
          <button
            onClick={() => setActiveTab('code')}
            className={`flex-1 py-4 text-sm font-medium flex items-center justify-center gap-2 transition-colors ${
              activeTab === 'code' 
                ? 'text-indigo-400 border-b-2 border-indigo-500 bg-gray-900/50' 
                : 'text-gray-400 hover:text-white hover:bg-gray-800/50'
            }`}
          >
            <Code2 size={16} />
            React Native Code
          </button>
          <button
            onClick={() => setActiveTab('analysis')}
            className={`flex-1 py-4 text-sm font-medium flex items-center justify-center gap-2 transition-colors ${
              activeTab === 'analysis' 
                ? 'text-indigo-400 border-b-2 border-indigo-500 bg-gray-900/50' 
                : 'text-gray-400 hover:text-white hover:bg-gray-800/50'
            }`}
          >
            <BarChart2 size={16} />
            App Analysis
          </button>
        </div>

        {/* Panel Content */}
        <div className="flex-1 overflow-y-auto p-8 relative bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-indigo-900/20 via-gray-900 to-gray-900">
          
          {activeTab === 'preview' && (
            <div className="flex flex-col h-full items-center justify-center animate-in fade-in duration-500">
              <Suspense fallback={<div className="text-gray-400">Loading preview...</div>}>
                <MobileSimulator htmlContent={state.currentPreviewHtml} />
              </Suspense>
              <p className="mt-6 text-sm text-gray-500">
                Visual approximation based on Tailwind CSS
              </p>
            </div>
          )}

          {activeTab === 'code' && (
            <div className="h-full animate-in fade-in duration-500">
               <h3 className="text-gray-400 text-sm mb-4">Generated React Native (Expo) Component</h3>
               <Suspense fallback={<div className="text-gray-400">Loading code...</div>}>
                 <CodeBlock code={state.currentCode} language="typescript" />
               </Suspense>
            </div>
          )}

          {activeTab === 'analysis' && (
              <div className="h-full flex flex-col items-center justify-center animate-in fade-in duration-500 max-w-lg mx-auto">
                  <Suspense fallback={<div className="text-gray-400">Loading analysis...</div>}>
                    <AnalysisChart data={state.analysisData} />
                  </Suspense>
                  <div className="mt-8 p-4 bg-gray-800/50 rounded-lg border border-gray-700 w-full">
                      <h4 className="text-indigo-400 font-semibold mb-2">AI Insights</h4>
                      <p className="text-sm text-gray-300 leading-relaxed">
                          Request an analysis in the chat (e.g., "Analyze the complexity of this login screen") to populate this chart with metrics regarding performance, security, and best practices.
                      </p>
                  </div>
              </div>
          )}
        </div>
      </div>
    </div>
  );
}