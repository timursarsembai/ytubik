import React, { useState } from 'react';
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
  Pagination
} from '@mui/material';
import { Download, Refresh } from '@mui/icons-material';
import { useQuery } from 'react-query';
import { getDownloadsHistory } from '../services/api';

const DownloadHistory: React.FC = () => {
  const [page, setPage] = useState(1);
  const perPage = 10;

  const { data, isLoading, error, refetch } = useQuery(
    ['downloads', page],
    () => getDownloadsHistory(page, perPage),
    {
      refetchInterval: 5000, // Обновляем каждые 5 секунд
    }
  );

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
        return 'Истекло';
      default:
        return status;
    }
  };

  const formatFileSize = (sizeInMB: number) => {
    if (sizeInMB < 1) {
      return `${(sizeInMB * 1024).toFixed(1)} KB`;
    }
    return `${sizeInMB.toFixed(1)} MB`;
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('ru-RU');
  };

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" p={3}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error">
        Ошибка загрузки истории: {(error as any)?.message}
      </Alert>
    );
  }

  const totalPages = Math.ceil((data?.total || 0) / perPage);

  return (
    <Paper elevation={3} sx={{ p: 3 }}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="h5">
          История загрузок
        </Typography>
        <Button
          startIcon={<Refresh />}
          onClick={() => refetch()}
          variant="outlined"
        >
          Обновить
        </Button>
      </Box>

      {!data?.downloads?.length ? (
        <Alert severity="info">
          История загрузок пуста
        </Alert>
      ) : (
        <>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Название</TableCell>
                  <TableCell>Статус</TableCell>
                  <TableCell>Размер</TableCell>
                  <TableCell>Дата</TableCell>
                  <TableCell>Действия</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {data.downloads.map((download: any) => (
                  <TableRow key={download.id}>
                    <TableCell>
                      <Typography variant="body2" noWrap sx={{ maxWidth: 300 }}>
                        {download.video_info?.title || 'Неизвестно'}
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
                      {download.file_size ? formatFileSize(download.file_size) : '—'}
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">
                        {formatDate(download.created_at)}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      {download.status === 'completed' && download.id && (
                        <Button
                          size="small"
                          startIcon={<Download />}
                          href={`http://localhost:8000/api/download/${download.id}/file`}
                          download
                          variant="contained"
                        >
                          Скачать
                        </Button>
                      )}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>

          {totalPages > 1 && (
            <Box display="flex" justifyContent="center" mt={3}>
              <Pagination
                count={totalPages}
                page={page}
                onChange={(_, newPage) => setPage(newPage)}
                color="primary"
              />
            </Box>
          )}
        </>
      )}
    </Paper>
  );
};

export default DownloadHistory;
