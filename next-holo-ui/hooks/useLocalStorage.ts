import { useEffect, useState } from "react";

// Generic version that supports any type
export function useLocalStorage<T>(key: string, defaultValue: T): [T, (value: T | ((prev: T) => T)) => void, boolean] {
  const [value, setValue] = useState<T>(defaultValue);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    try {
      const stored = typeof window !== "undefined" ? window.localStorage.getItem(key) : null;
      if (stored !== null) {
        try {
          const parsed = JSON.parse(stored);
          setValue(parsed);
        } catch {
          // If parsing fails, treat as string (backward compatibility)
          setValue(stored as unknown as T);
        }
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
      const serialized = typeof value === "string" ? value : JSON.stringify(value);
      window.localStorage.setItem(key, serialized);
    } catch {
      // ignore
    }
  }, [key, ready, value]);

  const setStoredValue = (newValue: T | ((prev: T) => T)) => {
    setValue((prev) => {
      const next = typeof newValue === "function" ? (newValue as (prev: T) => T)(prev) : newValue;
      return next;
    });
  };

  return [value, setStoredValue, ready] as const;
}

