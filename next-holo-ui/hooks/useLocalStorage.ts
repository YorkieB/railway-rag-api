import { useEffect, useState } from "react";

export function useLocalStorage(key: string, defaultValue: string) {
  const [value, setValue] = useState<string>(defaultValue);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    try {
      const stored = typeof window !== "undefined" ? window.localStorage.getItem(key) : null;
      if (stored !== null) {
        setValue(stored);
      }
    } catch {
      // ignore
    } finally {
      setReady(true);
    }
  }, [key]);

  useEffect(() => {
    if (!ready) return;
    try {
      window.localStorage.setItem(key, value);
    } catch {
      // ignore
    }
  }, [key, ready, value]);

  return [value, setValue, ready] as const;
}

