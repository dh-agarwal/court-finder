// src/main.tsx
import React from 'react';
import ReactDOM from 'react-dom';
import App from './App';
import { TokenProvider } from './TokenContext'; // Import the TokenProvider
import './index.css'; // Assuming you have global styles here

ReactDOM.render(
  <React.StrictMode>
    <TokenProvider> {/* Wrap the entire App with TokenProvider */}
      <App />
    </TokenProvider>
  </React.StrictMode>,
  document.getElementById('root')
);
