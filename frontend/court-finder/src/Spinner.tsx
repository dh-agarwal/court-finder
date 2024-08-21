import React from 'react';
import './Spinner.css';

interface SpinnerProps {
  message: string;
}

const Spinner: React.FC<SpinnerProps> = ({ message }) => {
  return (
    <div className="spinner-overlay">
      <div className="spinner"></div>
      <div className="loading-message">{message}</div>
    </div>
  );
};

export default Spinner;
