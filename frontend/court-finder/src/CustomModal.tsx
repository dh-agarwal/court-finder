import React, { useEffect, useState } from 'react';
import { GiTennisBall } from 'react-icons/gi';
import './CustomModal.css';

const CustomModal = ({ show, onClose, onConfirm, tokenCost, rectangleSize, courtCount, loading, loadingMessage, tokens, error }) => {
  const [dots, setDots] = useState(1);

  useEffect(() => {
    if (loading) {
      const interval = setInterval(() => {
        setDots(prevDots => (prevDots % 3) + 1);
      }, 600);
      return () => clearInterval(interval);
    }
  }, [loading]);

  if (!show) return null;

  const hasEnoughTokens = tokens >= tokenCost;

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <h2>
          {loading
            ? `${loadingMessage}${'.'.repeat(dots)}`
            : courtCount !== null
            ? courtCount > 0
              ? "Search Results"
              : "No Courts Found"
            : "Confirm Search"}
        </h2>

        {!loading && courtCount === null && !error && (
          <>
            <p>This search will cost <u>{tokenCost}</u> tokens. Do you want to proceed?</p>
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

        {!loading && courtCount !== null && !error && (
          <p>
            {courtCount > 0
              ? `${courtCount} potential court${courtCount > 1 ? 's' : ''} found!`
              : "No courts were found."}
          </p>
        )}

        {!loading && error && (
          <p style={{ color: 'red' }}>
            {error}
          </p>
        )}

        <div className="modal-actions">
          {!loading && (
            <button className="modal-button cancel" onClick={onClose}>
              Close
            </button>
          )}
          {!loading && courtCount === null && !error && (
            <button
              className="modal-button confirm"
              onClick={hasEnoughTokens ? onConfirm : undefined}
              disabled={!hasEnoughTokens}
              title={!hasEnoughTokens ? "You don't have enough tokens. Tokens reset daily at midnight." : ""}
            >
              Confirm
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default CustomModal;
