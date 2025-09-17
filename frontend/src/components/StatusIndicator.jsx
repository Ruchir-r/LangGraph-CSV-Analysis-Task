/**
 * StatusIndicator Component
 * Real-time status display for V2 multi-temporal analysis system
 * 
 * Features:
 * - System health monitoring
 * - Analysis progress tracking  
 * - File upload status
 * - WebSocket connection status
 * - LangGraph workflow status
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Chip,
  Tooltip,
  CircularProgress,
  Badge,
  Popover,
  Typography,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider,
  LinearProgress
} from '@mui/material';
import {
  CheckCircle as HealthyIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
  CloudUpload as FilesIcon,
  Psychology as AIIcon,
  Speed as PerformanceIcon,
  Wifi as ConnectionIcon,
  Timeline as AnalysisIcon
} from '@mui/icons-material';

const StatusIndicator = ({ 
  isAnalyzing = false, 
  filesCount = 0,
  systemHealth = {},
  analysisProgress = null,
  websocketConnected = false,
  backgroundTasks = {}
}) => {
  const [anchorEl, setAnchorEl] = useState(null);
  const [systemStatus, setSystemStatus] = useState('healthy');

  useEffect(() => {
    // Determine overall system status
    if (systemHealth.database === 'error' || systemHealth.langgraph === 'error') {
      setSystemStatus('error');
    } else if (systemHealth.database === 'warning' || !websocketConnected) {
      setSystemStatus('warning');
    } else {
      setSystemStatus('healthy');
    }
  }, [systemHealth, websocketConnected]);

  const handleClick = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const getStatusIcon = () => {
    switch (systemStatus) {
      case 'healthy':
        return <HealthyIcon color="success" />;
      case 'warning':
        return <WarningIcon color="warning" />;
      case 'error':
        return <ErrorIcon color="error" />;
      default:
        return <HealthyIcon color="success" />;
    }
  };

  const getStatusColor = () => {
    switch (systemStatus) {
      case 'healthy':
        return 'success';
      case 'warning':
        return 'warning';
      case 'error':
        return 'error';
      default:
        return 'success';
    }
  };

  const getConnectionStatus = () => {
    if (websocketConnected) {
      return { label: 'Connected', color: 'success', icon: <ConnectionIcon /> };
    } else {
      return { label: 'Disconnected', color: 'error', icon: <ConnectionIcon /> };
    }
  };

  const getTotalBackgroundTasks = () => {
    return Object.values(backgroundTasks).reduce((sum, count) => sum + count, 0);
  };

  const open = Boolean(anchorEl);

  return (
    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
      {/* Main Status Indicator */}
      <Tooltip title="Click for detailed system status">
        <Chip
          icon={getStatusIcon()}
          label={`${systemStatus.charAt(0).toUpperCase() + systemStatus.slice(1)}`}
          color={getStatusColor()}
          variant="outlined"
          size="small"
          onClick={handleClick}
          sx={{ 
            cursor: 'pointer',
            '&:hover': { 
              bgcolor: `${getStatusColor()}.50` 
            }
          }}
        />
      </Tooltip>

      {/* Files Count */}
      <Chip
        icon={<FilesIcon />}
        label={`${filesCount} files`}
        color="primary"
        variant="outlined"
        size="small"
      />

      {/* Analysis Progress */}
      {isAnalyzing && analysisProgress && (
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
          <CircularProgress size={16} thickness={4} />
          <Chip
            label={`${Math.round(analysisProgress.progress_percentage)}%`}
            color="secondary"
            variant="filled"
            size="small"
          />
        </Box>
      )}

      {/* Background Tasks */}
      {getTotalBackgroundTasks() > 0 && (
        <Badge badgeContent={getTotalBackgroundTasks()} color="info">
          <Chip
            icon={<AnalysisIcon />}
            label="Tasks"
            color="info"
            variant="outlined"
            size="small"
          />
        </Badge>
      )}

      {/* Detailed Status Popover */}
      <Popover
        open={open}
        anchorEl={anchorEl}
        onClose={handleClose}
        anchorOrigin={{
          vertical: 'bottom',
          horizontal: 'right',
        }}
        transformOrigin={{
          vertical: 'top',
          horizontal: 'right',
        }}
        PaperProps={{
          sx: { 
            minWidth: 320, 
            maxWidth: 400,
            p: 1
          }
        }}
      >
        <Typography variant="h6" sx={{ p: 1, pb: 0 }}>
          System Status
        </Typography>

        <List dense>
          {/* Overall Health */}
          <ListItem>
            <ListItemIcon>
              {getStatusIcon()}
            </ListItemIcon>
            <ListItemText 
              primary="System Health"
              secondary={`Overall status: ${systemStatus}`}
            />
          </ListItem>

          <Divider />

          {/* Database Status */}
          <ListItem>
            <ListItemIcon>
              <HealthyIcon color={systemHealth.database === 'connected' ? 'success' : 'error'} />
            </ListItemIcon>
            <ListItemText 
              primary="Database"
              secondary={systemHealth.database || 'Unknown'}
            />
          </ListItem>

          {/* LangGraph Status */}
          <ListItem>
            <ListItemIcon>
              <AIIcon color={systemHealth.langgraph === 'operational' ? 'success' : 'warning'} />
            </ListItemIcon>
            <ListItemText 
              primary="LangGraph Workflow"
              secondary={systemHealth.langgraph || 'Unknown'}
            />
          </ListItem>

          {/* WebSocket Connection */}
          <ListItem>
            <ListItemIcon>
              <ConnectionIcon color={websocketConnected ? 'success' : 'error'} />
            </ListItemIcon>
            <ListItemText 
              primary="Real-time Updates"
              secondary={websocketConnected ? 'Connected' : 'Disconnected'}
            />
          </ListItem>

          {/* Files Status */}
          <ListItem>
            <ListItemIcon>
              <FilesIcon color="primary" />
            </ListItemIcon>
            <ListItemText 
              primary="Data Files"
              secondary={`${filesCount} files available for analysis`}
            />
          </ListItem>

          {/* Background Tasks */}
          {Object.keys(backgroundTasks).length > 0 && (
            <>
              <Divider />
              <ListItem>
                <ListItemIcon>
                  <PerformanceIcon color="info" />
                </ListItemIcon>
                <ListItemText 
                  primary="Background Tasks"
                  secondary={
                    <Box>
                      {Object.entries(backgroundTasks).map(([status, count]) => (
                        <Typography key={status} variant="caption" display="block">
                          {status}: {count}
                        </Typography>
                      ))}
                    </Box>
                  }
                />
              </ListItem>
            </>
          )}

          {/* Current Analysis Progress */}
          {isAnalyzing && analysisProgress && (
            <>
              <Divider />
              <ListItem>
                <ListItemIcon>
                  <CircularProgress size={20} thickness={4} />
                </ListItemIcon>
                <ListItemText 
                  primary="Current Analysis"
                  secondary={
                    <Box>
                      <Typography variant="body2">
                        {analysisProgress.status_message}
                      </Typography>
                      <LinearProgress 
                        variant="determinate" 
                        value={analysisProgress.progress_percentage}
                        sx={{ mt: 1, mb: 0.5 }}
                      />
                      <Typography variant="caption">
                        {Math.round(analysisProgress.progress_percentage)}% complete
                      </Typography>
                      {analysisProgress.current_node && (
                        <Typography variant="caption" display="block">
                          Current: {analysisProgress.current_node}
                        </Typography>
                      )}
                    </Box>
                  }
                />
              </ListItem>
            </>
          )}
        </List>

        <Typography variant="caption" color="text.secondary" sx={{ p: 1, display: 'block' }}>
          Version 2.0.0 Enhanced • Last updated: {new Date().toLocaleTimeString()}
        </Typography>
      </Popover>
    </Box>
  );
};

export default StatusIndicator;