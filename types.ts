export enum MessageRole {
  User = 'user',
  Model = 'model',
  System = 'system'
}

export interface Attachment {
  mimeType: string;
  data: string; // Base64 string
  fileName?: string;
}

export interface Message {
  id: string;
  role: MessageRole;
  content: string;
  timestamp: Date;
  isThinking?: boolean;
  attachments?: Attachment[];
}

export interface GeneratedAsset {
  type: 'code' | 'preview' | 'analysis';
  language?: string; // e.g., 'typescript', 'html'
  content: string;
  title?: string;
}

export interface AnalysisData {
  name: string;
  value: number;
  fullMark: number;
}

export interface AppState {
  messages: Message[];
  currentCode: string;
  currentPreviewHtml: string;
  isGenerating: boolean;
  analysisData: AnalysisData[];
}

export interface ChatSession {
  id: string;
  title: string;
  timestamp: number;
  state: AppState;
}