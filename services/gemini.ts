import { GoogleGenAI, GenerateContentResponse, Part } from "@google/genai";
import { Message, MessageRole, GeneratedAsset, AnalysisData, Attachment } from "../types";

const API_KEY = process.env.API_KEY || '';

// System instruction to guide Gemini to act as a Mobile Dev Architect
const SYSTEM_INSTRUCTION = `
You are an expert AI Mobile Full Stack Architect. Your goal is to assist developers in building high-quality mobile applications using React Native, Expo, and Node.js.

You have three main capabilities:
1. **Chat & Advice:** Answer questions about mobile dev patterns, libraries (React Navigation, TanStack Query, Supabase), and best practices.
2. **Code Generation:** When asked for code, provide clean, TypeScript-based React Native code.
3. **UI Preview:** When asked to "preview" or "show" a screen, you MUST generate a standard HTML string using Tailwind CSS that visually approximates the mobile screen.
4. **Vision:** You can analyze images provided by the user (wireframes, screenshots, or error logs) to generate code or provide feedback.

**CRITICAL OUTPUT RULES:**
- If the user asks for a UI preview, wrap the HTML/Tailwind code in a block labeled \`\`\`html-preview ... \`\`\`.
- If the user asks for React Native code, wrap it in \`\`\`tsx ... \`\`\`.
- If the user asks for backend analysis or complexity stats, provide a JSON block \`\`\`json-analysis ... \`\`\` with an array of objects: [{ "name": "Metric", "value": 80, "fullMark": 100 }].

Example "html-preview":
\`\`\`html-preview
<div class="flex flex-col h-full bg-white p-4">
  <h1 class="text-2xl font-bold text-gray-900">Welcome</h1>
</div>
\`\`\`
`;

export const sendMessageToGemini = async (
  history: Message[],
  newMessage: string,
  attachments: Attachment[] = [],
  onStream: (chunk: string) => void
): Promise<string> => {
  if (!API_KEY) throw new Error("API Key is missing");

  const ai = new GoogleGenAI({ apiKey: API_KEY });
  
  // Transform history for the chat context
  // We need to exclude the very last message if it was optimistically added to the UI state
  // because we are sending it as the 'message' parameter.
  const historyToUse = history.slice(0, history.length - 1);

  const chatHistory = historyToUse.map(msg => {
    const parts: Part[] = [{ text: msg.content }];
    
    // Add history attachments if any
    if (msg.attachments && msg.attachments.length > 0) {
      msg.attachments.forEach(att => {
        parts.push({
          inlineData: {
            mimeType: att.mimeType,
            data: att.data
          }
        });
      });
    }

    return {
      role: msg.role === MessageRole.User ? 'user' : 'model',
      parts: parts
    };
  });

  const chat = ai.chats.create({
    model: 'gemini-2.5-flash',
    config: {
      systemInstruction: SYSTEM_INSTRUCTION,
      temperature: 0.7, 
    },
    history: chatHistory
  });

  // Construct current message parts
  const currentMessageParts: Part[] = [{ text: newMessage }];
  if (attachments.length > 0) {
    attachments.forEach(att => {
      currentMessageParts.push({
        inlineData: {
          mimeType: att.mimeType,
          data: att.data
        }
      });
    });
  }

  const result = await chat.sendMessageStream({ 
    message: currentMessageParts 
  });
  
  let fullText = "";
  for await (const chunk of result) {
    const text = (chunk as GenerateContentResponse).text;
    if (text) {
      fullText += text;
      onStream(text);
    }
  }

  return fullText;
};

// Helper to extract assets from the raw markdown response
export const parseGeneratedAssets = (response: string): GeneratedAsset[] => {
  const assets: GeneratedAsset[] = [];

  // Extract HTML Preview
  const htmlMatch = response.match(/```html-preview([\s\S]*?)```/);
  if (htmlMatch && htmlMatch[1]) {
    assets.push({
      type: 'preview',
      content: htmlMatch[1].trim(),
      language: 'html',
      title: 'UI Preview'
    });
  }

  // Extract TSX/JS Code (React Native)
  const codeMatches = response.matchAll(/```(tsx|typescript|javascript|jsx)([\s\S]*?)```/g);
  for (const match of codeMatches) {
    // We skip the html-preview block if it was accidentally matched as generic code (unlikely due to specific tag)
    if (match[1] !== 'html-preview') {
      assets.push({
        type: 'code',
        content: match[2].trim(),
        language: match[1],
        title: 'React Native Component'
      });
    }
  }

  // Extract Analysis Data
  const jsonMatch = response.match(/```json-analysis([\s\S]*?)```/);
  if (jsonMatch && jsonMatch[1]) {
     assets.push({
      type: 'analysis',
      content: jsonMatch[1].trim(),
      title: 'Project Analysis'
     });
  }

  return assets;
};

export const parseAnalysisData = (jsonString: string): AnalysisData[] => {
  try {
    return JSON.parse(jsonString);
  } catch (e) {
    console.error("Failed to parse analysis JSON", e);
    return [];
  }
}