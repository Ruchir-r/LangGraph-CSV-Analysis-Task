/**
 * Navigation Component
 * Enhanced navigation for V2 multi-temporal analysis system
 * 
 * Features:
 * - Material-UI based navigation tabs
 * - Active route highlighting
 * - Progress indicators for ongoing analyses
 * - Responsive design
 */

import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  Tabs,
  Tab,
  Box,
  Badge,
  Tooltip,
  useTheme,
  useMediaQuery
} from '@mui/material';
import {
  CloudUpload as UploadIcon,
  Chat as ChatIcon,
  Analytics as ResultsIcon,
  Assessment as AnalysisIcon
} from '@mui/icons-material';

const Navigation = ({ 
  filesCount = 0, 
  isAnalyzing = false, 
  activeAnalysisCount = 0 
}) => {
  const navigate = useNavigate();
  const location = useLocation();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  // Determine current tab based on pathname
  const getCurrentTab = () => {
    const path = location.pathname;
    if (path.startsWith('/upload')) return 0;
    if (path.startsWith('/chat')) return 1;
    if (path.startsWith('/results')) return 2;
    return 0; // default to upload
  };

  const handleTabChange = (event, newValue) => {
    const routes = ['/upload', '/chat', '/results'];
    navigate(routes[newValue]);
  };

  return (
    <Box 
      sx={{ 
        borderBottom: 1, 
        borderColor: 'divider',
        bgcolor: 'background.paper',
        position: 'sticky',
        top: 64, // Below AppBar
        zIndex: 100,
        px: { xs: 1, md: 3 },
        py: 1
      }}
    >
      <Tabs 
        value={getCurrentTab()} 
        onChange={handleTabChange}
        variant={isMobile ? "fullWidth" : "standard"}
        textColor="primary"
        indicatorColor="primary"
        sx={{
          '& .MuiTab-root': {
            minHeight: 60,
            fontSize: '0.9rem',
            fontWeight: 500,
            textTransform: 'none',
            '&.Mui-selected': {
              color: 'primary.main',
              fontWeight: 600,
            }
          }
        }}
      >
        <Tab 
          icon={
            <Badge 
              badgeContent={filesCount} 
              color="primary" 
              sx={{ '& .MuiBadge-badge': { fontSize: '0.7rem' } }}
            >
              <UploadIcon />
            </Badge>
          } 
          label={isMobile ? "Upload" : "File Upload"} 
          iconPosition="start"
          sx={{ 
            minWidth: { xs: 'auto', md: 140 },
            px: { xs: 1, md: 2 }
          }}
        />
        
        <Tab 
          icon={
            <Badge 
              variant="dot" 
              color="secondary" 
              invisible={!isAnalyzing}
              sx={{ 
                '& .MuiBadge-dot': { 
                  animation: isAnalyzing ? 'pulse 1.5s ease-in-out infinite' : 'none',
                  '@keyframes pulse': {
                    '0%': { opacity: 1, transform: 'scale(1)' },
                    '50%': { opacity: 0.5, transform: 'scale(1.2)' },
                    '100%': { opacity: 1, transform: 'scale(1)' }
                  }
                }
              }}
            >
              <ChatIcon />
            </Badge>
          } 
          label={isMobile ? "Chat" : "AI Assistant"} 
          iconPosition="start"
          disabled={filesCount === 0}
          sx={{ 
            minWidth: { xs: 'auto', md: 140 },
            px: { xs: 1, md: 2 }
          }}
        />
        
        <Tab 
          icon={
            <Badge 
              badgeContent={activeAnalysisCount > 0 ? activeAnalysisCount : null} 
              color="error"
              sx={{ '& .MuiBadge-badge': { fontSize: '0.7rem' } }}
            >
              <ResultsIcon />
            </Badge>
          } 
          label={isMobile ? "Results" : "Analysis Results"} 
          iconPosition="start"
          disabled={filesCount === 0}
          sx={{ 
            minWidth: { xs: 'auto', md: 140 },
            px: { xs: 1, md: 2 }
          }}
        />
      </Tabs>

      {/* Progress indicator for active analysis */}
      {isAnalyzing && (
        <Box 
          sx={{ 
            position: 'absolute', 
            bottom: 0, 
            left: 0, 
            right: 0, 
            height: 2,
            bgcolor: 'primary.light',
            '&::before': {
              content: '""',
              position: 'absolute',
              top: 0,
              left: 0,
              height: '100%',
              bgcolor: 'primary.main',
              animation: 'loading 2s linear infinite',
              '@keyframes loading': {
                '0%': { width: '0%' },
                '50%': { width: '70%' },
                '100%': { width: '100%' }
              }
            }
          }}
        />
      )}

      {/* Helpful tooltips for disabled tabs */}
      {filesCount === 0 && (
        <Box sx={{ display: 'none' }}>
          <Tooltip title="Upload data files first to enable chat and analysis features" placement="bottom">
            <span />
          </Tooltip>
        </Box>
      )}
    </Box>
  );
};

export default Navigation;