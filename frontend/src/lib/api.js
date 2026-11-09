import axios from "axios";
import { useMemo } from "react";
import { useAuth } from "@clerk/react";
import { useQuery } from "@tanstack/react-query";

export const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
export const API = `${BACKEND_URL}/api`;
export const publicApi = axios.create({ baseURL: API });

export const fileUrl = (path) => (path ? `${BACKEND_URL}${path}` : null);

export function useApi() {
  const { getToken } = useAuth();
  return useMemo(() => {
    const client = axios.create({ baseURL: API });
    client.interceptors.request.use(async (cfg) => {
      const token = await getToken();
      if (token) cfg.headers.Authorization = `Bearer ${token}`;
      return cfg;
    });
    return client;
  }, [getToken]);
}

export function errMsg(e, fallback = "Something went wrong") {
  const d = e?.response?.data?.detail;
  if (typeof d === "string") return d;
  if (Array.isArray(d)) return d.map((x) => x.msg).join(", ");
  return e?.message || fallback;
}

export const formatINR = (paise) => `₹${(paise / 100).toLocaleString("en-IN")}`;
export const formatBytes = (b) => (b > 1048576 ? `${(b / 1048576).toFixed(1)} MB` : `${Math.round(b / 1024)} KB`);
export const formatDate = (iso) =>
  iso ? new Date(iso).toLocaleString("en-IN", { day: "numeric", month: "short", hour: "2-digit", minute: "2-digit" }) : "";

export function useCatalog() {
  return useQuery({ queryKey: ["catalog"], queryFn: () => publicApi.get("/catalog").then((r) => r.data), staleTime: Infinity });
}

export function useMe() {
  const api = useApi();
  return useQuery({ queryKey: ["me"], queryFn: () => api.get("/me").then((r) => r.data) });
}

export const labelOf = (list, id) => list?.find((o) => o.id === id)?.label || id;
