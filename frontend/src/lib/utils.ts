import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatBytes(bytes: number, decimals = 2) {
  if (bytes === 0) return "0 Bytes";
  const k = 1024;
  const dm = decimals < 0 ? 0 : decimals;
  const sizes = ["Bytes", "KB", "MB", "GB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + " " + sizes[i];
}

export function formatDate(dateString: string) {
  const d = new Date(dateString);
  return d.toLocaleString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function parseApiError(err: any, fallback: string): string {
  if (err.response?.data?.detail) {
    if (typeof err.response.data.detail === "string") return err.response.data.detail;
    if (Array.isArray(err.response.data.detail)) {
      return err.response.data.detail.map((d: any) => d.msg || JSON.stringify(d)).join(", ");
    }
  }
  if (err.message && err.message !== "Network Error") return err.message;
  return `${fallback} (Backend service may be starting up, please allow 15-30s and try again)`;
}

