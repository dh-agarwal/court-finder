import React, { useEffect, useState } from 'react';
import { GiTennisBall } from 'react-icons/gi'; // Import the alternative tennis ball icon
import './CustomModal.css';

const CustomModal = ({ show, onClose, onConfirm, tokenCost, rectangleSize, courtCount, loading, loadingMessage }) => {
  const [dots, setDots] = useState(1);

  useEffect(() => {
    if (loading) {
      const interval = setInterval(() => {
        setDots(prevDots => (prevDots % 3) + 1);
      }, 600);
      return () => clearInterval(interval);
    }
  }, [loading]);

  if (!show) {
    return null;
  }

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <h2>{loading ? `${loadingMessage}${'.'.repeat(dots)}` : (courtCount !== null ? "" : "Confirm Search")}</h2>
        
        {!loading && courtCount === null && (
          <>
            <p>
              This search will cost <u>{tokenCost}</u> tokens. Do you want to proceed?
            </p>
            <p className="rectangle-size">
              Search area: {rectangleSize.width} miles x {rectangleSize.height} miles
            </p>
          </>
        )}
        
        {loading && (
          <div className="spinner-tennis">
            <GiTennisBall className="spinning-tennis-ball" />
          </div>
        )}
        
        {!loading && courtCount !== null && (
          <p>{courtCount > 0 ? `${courtCount} potential courts found!` : "No courts were found."}</p>
        )}
        
        <div className="modal-actions">
          {!loading && (
            <button className="modal-button cancel" onClick={onClose}>
              Close
            </button>
          )}
          {!loading && courtCount === null && (
            <button className="modal-button confirm" onClick={onConfirm}>
              Confirm
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default CustomModal;
