/**
 * FileUploadPage Component  
 * Enhanced file upload with V2 multi-temporal analysis capabilities
 * 
 * Features:
 * - Drag and drop multiple file upload
 * - File preview and schema detection
 * - Temporal alignment visualization
 * - Progress tracking and error handling
 * - Support for CSV, Excel files
 * - File validation and preprocessing
 */

import React, { useState, useCallback, useRef } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  LinearProgress,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Alert,
  AlertTitle,
  IconButton,
  Collapse,
  Grid,
  Tooltip,
  Divider,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemSecondaryAction
} from '@mui/material';
import {
  CloudUpload,
  InsertDriveFile,
  Delete as DeleteIcon,
  Visibility as PreviewIcon,
  CheckCircle as ValidIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
  ExpandMore as ExpandIcon,
  ExpandLess as CollapseIcon,
  Timeline as TimelineIcon,
  Assessment as AnalysisIcon
} from '@mui/icons-material';

import APIService from '../services/api';

const FileUploadPage = ({ files, onFilesUploaded }) => {
  const [uploadProgress, setUploadProgress] = useState({});
  const [uploadErrors, setUploadErrors] = useState({});
  const [isDragOver, setIsDragOver] = useState(false);
  const [expandedFiles, setExpandedFiles] = useState({});
  const [isUploading, setIsUploading] = useState(false);
  const fileInputRef = useRef(null);
  const apiService = new APIService();

  // Supported file types for V2
  const supportedTypes = ['text/csv', 'application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'];
  const maxFileSize = 100 * 1024 * 1024; // 100MB
  const maxFiles = 10; // Max files per session

  const handleDragOver = useCallback((event) => {
    event.preventDefault();
    setIsDragOver(true);
  }, []);

  const handleDragLeave = useCallback((event) => {
    event.preventDefault();
    setIsDragOver(false);
  }, []);

  const handleDrop = useCallback((event) => {
    event.preventDefault();
    setIsDragOver(false);
    
    const droppedFiles = Array.from(event.dataTransfer.files);
    handleFileSelection(droppedFiles);
  }, []);

  const handleFileInputChange = (event) => {
    const selectedFiles = Array.from(event.target.files);
    handleFileSelection(selectedFiles);
  };

  const validateFiles = (fileList) => {
    const errors = {};
    const validFiles = [];

    fileList.forEach((file, index) => {
      const fileErrors = [];

      // Check file type
      if (!supportedTypes.includes(file.type)) {
        fileErrors.push('Unsupported file type. Please use CSV or Excel files.');
      }

      // Check file size
      if (file.size > maxFileSize) {
        fileErrors.push('File size exceeds 100MB limit.');
      }

      // Check total files limit
      if (files.length + validFiles.length >= maxFiles) {
        fileErrors.push('Maximum 10 files allowed per session.');
      }

      if (fileErrors.length > 0) {
        errors[`temp_${index}`] = fileErrors;
      } else {
        validFiles.push(file);
      }
    });

    return { validFiles, errors };
  };

  const handleFileSelection = async (fileList) => {
    const { validFiles, errors } = validateFiles(fileList);
    
    if (Object.keys(errors).length > 0) {
      setUploadErrors(errors);
      return;
    }

    setIsUploading(true);
    setUploadErrors({});

    try {
      const uploadPromises = validFiles.map(async (file) => {
        const fileId = `temp_${Date.now()}_${Math.random()}`;
        
        setUploadProgress(prev => ({
          ...prev,
          [fileId]: { progress: 0, status: 'uploading' }
        }));

        try {
          // Upload file using V2 API
          const response = await apiService.uploadFile(file);
          
          setUploadProgress(prev => ({
            ...prev,
            [fileId]: { progress: 100, status: 'completed', response }
          }));

          return {
            ...response,
            id: response.file_id, // Ensure id property exists for compatibility
            originalFile: file,
            tempId: fileId
          };
        } catch (error) {
          console.error('File upload failed:', error);
          setUploadProgress(prev => ({
            ...prev,
            [fileId]: { progress: 0, status: 'error', error: error.message }
          }));
          
          setUploadErrors(prev => ({
            ...prev,
            [fileId]: [error.message]
          }));

          return null;
        }
      });

      const results = await Promise.all(uploadPromises);
      const successfulUploads = results.filter(result => result !== null);

      if (successfulUploads.length > 0) {
        onFilesUploaded(successfulUploads);
        // Show success message
        console.log(`Successfully uploaded ${successfulUploads.length} file(s)`);
      }

    } catch (error) {
      console.error('Upload process failed:', error);
    } finally {
      setIsUploading(false);
      // Clear progress after a delay
      setTimeout(() => {
        setUploadProgress({});
      }, 3000);
    }
  };

  const handleRemoveFile = async (fileId) => {
    try {
      // Remove file from backend (implement deletion API)
      // await apiService.deleteFile(fileId);
      
      const updatedFiles = files.filter(file => file.file_id !== fileId);
      // Call onFilesUploaded with the updated list to replace the current files
      onFilesUploaded(updatedFiles, true); // true indicates replacement
    } catch (error) {
      console.error('Failed to remove file:', error);
    }
  };

  const toggleFileExpansion = (fileId) => {
    setExpandedFiles(prev => ({
      ...prev,
      [fileId]: !prev[fileId]
    }));
  };

  const getFileTypeIcon = (filename) => {
    const extension = filename.split('.').pop().toLowerCase();
    return <InsertDriveFile color={extension === 'csv' ? 'primary' : 'secondary'} />;
  };

  const renderFilePreview = (file) => {
    if (!file.preview || !file.preview.length) return null;

    return (
      <TableContainer component={Paper} sx={{ mt: 2, maxHeight: 300 }}>
        <Table size="small">
          <TableHead>
            <TableRow>
              {Object.keys(file.preview[0] || {}).map(column => (
                <TableCell key={column} sx={{ fontWeight: 600 }}>
                  {column}
                </TableCell>
              ))}
            </TableRow>
          </TableHead>
          <TableBody>
            {file.preview.slice(0, 5).map((row, index) => (
              <TableRow key={index}>
                {Object.values(row).map((value, cellIndex) => (
                  <TableCell key={cellIndex}>
                    {value !== null && value !== undefined ? String(value) : '—'}
                  </TableCell>
                ))}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    );
  };

  const renderAnalysisInfo = (file) => {
    if (!file.analysis) return null;

    const { numeric_columns, categorical_columns, date_columns } = file.analysis;

    return (
      <Grid container spacing={2} sx={{ mt: 1 }}>
        <Grid item xs={12} md={4}>
          <Typography variant="subtitle2" gutterBottom>
            <AnalysisIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
            Numeric Columns ({numeric_columns?.length || 0})
          </Typography>
          <Box>
            {numeric_columns?.map(col => (
              <Chip key={col} label={col} size="small" color="primary" sx={{ m: 0.25 }} />
            ))}
          </Box>
        </Grid>
        
        <Grid item xs={12} md={4}>
          <Typography variant="subtitle2" gutterBottom>
            Categorical Columns ({categorical_columns?.length || 0})
          </Typography>
          <Box>
            {categorical_columns?.map(col => (
              <Chip key={col} label={col} size="small" color="secondary" sx={{ m: 0.25 }} />
            ))}
          </Box>
        </Grid>
        
        <Grid item xs={12} md={4}>
          <Typography variant="subtitle2" gutterBottom>
            <TimelineIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
            Date Columns ({date_columns?.length || 0})
          </Typography>
          <Box>
            {date_columns?.map(col => (
              <Chip key={col} label={col} size="small" color="info" sx={{ m: 0.25 }} />
            ))}
          </Box>
        </Grid>
      </Grid>
    );
  };

  return (
    <Box sx={{ p: { xs: 1, md: 3 } }}>
      <Typography variant="h4" gutterBottom>
        File Upload
      </Typography>
      
      <Typography variant="body1" color="text.secondary" paragraph>
        Upload CSV or Excel files for multi-temporal analysis. The system will automatically detect 
        schemas, align temporal data, and prepare files for advanced LangGraph workflow analysis.
      </Typography>

      {/* Upload Area */}
      <Card 
        sx={{ 
          mb: 3,
          border: isDragOver ? '2px dashed' : '2px dashed transparent',
          borderColor: isDragOver ? 'primary.main' : 'grey.300',
          bgcolor: isDragOver ? 'primary.50' : 'background.paper',
          transition: 'all 0.2s ease-in-out',
          cursor: 'pointer'
        }}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
      >
        <CardContent sx={{ textAlign: 'center', py: 4 }}>
          <CloudUpload sx={{ fontSize: 64, color: 'primary.main', mb: 2 }} />
          
          <Typography variant="h5" gutterBottom>
            {isDragOver ? 'Drop files here' : 'Upload Data Files'}
          </Typography>
          
          <Typography variant="body1" color="text.secondary" paragraph>
            Drag and drop files here, or click to browse
          </Typography>
          
          <Typography variant="body2" color="text.secondary" gutterBottom>
            Supported formats: CSV, Excel (.xlsx, .xls) • Max size: 100MB • Max files: {maxFiles}
          </Typography>
          
          <Button 
            variant="contained" 
            startIcon={<CloudUpload />}
            disabled={isUploading}
            sx={{ mt: 2 }}
          >
            {isUploading ? 'Uploading...' : 'Browse Files'}
          </Button>

          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileInputChange}
            multiple
            accept=".csv,.xlsx,.xls"
            style={{ display: 'none' }}
          />
        </CardContent>
      </Card>

      {/* Upload Progress */}
      {Object.keys(uploadProgress).length > 0 && (
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Upload Progress
            </Typography>
            {Object.entries(uploadProgress).map(([fileId, progress]) => (
              <Box key={fileId} sx={{ mb: 2 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="body2">
                    {progress.response?.filename || `File ${fileId}`}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {progress.status === 'completed' ? '✓ Complete' : 
                     progress.status === 'error' ? '✗ Failed' : 
                     `${progress.progress}%`}
                  </Typography>
                </Box>
                <LinearProgress 
                  variant="determinate" 
                  value={progress.progress} 
                  color={progress.status === 'error' ? 'error' : 'primary'}
                />
              </Box>
            ))}
          </CardContent>
        </Card>
      )}

      {/* Upload Errors */}
      {Object.keys(uploadErrors).length > 0 && (
        <Alert severity="error" sx={{ mb: 3 }}>
          <AlertTitle>Upload Errors</AlertTitle>
          {Object.entries(uploadErrors).map(([fileId, errors]) => (
            <Box key={fileId}>
              {errors.map((error, index) => (
                <Typography key={index} variant="body2">
                  • {error}
                </Typography>
              ))}
            </Box>
          ))}
        </Alert>
      )}

      {/* Uploaded Files */}
      {files.length > 0 && (
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Uploaded Files ({files.length})
            </Typography>
            
            <List>
              {files.map((file) => (
                <Box key={file.file_id}>
                  <ListItem
                    secondaryAction={
                      <Box>
                        <Tooltip title="Toggle details">
                          <IconButton 
                            edge="end" 
                            onClick={() => toggleFileExpansion(file.file_id)}
                            sx={{ mr: 1 }}
                          >
                            {expandedFiles[file.file_id] ? <CollapseIcon /> : <ExpandIcon />}
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Remove file">
                          <IconButton 
                            edge="end" 
                            color="error"
                            onClick={() => handleRemoveFile(file.file_id)}
                          >
                            <DeleteIcon />
                          </IconButton>
                        </Tooltip>
                      </Box>
                    }
                  >
                    <ListItemIcon>
                      {getFileTypeIcon(file.filename)}
                    </ListItemIcon>
                    <ListItemText
                      primary={
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          {file.filename}
                          <ValidIcon color="success" size="small" />
                        </Box>
                      }
                      secondary={
                        <Box sx={{ mt: 0.5 }}>
                          <Typography variant="body2" color="text.secondary">
                            {file.row_count?.toLocaleString()} rows • {file.columns?.length} columns • {(file.file_size / 1024 / 1024).toFixed(1)} MB
                          </Typography>
                        </Box>
                      }
                    />
                  </ListItem>

                  <Collapse in={expandedFiles[file.file_id]}>
                    <Box sx={{ pl: 4, pr: 2, pb: 2 }}>
                      {renderAnalysisInfo(file)}
                      {renderFilePreview(file)}
                    </Box>
                  </Collapse>

                  <Divider />
                </Box>
              ))}
            </List>

            {files.length > 0 && (
              <Alert 
                severity="success" 
                sx={{ 
                  mt: 2, 
                  cursor: 'pointer',
                  '&:hover': {
                    bgcolor: 'success.50',
                    transform: 'scale(1.02)',
                    transition: 'all 0.2s ease-in-out'
                  }
                }}
                onClick={() => window.location.href = '/chat'}
              >
                <AlertTitle>🎉 Files Ready for Analysis!</AlertTitle>
                Your files have been processed and are ready for multi-temporal analysis. 
                <strong>Click here</strong> or navigate to the <strong>AI Assistant</strong> tab to start asking questions about your data.
                <br />
                <small>💡 Try asking: "Compare revenue trends" or "Analyze seasonal patterns"</small>
              </Alert>
            )}
          </CardContent>
        </Card>
      )}

      {files.length === 0 && (
        <Alert severity="info">
          <AlertTitle>No Files Uploaded</AlertTitle>
          Upload CSV or Excel files to begin multi-temporal data analysis with our enhanced V2 system.
        </Alert>
      )}
    </Box>
  );
};

export default FileUploadPage;