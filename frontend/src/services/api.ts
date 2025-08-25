import axios from 'axios';

// Используем относительный путь по умолчанию, чтобы работать за reverse proxy
const API_BASE_URL = process.env.REACT_APP_API_URL || '';

const api = axios.create({
  baseURL: `${API_BASE_URL}/api`,
  timeout: 30000,
  withCredentials: true, // Включаем поддержку cookies
});

// Типы данных
export interface DownloadRequest {
  url: string;
  format: string;
  quality: string;
  audio_only: boolean;
}

export interface VideoInfo {
  video_id: string;
  title: string;
  description?: string;
  duration?: number;
  thumbnail?: string;
  channel_name?: string;
  view_count?: number;
  available_formats: any[];
}

export interface DownloadResponse {
  id: string;
  status: string;
  video_info?: VideoInfo;
  download_url?: string;
  error_message?: string;
  created_at: string;
}

export interface DownloadHistory {
  downloads: DownloadResponse[];
  total: number;
  page: number;
  per_page: number;
}

// API функции
export const createDownload = async (request: DownloadRequest): Promise<DownloadResponse> => {
  const response = await api.post('/download', request);
  return response.data;
};

export const getDownloadStatus = async (downloadId: string) => {
  const response = await api.get(`/download/${downloadId}/status`);
  return response.data;
};

export const getDownloadsHistory = async (page: number = 1, perPage: number = 20): Promise<DownloadHistory> => {
  const response = await api.get(`/downloads?page=${page}&per_page=${perPage}`);
  return response.data;
};

export const getVideoInfo = async (url: string): Promise<VideoInfo> => {
  const response = await api.post('/video/info', { url });
  return response.data;
};

export default api;
