import React from 'react';

const Logo: React.FC<{ className?: string }> = ({ className = "" }) => {
  return (
    <svg 
      className={`w-8 h-8 ${className}`}
      viewBox="0 0 32 32" 
      fill="none" 
      xmlns="http://www.w3.org/2000/svg"
    >
      <rect width="32" height="32" rx="8" fill="#FF6600"/>
      <path 
        d="M8 12h16v2H8v-2zm0 4h12v2H8v-2zm0 4h8v2H8v-2z" 
        fill="white"
      />
      <circle cx="24" cy="8" r="3" fill="white"/>
    </svg>
  );
};

export default Logo;