import Cookies from 'js-cookie';
import { useState, useEffect } from 'react';

export const useToken = () => {
  const [tokens, setTokens] = useState<number>(100); // Default value

  useEffect(() => {
    // Check if the tokens cookie exists
    const tokenValue = Cookies.get('tokens');
    const lastReset = Cookies.get('lastReset');

    const today = new Date().toISOString().split('T')[0];

    if (lastReset !== today) {
      // Reset tokens daily
      Cookies.set('tokens', '100', { expires: 1 }); // reset daily
      Cookies.set('lastReset', today, { expires: 1 });
      setTokens(100);
    } else if (tokenValue) {
      setTokens(parseInt(tokenValue, 10));
    }
  }, []);

  const spendTokens = (amount: number) => {
    const currentTokens = Math.max(0, tokens - amount);
    setTokens(currentTokens);
    Cookies.set('tokens', currentTokens.toString(), { expires: 1 });
  };

  return { tokens, spendTokens };
};
