import React from 'react';

interface MobileSimulatorProps {
  htmlContent: string;
}

const MobileSimulator: React.FC<MobileSimulatorProps> = ({ htmlContent }) => {
  return (
    <div className="relative mx-auto border-gray-800 bg-gray-800 border-[14px] rounded-[2.5rem] h-[600px] w-[300px] shadow-xl flex flex-col">
      <div className="h-[32px] w-[3px] bg-gray-800 absolute -left-[17px] top-[72px] rounded-l-lg"></div>
      <div className="h-[46px] w-[3px] bg-gray-800 absolute -left-[17px] top-[124px] rounded-l-lg"></div>
      <div className="h-[46px] w-[3px] bg-gray-800 absolute -left-[17px] top-[178px] rounded-l-lg"></div>
      <div className="h-[64px] w-[3px] bg-gray-800 absolute -right-[17px] top-[142px] rounded-r-lg"></div>
      
      {/* Notch / Top Bar */}
      <div className="rounded-[2rem] overflow-hidden w-full h-full bg-white relative">
        <div className="absolute top-0 w-full h-8 bg-gray-100/90 backdrop-blur-sm z-10 flex items-center justify-between px-6">
            <span className="text-[10px] font-bold text-gray-900">9:41</span>
            <div className="flex space-x-1">
                <div className="w-3 h-3 bg-gray-900 rounded-full text-[8px] flex items-center justify-center text-white">5G</div>
                <div className="w-4 h-3 bg-gray-300 rounded-sm overflow-hidden border border-gray-400 relative">
                     <div className="bg-gray-900 h-full w-[80%]"></div>
                </div>
            </div>
        </div>
        
        {/* Content Area */}
        <div className="w-full h-full pt-8 overflow-y-auto no-scrollbar">
           {/* Render safe HTML here. In a real app, use an iframe for total isolation. 
               Here we trust the Gemini output (sanitized by context) for demo purposes. */}
           <div 
             className="w-full min-h-full"
             dangerouslySetInnerHTML={{ __html: htmlContent }} 
           />
        </div>

        {/* Home Indicator */}
        <div className="absolute bottom-1 left-1/2 transform -translate-x-1/2 w-32 h-1 bg-gray-900 rounded-full opacity-20"></div>
      </div>
    </div>
  );
};

export default MobileSimulator;