import React from 'react';
import './Spinner.css';

const Spinner = ({ message }) => {
  return (
    <div className="spinner-overlay">
      <div className="spinner"></div>
      <div className="loading-message">{message}</div>
    </div>
  );
};

export default Spinner;
