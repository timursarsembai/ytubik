import React from 'react';
import { Container, AppBar, Toolbar, Typography, Box } from '@mui/material';
import { VideoLibrary } from '@mui/icons-material';
import DownloadForm from './components/DownloadForm';
import DownloadHistory from './components/DownloadHistory';

function App() {
  return (
    <div className="App">
      <AppBar position="static">
        <Toolbar>
          <VideoLibrary sx={{ mr: 2 }} />
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            YouTube Video Downloader
          </Typography>
        </Toolbar>
      </AppBar>
      
      <Container maxWidth="md" sx={{ mt: 4, mb: 4 }}>
        <Box sx={{ mb: 4 }}>
          <DownloadForm />
        </Box>
        
        <Box>
          <DownloadHistory />
        </Box>
      </Container>
    </div>
  );
}

export default App;
