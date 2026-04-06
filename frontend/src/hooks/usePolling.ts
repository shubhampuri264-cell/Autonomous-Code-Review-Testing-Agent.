import { useEffect, useRef } from "react";

export default function usePolling(
  callback: () => void,
  intervalMs: number,
  enabled: boolean
) {
  const savedCallback = useRef(callback);

  useEffect(() => {
    savedCallback.current = callback;
  }, [callback]);

  useEffect(() => {
    if (!enabled) return;

    const tick = () => savedCallback.current();
    const id = setInterval(tick, intervalMs);

    return () => clearInterval(id);
  }, [intervalMs, enabled]);
}
