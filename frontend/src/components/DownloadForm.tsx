import React, { useState } from 'react';
import {
  Paper,
  TextField,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  FormControlLabel,
  Switch,
  Box,
  Typography,
  Alert,
  CircularProgress
} from '@mui/material';
import { Download } from '@mui/icons-material';
import { useMutation } from 'react-query';
import { createDownload } from '../services/api';

const DownloadForm: React.FC = () => {
  const [url, setUrl] = useState('');
  const [format, setFormat] = useState('video_mp4');
  const [quality, setQuality] = useState('best');
  const [audioOnly, setAudioOnly] = useState(false);

  const mutation = useMutation(createDownload, {
    onSuccess: (data) => {
      setUrl('');
      // Здесь можно добавить уведомление о успешном создании загрузки
    },
    onError: (error: any) => {
      console.error('Ошибка создания загрузки:', error);
    }
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!url.trim()) {
      return;
    }

    mutation.mutate({
      url,
      format,
      quality,
      audio_only: audioOnly
    });
  };

  const isYouTubeUrl = (url: string) => {
    return url.includes('youtube.com') || url.includes('youtu.be');
  };

  return (
    <Paper elevation={3} sx={{ p: 3 }}>
      <Typography variant="h5" gutterBottom>
        Скачать видео с YouTube
      </Typography>
      
      <form onSubmit={handleSubmit}>
        <Box sx={{ mb: 3 }}>
          <TextField
            fullWidth
            label="YouTube URL"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="https://www.youtube.com/watch?v=..."
            error={url.length > 0 && !isYouTubeUrl(url)}
            helperText={url.length > 0 && !isYouTubeUrl(url) ? "Введите корректную YouTube ссылку" : ""}
            variant="outlined"
          />
        </Box>

        <Box sx={{ display: 'flex', gap: 2, mb: 3, flexWrap: 'wrap' }}>
          <FormControl sx={{ minWidth: 120 }}>
            <InputLabel>Формат</InputLabel>
            <Select
              value={format}
              label="Формат"
              onChange={(e) => setFormat(e.target.value)}
            >
              <MenuItem value="video_mp4">MP4 (Видео)</MenuItem>
              <MenuItem value="video_webm">WebM (Видео)</MenuItem>
              <MenuItem value="audio_mp3">MP3 (Аудио)</MenuItem>
              <MenuItem value="audio_aac">AAC (Аудио)</MenuItem>
            </Select>
          </FormControl>

          <FormControl sx={{ minWidth: 120 }}>
            <InputLabel>Качество</InputLabel>
            <Select
              value={quality}
              label="Качество"
              onChange={(e) => setQuality(e.target.value)}
              disabled={audioOnly}
            >
              <MenuItem value="best">Лучшее</MenuItem>
              <MenuItem value="1080p">1080p</MenuItem>
              <MenuItem value="720p">720p</MenuItem>
              <MenuItem value="480p">480p</MenuItem>
              <MenuItem value="360p">360p</MenuItem>
            </Select>
          </FormControl>

          <FormControlLabel
            control={
              <Switch
                checked={audioOnly}
                onChange={(e) => setAudioOnly(e.target.checked)}
              />
            }
            label="Только аудио"
          />
        </Box>

        {mutation.error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {(() => {
              const error = (mutation.error as any)?.response?.data?.detail;
              if (typeof error === 'string') {
                return error;
              } else if (typeof error === 'object' && error?.error) {
                // Обрабатываем объект rate limiting
                return `${error.error}. Часовой лимит: ${error.hourly_count}/${error.hourly_limit}, Дневной лимит: ${error.daily_count}/${error.daily_limit}`;
              } else {
                return 'Произошла ошибка';
              }
            })()}
          </Alert>
        )}

        {mutation.isSuccess && (
          <Alert severity="success" sx={{ mb: 2 }}>
            Загрузка успешно создана! Проверьте историю загрузок.
          </Alert>
        )}

        <Button
          type="submit"
          variant="contained"
          startIcon={mutation.isLoading ? <CircularProgress size={20} /> : <Download />}
          disabled={mutation.isLoading || !url.trim() || !isYouTubeUrl(url)}
          fullWidth
        >
          {mutation.isLoading ? 'Создание загрузки...' : 'Скачать'}
        </Button>
      </form>
    </Paper>
  );
};

export default DownloadForm;
