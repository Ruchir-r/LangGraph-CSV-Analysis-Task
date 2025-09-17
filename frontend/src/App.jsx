import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { CssBaseline, Box, AppBar, Toolbar, Typography, Container } from '@mui/material';
import { styled } from '@mui/material/styles';

// Import components
import FileUploadPage from './components/FileUploadPage';
import ChatInterface from './components/ChatInterface';
import AnalysisResults from './components/AnalysisResults';
import Navigation from './components/Navigation';
import StatusIndicator from './components/StatusIndicator';

// Theme configuration for the app
const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
    background: {
      default: '#f5f5f5',
    },
  },
  typography: {
    fontFamily: 'Roboto, Arial, sans-serif',
    h4: {
      fontWeight: 600,
    },
    h5: {
      fontWeight: 500,
    },
  },
  components: {
    MuiAppBar: {
      styleOverrides: {
        root: {
          background: 'linear-gradient(135deg, #1976d2 0%, #1565c0 100%)',
        },
      },
    },
  },
});

const StyledContainer = styled(Container)(({ theme }) => ({
  marginTop: theme.spacing(3),
  marginBottom: theme.spacing(3),
}));

function App() {
  const [files, setFiles] = useState([]);
  const [analysisResults, setAnalysisResults] = useState(null);
  const [sessionId, setSessionId] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  useEffect(() => {
    // Generate session ID on app start
    setSessionId(generateSessionId());
  }, []);

  const generateSessionId = () => {
    return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
  };

  const handleFilesUploaded = (uploadedFiles, isReplacement = false) => {
    console.log('Files uploaded:', uploadedFiles, 'isReplacement:', isReplacement); // Debug log
    
    if (isReplacement) {
      // Replace the entire files array (used for file removal)
      setFiles(Array.isArray(uploadedFiles) ? uploadedFiles : [uploadedFiles]);
    } else {
      // Add new files to existing array (used for file upload)
      if (Array.isArray(uploadedFiles)) {
        setFiles(prev => [...prev, ...uploadedFiles]);
      } else {
        setFiles(prev => [...prev, uploadedFiles]);
      }
    }
  };

  const handleAnalysisStart = () => {
    setIsAnalyzing(true);
  };

  const handleAnalysisComplete = (results) => {
    setAnalysisResults(results);
    setIsAnalyzing(false);
  };

  const handleAnalysisError = (error) => {
    console.error('Analysis error:', error);
    setIsAnalyzing(false);
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Box sx={{ flexGrow: 1 }}>
          <AppBar position="static">
            <Toolbar>
              <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
                Historical Multi-Table Data Analysis
              </Typography>
              <Typography variant="subtitle2" sx={{ mr: 2 }}>
                Version 2.0 - Enhanced
              </Typography>
              <StatusIndicator isAnalyzing={isAnalyzing} filesCount={files.length} />
            </Toolbar>
          </AppBar>

          <Navigation 
            filesCount={files.length}
            isAnalyzing={isAnalyzing}
            activeAnalysisCount={analysisResults ? 1 : 0}
          />

          <StyledContainer maxWidth="xl">
            <Routes>
              <Route 
                path="/" 
                element={<Navigate to="/upload" replace />} 
              />
              <Route 
                path="/upload" 
                element={
                  <FileUploadPage 
                    files={files}
                    onFilesUploaded={handleFilesUploaded}
                  />
                } 
              />
              <Route 
                path="/chat" 
                element={
                  <ChatInterface
                    files={files}
                    sessionId={sessionId}
                    onAnalysisStart={handleAnalysisStart}
                    onAnalysisComplete={handleAnalysisComplete}
                    onAnalysisError={handleAnalysisError}
                    isAnalyzing={isAnalyzing}
                  />
                } 
              />
              <Route 
                path="/results" 
                element={
                  <AnalysisResults 
                    results={analysisResults}
                    files={files}
                    sessionId={sessionId}
                  />
                } 
              />
            </Routes>
          </StyledContainer>
        </Box>
      </Router>
    </ThemeProvider>
  );
}

export default App;