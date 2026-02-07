import React, { useCallback } from 'react';
import { Copy, Download } from 'lucide-react';

interface CodeBlockProps {
  code: string;
  language?: string;
}

const CodeBlock: React.FC<CodeBlockProps> = React.memo(({ code, language = 'typescript' }) => {
  const copyToClipboard = useCallback(() => {
    navigator.clipboard.writeText(code);
  }, [code]);

  const downloadCode = useCallback(() => {
    const blob = new Blob([code], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `Component.${language === 'typescript' || language === 'tsx' ? 'tsx' : 'js'}`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }, [code, language]);

  return (
    <div className="rounded-lg overflow-hidden bg-[#1e1e1e] border border-gray-700 my-4 shadow-lg">
      <div className="flex items-center justify-between px-4 py-2 bg-[#2d2d2d] border-b border-gray-700">
        <span className="text-xs text-gray-400 font-mono uppercase">{language}</span>
        <div className="flex items-center gap-2">
            <button 
            onClick={downloadCode}
            className="text-gray-400 hover:text-white transition-colors"
            title="Download code file"
            >
            <Download size={14} />
            </button>
            <button 
            onClick={copyToClipboard}
            className="text-gray-400 hover:text-white transition-colors"
            title="Copy code"
            >
            <Copy size={14} />
            </button>
        </div>
      </div>
      <div className="p-4 overflow-x-auto">
        <pre className="font-mono text-sm leading-relaxed text-gray-300">
          <code>{code}</code>
        </pre>
      </div>
    </div>
  );
});

CodeBlock.displayName = 'CodeBlock';

export default CodeBlock;