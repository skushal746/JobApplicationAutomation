import { useEffect, useState, useCallback } from 'react';

export const useWebSocket = (url: string) => {
  const [messages, setMessages] = useState<any[]>([]);
  const [lastMessage, setLastMessage] = useState<any>(null);
  const [readyState, setReadyState] = useState<number>(WebSocket.CONNECTING);
  const [socket, setSocket] = useState<WebSocket | null>(null);

  useEffect(() => {
    const ws = new WebSocket(url);
    setSocket(ws);

    ws.onopen = () => setReadyState(WebSocket.OPEN);
    ws.onclose = () => setReadyState(WebSocket.CLOSED);
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setMessages((prev) => [...prev, data]);
      setLastMessage(data);
    };

    return () => {
      ws.close();
    };
  }, [url]);

  const sendMessage = useCallback((message: any) => {
    if (socket && readyState === WebSocket.OPEN) {
      socket.send(JSON.stringify(message));
    }
  }, [socket, readyState]);

  return { messages, lastMessage, readyState, sendMessage };
};
