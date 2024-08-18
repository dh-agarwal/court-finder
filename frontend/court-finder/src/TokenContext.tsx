// TokenContext.tsx
import React, { createContext, useState, useContext, ReactNode } from 'react';

interface TokenContextType {
  tokens: number;
}

const TokenContext = createContext<TokenContextType | undefined>(undefined);

export const TokenProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [tokens] = useState<number>(500); // Starting with 500 tokens

  return (
    <TokenContext.Provider value={{ tokens }}>
      {children}
    </TokenContext.Provider>
  );
};

export const useToken = () => {
  const context = useContext(TokenContext);
  if (!context) {
    throw new Error('useToken must be used within a TokenProvider');
  }
  return context;
};
