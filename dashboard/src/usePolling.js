import { useState, useEffect } from "react";
import axios from "axios";

const API_BASE = "http://localhost:8000";

export function usePolling(endpoint, intervalMs = 2000) {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    let isMounted = true;

    const fetchData = async () => {
      try {
        const response = await axios.get(`${API_BASE}${endpoint}`);
        if (isMounted) {
          setData(response.data);
          setError(null);
        }
      } catch (err) {
        if (isMounted) {
          setError(err.message);
        }
      }
    };

    fetchData(); // fetch immediately on mount, don't wait for the first interval
    const intervalId = setInterval(fetchData, intervalMs);

    return () => {
      isMounted = false;
      clearInterval(intervalId);
    };
  }, [endpoint, intervalMs]);

  return { data, error };
}