import { useEffect, useRef, useState } from 'react';

/**
 * WebSocket hook with basic reconnection logic.
 *
 * - Automatically reconnects with exponential backoff when the connection drops.
 * - Exposes connection state, last message, and a send helper.
 */
const useWebSocket = (url, { maxRetries = 5, initialDelayMs = 1000 } = {}) => {
  const [message, setMessage] = useState(null);
  const [isConnected, setIsConnected] = useState(false);
  const ws = useRef(null);
  const retriesRef = useRef(0);
  const manualCloseRef = useRef(false);
  const reconnectTimeoutRef = useRef(null);

  useEffect(() => {
    manualCloseRef.current = false;

    const connect = () => {
      if (manualCloseRef.current) return;

      ws.current = new WebSocket(url);

      ws.current.onopen = () => {
        console.log('WebSocket connected');
        setIsConnected(true);
        retriesRef.current = 0;
      };

      ws.current.onmessage = (event) => {
        try {
          const parsed = JSON.parse(event.data);
          setMessage(parsed);
        } catch {
          setMessage(event.data);
        }
      };

      const scheduleReconnect = () => {
        setIsConnected(false);
        if (manualCloseRef.current) return;
        if (retriesRef.current >= maxRetries) {
          console.warn('Max WebSocket reconnection attempts reached.');
          return;
        }
        const delay =
          initialDelayMs * Math.pow(2, retriesRef.current); // exponential backoff
        retriesRef.current += 1;
        console.info(`Reconnecting WebSocket in ${delay}ms (attempt ${retriesRef.current})`);
        reconnectTimeoutRef.current = setTimeout(connect, delay);
      };

      ws.current.onclose = () => {
        console.log('WebSocket disconnected');
        scheduleReconnect();
      };

      ws.current.onerror = (error) => {
        console.error('WebSocket error:', error);
        scheduleReconnect();
      };
    };

    connect();

    return () => {
      manualCloseRef.current = true;
      setIsConnected(false);
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (ws.current) {
        ws.current.close();
      }
    };
  }, [url, maxRetries, initialDelayMs]);

  const sendMessage = (msg) => {
    if (ws.current && ws.current.readyState === WebSocket.OPEN) {
      ws.current.send(msg);
    } else {
      console.warn('WebSocket not connected.');
    }
  };

  return { message, isConnected, sendMessage };
};

export default useWebSocket;
