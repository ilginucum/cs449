import React, { useState, useEffect } from 'react';
import { Card } from '@/components/ui/card';

const GestureInterface = () => {
  const [cursorPosition, setCursorPosition] = useState({ x: 0, y: 0 });
  const [activeButton, setActiveButton] = useState(null);
  const [scrollPosition, setScrollPosition] = useState(0);
  
  const buttons = [
    { id: 1, label: 'Open Menu', color: 'bg-blue-500' },
    { id: 2, label: 'Close Menu', color: 'bg-red-500' },
    { id: 3, label: 'Settings', color: 'bg-green-500' },
    { id: 4, label: 'Help', color: 'bg-purple-500' }
  ];

  const handleButtonHover = (buttonId) => {
    setActiveButton(buttonId);
  };

  const handleButtonClick = (buttonId) => {
    // Handle button click actions here
    console.log(`Button ${buttonId} clicked`);
  };

  return (
    <Card className="p-6 w-full max-w-4xl mx-auto">
      <div className="mb-4">
        <div className="text-2xl font-bold mb-4">Gesture Control Interface</div>
        
        {/* Cursor Indicator */}
        <div 
          className="w-4 h-4 bg-blue-500 rounded-full absolute"
          style={{ 
            left: `${cursorPosition.x}px`, 
            top: `${cursorPosition.y}px`,
            transition: 'all 0.1s ease-out',
            pointerEvents: 'none'
          }}
        />

        {/* Buttons */}
        <div className="grid grid-cols-2 gap-4 mb-6">
          {buttons.map((button) => (
            <button
              key={button.id}
              className={`${button.color} text-white p-4 rounded-lg transition-all
                ${activeButton === button.id ? 'scale-105 ring-2 ring-white' : ''}`}
              onMouseEnter={() => handleButtonHover(button.id)}
              onMouseLeave={() => handleButtonHover(null)}
              onClick={() => handleButtonClick(button.id)}
            >
              {button.label}
            </button>
          ))}
        </div>

        {/* Scrollable Content */}
        <div className="relative h-64 border rounded-lg overflow-hidden">
          <div 
            className="absolute w-full transition-transform"
            style={{ transform: `translateY(-${scrollPosition}px)` }}
          >
            {Array.from({ length: 20 }).map((_, i) => (
              <div key={i} className="p-4 border-b">
                Scrollable Content Item {i + 1}
              </div>
            ))}
          </div>
          
          {/* Scrollbar */}
          <div className="absolute right-0 top-0 w-2 h-full bg-gray-200">
            <div 
              className="w-full bg-blue-500 rounded"
              style={{
                height: '20%',
                transform: `translateY(${scrollPosition * 0.8}px)`,
                transition: 'transform 0.1s ease-out'
              }}
            />
          </div>
        </div>
      </div>
    </Card>
  );
};

export default GestureInterface;