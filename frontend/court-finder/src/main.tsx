// src/main.tsx
import React from 'react';
import ReactDOM from 'react-dom';
import App from './App';
import './index.css'; // Assuming you have global styles here

ReactDOM.render(
  <React.StrictMode>
      <App />
  </React.StrictMode>,
  document.getElementById('root')
);
