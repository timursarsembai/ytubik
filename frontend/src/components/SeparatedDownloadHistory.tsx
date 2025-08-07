import React, { useState, useEffect } from 'react';
import {
  Paper,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  Button,
  Box,
  CircularProgress,
  Alert,
  Pagination,
  Grid
} from '@mui/material';
import { Refresh, GetApp } from '@mui/icons-material';
import { useQuery } from 'react-query';

interface GlobalActivity {
  video_title: string;
  created_at: string;
}

interface GlobalActivityResponse {
  activity: GlobalActivity[];
  total: number;
  page: number;
  per_page: number;
}

interface UserDownload {
  id: string;
  status: string;
  video_info?: {
    title: string;
    duration?: number;
    thumbnail?: string;
  };
  download_url?: string;
  error_message?: string;
  created_at: string;
}

interface MyDownloadsResponse {
  downloads: UserDownload[];
  total: number;
  page: number;
  per_page: number;
}

const SeparatedDownloadHistory: React.FC = () => {
  const [globalPage, setGlobalPage] = useState(1);
  const [myPage, setMyPage] = useState(1);
  const perPage = 10;

  // Глобальная активность
  const { 
    data: globalData, 
    isLoading: globalLoading, 
    error: globalError, 
    refetch: refetchGlobal 
  } = useQuery<GlobalActivityResponse, Error>(
    ['global-activity', globalPage],
    async () => {
      const response = await fetch(`/api/downloads/global?page=${globalPage}&per_page=${perPage}`);
      if (!response.ok) throw new Error('Failed to fetch global activity');
      return response.json();
    },
    {
      refetchInterval: 10000, // Обновляем каждые 10 секунд
    }
  );

  // Мои загрузки
  const { 
    data: myData, 
    isLoading: myLoading, 
    error: myError, 
    refetch: refetchMy 
  } = useQuery<MyDownloadsResponse, Error>(
    ['my-downloads', myPage],
    async () => {
      const response = await fetch(`/api/downloads/my?page=${myPage}&per_page=${perPage}`);
      if (!response.ok) throw new Error('Failed to fetch my downloads');
      return response.json();
    },
    {
      refetchInterval: 5000, // Обновляем каждые 5 секунд
    }
  );

  // Автоматическая очистка при закрытии браузера/вкладки
  useEffect(() => {
    const handleBeforeUnload = async (event: BeforeUnloadEvent) => {
      try {
        // Используем fetch для основной попытки
        await fetch('/api/downloads/cleanup-user', {
          method: 'DELETE',
          headers: {
            'Content-Type': 'application/json',
          },
        });
      } catch (error) {
        console.error('Error cleaning up downloads on beforeunload:', error);
      }
    };

    const handleVisibilityChange = () => {
      if (document.visibilityState === 'hidden') {
        // Используем sendBeacon как надежный способ для мобильных устройств
        try {
          const success = navigator.sendBeacon('/api/downloads/cleanup-user', '');
          if (!success) {
            // Fallback если sendBeacon не сработал
            fetch('/api/downloads/cleanup-user', {
              method: 'DELETE',
              keepalive: true
            }).catch(err => console.error('Cleanup fallback failed:', err));
          }
        } catch (error) {
          console.error('Error cleaning up downloads on visibility change:', error);
        }
      }
    };

    const handleUnload = () => {
      // Последняя попытка через sendBeacon
      navigator.sendBeacon('/api/downloads/cleanup-user', JSON.stringify({}));
    };

    // Добавляем обработчики событий
    window.addEventListener('beforeunload', handleBeforeUnload);
    window.addEventListener('unload', handleUnload);
    document.addEventListener('visibilitychange', handleVisibilityChange);

    // Очистка обработчиков при размонтировании компонента
    return () => {
      window.removeEventListener('beforeunload', handleBeforeUnload);
      window.removeEventListener('unload', handleUnload);
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  }, []);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'success';
      case 'processing':
        return 'warning';
      case 'failed':
        return 'error';
      case 'pending':
        return 'info';
      case 'expired':
        return 'default';
      default:
        return 'default';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'completed':
        return 'Завершено';
      case 'processing':
        return 'Обработка';
      case 'failed':
        return 'Ошибка';
      case 'pending':
        return 'Ожидание';
      case 'expired':
        return 'Срок истёк';
      default:
        return status;
    }
  };

  const handleManualCleanup = async () => {
    try {
      const response = await fetch('/api/downloads/cleanup', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      if (response.ok) {
        const result = await response.json();
        alert(`Очищено ${result.cleaned_count} файлов`);
        refetchMy(); // Обновляем список
      }
    } catch (error) {
      console.error('Error cleaning up downloads:', error);
      alert('Ошибка при очистке файлов');
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('ru-RU');
  };

  const handleDownload = async (url: string, filename?: string) => {
    try {
      // Используем полный URL для избежания проблем с роутингом
      const fullUrl = url.startsWith('http') ? url : `http://localhost:8000${url}`;
      
      // Используем fetch для получения файла
      const response = await fetch(fullUrl);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      // Получаем blob
      const blob = await response.blob();
      
      // Получаем имя файла из заголовков
      let downloadFilename = filename;
      const contentDisposition = response.headers.get('content-disposition');
      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename\*=UTF-8''(.+)/);
        if (filenameMatch) {
          downloadFilename = decodeURIComponent(filenameMatch[1]);
        }
      }
      
      // Создаем URL для blob и скачиваем
      const blobUrl = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = blobUrl;
      link.download = downloadFilename || 'download';
      link.style.display = 'none';
      
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      // Освобождаем память
      window.URL.revokeObjectURL(blobUrl);
      
    } catch (error) {
      console.error('Ошибка при скачивании:', error);
      alert('Ошибка при скачивании файла');
    }
  };

  return (
    <Box sx={{ mt: 4 }}>
      <Grid container spacing={4}>
        {/* Мои загрузки */}
        <Grid item xs={12} md={12}>
          <Paper sx={{ p: 3 }}>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
              <Typography variant="h6" component="h2">
                📁 Мои загрузки
              </Typography>
              <Box display="flex" gap={1}>
                <Button
                  startIcon={<Refresh />}
                  onClick={() => refetchMy()}
                  disabled={myLoading}
                  size="small"
                >
                  Обновить
                </Button>
                <Button
                  onClick={handleManualCleanup}
                  disabled={myLoading}
                  size="small"
                  color="warning"
                  variant="outlined"
                >
                  Очистить файлы
                </Button>
              </Box>
            </Box>

            {myError && (
              <Alert severity="error" sx={{ mb: 2 }}>
                Ошибка загрузки ваших файлов
              </Alert>
            )}

            {myLoading ? (
              <Box display="flex" justifyContent="center" p={3}>
                <CircularProgress />
              </Box>
            ) : (
              <>
                <TableContainer>
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell>Название</TableCell>
                        <TableCell>Статус</TableCell>
                        <TableCell>Дата</TableCell>
                        <TableCell>Действия</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {myData?.downloads.map((download) => (
                        <TableRow key={download.id}>
                          <TableCell>
                            <Typography variant="body2" noWrap>
                              {download.video_info?.title || 'Обработка...'}
                            </Typography>
                          </TableCell>
                          <TableCell>
                            <Chip
                              label={getStatusText(download.status)}
                              color={getStatusColor(download.status) as any}
                              size="small"
                            />
                          </TableCell>
                          <TableCell>
                            <Typography variant="body2" color="text.secondary">
                              {formatDate(download.created_at)}
                            </Typography>
                          </TableCell>
                          <TableCell>
                            {download.status === 'completed' && download.download_url ? (
                              <Button
                                size="small"
                                startIcon={<GetApp />}
                                onClick={() => handleDownload(
                                  download.download_url!, 
                                  download.video_info?.title ? `${download.video_info.title}.mp4` : undefined
                                )}
                                variant="outlined"
                                color="primary"
                              >
                                Скачать
                              </Button>
                            ) : download.status === 'failed' ? (
                              <Typography variant="body2" color="error">
                                {download.error_message || 'Ошибка'}
                              </Typography>
                            ) : download.status === 'expired' ? (
                              <Typography variant="body2" color="text.secondary">
                                Файл удалён
                              </Typography>
                            ) : download.status === 'processing' ? (
                              <Box display="flex" alignItems="center" gap={1}>
                                <CircularProgress size={16} />
                                <Typography variant="body2" color="text.secondary">
                                  Обработка...
                                </Typography>
                              </Box>
                            ) : download.status === 'pending' ? (
                              <Typography variant="body2" color="text.secondary">
                                В очереди
                              </Typography>
                            ) : (
                              <CircularProgress size={20} />
                            )}
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>

                {myData && myData.total > perPage && (
                  <Box display="flex" justifyContent="center" mt={2}>
                    <Pagination
                      count={Math.ceil(myData.total / perPage)}
                      page={myPage}
                      onChange={(_, newPage) => setMyPage(newPage)}
                      color="primary"
                    />
                  </Box>
                )}
              </>
            )}
          </Paper>
        </Grid>

        {/* Глобальная активность */}
        <Grid item xs={12} md={12}>
          <Paper sx={{ p: 3 }}>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
              <Typography variant="h6" component="h2">
                🌍 Глобальная активность
              </Typography>
              <Button
                startIcon={<Refresh />}
                onClick={() => refetchGlobal()}
                disabled={globalLoading}
              >
                Обновить
              </Button>
            </Box>

            {globalError && (
              <Alert severity="error" sx={{ mb: 2 }}>
                Ошибка загрузки глобальной активности
              </Alert>
            )}

            {globalLoading ? (
              <Box display="flex" justifyContent="center" p={3}>
                <CircularProgress />
              </Box>
            ) : (
              <>
                <TableContainer>
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell>Название видео</TableCell>
                        <TableCell>Дата запроса</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {globalData?.activity.map((item, index) => (
                        <TableRow key={index}>
                          <TableCell>
                            <Typography variant="body2" noWrap>
                              {item.video_title}
                            </Typography>
                          </TableCell>
                          <TableCell>
                            <Typography variant="body2" color="text.secondary">
                              {formatDate(item.created_at)}
                            </Typography>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>

                {globalData && globalData.total > perPage && (
                  <Box display="flex" justifyContent="center" mt={2}>
                    <Pagination
                      count={Math.ceil(globalData.total / perPage)}
                      page={globalPage}
                      onChange={(_, newPage) => setGlobalPage(newPage)}
                      color="primary"
                    />
                  </Box>
                )}
              </>
            )}
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default SeparatedDownloadHistory;
