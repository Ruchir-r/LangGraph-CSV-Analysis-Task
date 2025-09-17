/**
 * ChatInterface Component
 * Enhanced chat interface for V2 multi-temporal analysis system
 */

import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  List,
  ListItem,
  ListItemText,
  Alert,
  CircularProgress,
  LinearProgress,
  Chip,
  Switch,
  FormControlLabel,
  Paper,
  Divider,
  Tooltip,
  Badge
} from '@mui/material';
import { 
  Send as SendIcon, 
  Assessment as AnalysisIcon,
  QuestionAnswer as SimpleIcon,
  TrendingUp as ComprehensiveIcon,
  Info as InfoIcon
} from '@mui/icons-material';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import APIService from '../services/api';
import './ChatInterface.css';

// Message bubble component with markdown rendering
const MessageBubble = ({ message, type }) => {
  const isUser = type === 'user';
  
  return (
    <Box className={`chat-message-bubble ${isUser ? 'chat-message-user' : 'chat-message-assistant'}`}>
      <Box className="markdown-content">
        <ReactMarkdown 
          remarkPlugins={[remarkGfm]}
          components={{
            // Custom rendering for better integration with Material-UI
            p: ({ children }) => <div>{children}</div>,
            h1: ({ children }) => <h1>{children}</h1>,
            h2: ({ children }) => <h2>{children}</h2>,
            h3: ({ children }) => <h3>{children}</h3>,
            strong: ({ children }) => <strong>{children}</strong>,
            em: ({ children }) => <em>{children}</em>,
          }}
        >
          {message.content}
        </ReactMarkdown>
      </Box>
      
      <div className="message-timestamp">
        {new Date(message.timestamp).toLocaleTimeString()}
      </div>
      
      {/* Analysis indicators */}
      {message.metadata && (
        <Box className="analysis-indicators">
          {message.metadata.workflowInitiated && (
            <Chip 
              label="Analysis Started" 
              size="small" 
              color="primary" 
              variant={isUser ? "filled" : "outlined"}
            />
          )}
          {message.metadata.analysisScope && (
            <Chip 
              label={message.metadata.analysisScope === 'comprehensive_workflow' ? 'Comprehensive' : 'Simple'}
              size="small" 
              color={message.metadata.analysisScope === 'comprehensive_workflow' ? 'success' : 'default'}
              variant="outlined"
            />
          )}
        </Box>
      )}
    </Box>
  );
};

const ChatInterface = ({ 
  files, 
  sessionId, 
  onAnalysisStart, 
  onAnalysisComplete, 
  onAnalysisError,
  isAnalyzing 
}) => {
  const [message, setMessage] = useState('');
  const [analysisMode, setAnalysisMode] = useState('simple'); // 'simple' or 'comprehensive'
  const [messages, setMessages] = useState([
    {
      type: 'assistant',
      content: `# Welcome! 👋

I'm your **AI Data Analysis Assistant** with two powerful modes:

## 💬 Simple Mode
- Quick conversational responses
- File information queries  
- Help and guidance
- Instant answers

## 🚀 Comprehensive Mode
- **8-node LangGraph workflow**
- Multi-temporal analysis
- Trend detection & pattern analysis
- Python code generation
- Business insights & recommendations

---

**Getting started:** Upload some data files and choose your preferred analysis mode using the toggle above!`,
      timestamp: new Date().toISOString()
    }
  ]);
  const [loading, setLoading] = useState(false);
  const [workflowProgress, setWorkflowProgress] = useState(null);
  const [currentAnalysis, setCurrentAnalysis] = useState(null);
  const apiService = new APIService();
  const wsRef = useRef(null);

  // Load session history on mount and when session changes
  useEffect(() => {
    if (sessionId) {
      loadSessionHistory();
    }
  }, [sessionId]);
  
  // WebSocket connection for real-time updates
  useEffect(() => {
    if (sessionId && !wsRef.current) {
      connectWebSocket();
    }
    
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [sessionId]);
  
  // Load session history when switching analysis modes
  useEffect(() => {
    if (sessionId) {
      loadSessionHistory();
    }
  }, [analysisMode]);

  const loadSessionHistory = async () => {
    try {
      console.log('Loading session history for session:', sessionId);
      
      // Get complete session history (messages + analysis results)
      const historyResponse = await apiService.getSessionCompleteHistory(sessionId);
      
      if (historyResponse && historyResponse.combined_history) {
        const loadedMessages = [];
        
        // Convert history items to message format
        historyResponse.combined_history.forEach(item => {
          if (item.type === 'message') {
            // Regular chat message
            loadedMessages.push({
              type: item.data.message_type,
              content: item.data.content,
              timestamp: item.data.timestamp,
              metadata: item.data.analysis_results || {}
            });
          } else if (item.type === 'analysis') {
            // Comprehensive analysis result - add as assistant message
            const analysisData = item.data;
            const analysisMessage = {
              type: 'assistant',
              content: `**📊 Comprehensive Analysis Results**\n\n**Query:** ${analysisData.query}\n\n**Executive Summary:**\n${analysisData.analysis_results.executive_summary || 'Analysis completed successfully.'}\n\n**Key Findings:**\n${(analysisData.analysis_results.key_findings || []).map(f => `• ${f}`).join('\n')}\n\n**Recommended Actions:**\n${(analysisData.analysis_results.recommended_actions || []).map(a => `• ${a}`).join('\n')}`,
              timestamp: analysisData.created_at,
              isAnalysisComplete: true,
              analysisData: analysisData.analysis_results,
              metadata: {
                analysisType: 'comprehensive',
                taskId: analysisData.task_id,
                operationType: analysisData.operation_type
              }
            };
            loadedMessages.push(analysisMessage);
          }
        });
        
        // Only update messages if we have loaded history and current messages are just the welcome message
        if (loadedMessages.length > 0 && messages.length <= 1) {
          // Keep the welcome message at the beginning
          const welcomeMessage = messages[0];
          setMessages([welcomeMessage, ...loadedMessages]);
          console.log(`Loaded ${loadedMessages.length} messages from session history`);
        }
      }
    } catch (error) {
      console.error('Failed to load session history:', error);
      // Don't show error to user, just log it
    }
  };
  
  const connectWebSocket = () => {
    const wsUrl = `ws://localhost:8000/api/v2/ws/${sessionId}`;
    console.log('Connecting to WebSocket:', wsUrl);
    
    wsRef.current = new WebSocket(wsUrl);
    
    wsRef.current.onopen = () => {
      console.log('WebSocket connected');
    };
    
    wsRef.current.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        handleWebSocketMessage(data);
      } catch (error) {
        console.error('WebSocket message parsing error:', error);
      }
    };
    
    wsRef.current.onclose = () => {
      console.log('WebSocket disconnected');
      wsRef.current = null;
      // Attempt to reconnect after 5 seconds
      setTimeout(() => {
        if (sessionId) {
          connectWebSocket();
        }
      }, 5000);
    };
    
    wsRef.current.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
  };

  const handleWebSocketMessage = (data) => {
    console.log('WebSocket message received:', data);
    
    switch (data.type) {
      case 'progress_update':
        setWorkflowProgress({
          progress: data.progress_percentage,
          currentNode: data.current_node,
          statusMessage: data.status_message,
          completedNodes: data.completed_nodes,
          estimatedCompletion: data.estimated_completion_seconds
        });
        break;
        
      case 'analysis_complete':
        setWorkflowProgress(null);
        setCurrentAnalysis(data.result);
        
        // Add completion message to chat
        const completionMessage = {
          type: 'assistant',
          content: `✅ **Analysis Complete!** 🎉\n\nYour multi-temporal analysis is ready. Here are the key findings:\n\n${data.result.key_findings?.slice(0, 3).map(f => `• ${f}`).join('\n') || 'Analysis completed successfully.'}\n\n**Next Steps:**\n• Visit the Results tab to view detailed insights\n• Ask follow-up questions about specific findings\n• Request additional analysis on different aspects`,
          timestamp: new Date().toISOString(),
          isAnalysisComplete: true,
          analysisData: data.result
        };
        
        setMessages(prev => [...prev, completionMessage]);
        
        if (onAnalysisComplete) {
          onAnalysisComplete(data.result);
        }
        break;
        
      case 'analysis_error':
        setWorkflowProgress(null);
        let errorContent = `❌ Analysis failed: ${data.error}. Please try again with a different question or check your data files.`;
        
        // Check for LLM configuration errors
        if (data.error && (
            data.error.includes('No valid LLM providers configured') ||
            data.error.includes('API key not configured') ||
            data.error.includes('Cannot generate analysis') ||
            data.error.includes('LLM')
          )) {
          errorContent = `⚠️ **LLM Configuration Required**\n\n${data.error}\n\n**To use comprehensive analysis:**\n\n1. 🔑 Set up API keys:\n   \`\`\`bash\n   export GOOGLE_API_KEY="your_google_api_key"\n   export OPENAI_API_KEY="your_openai_api_key"\n   \`\`\`\n\n2. 🔄 Restart the backend\n3. ✅ Try your query again\n\n*Note: Simple mode works without API keys for basic queries.*`;
        }
        
        const errorMessage = {
          type: 'assistant',
          content: errorContent,
          timestamp: new Date().toISOString(),
          isError: true
        };
        setMessages(prev => [...prev, errorMessage]);
        break;
        
      default:
        console.log('Unknown WebSocket message type:', data.type);
    }
  };

  const handleSendMessage = async () => {
    if (!message.trim()) return;

    const userMessage = {
      type: 'user',
      content: message,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setMessage('');
    setLoading(true);

    try {
      // Get file IDs for context - handle both id and file_id field names
      const fileIds = files.map(file => file.id || file.file_id).filter(id => id);
      
      console.log('Debug - Files array:', files);
      console.log('Debug - Files length:', files.length);
      console.log('Debug - Analysis mode:', analysisMode);
      console.log('Debug - Extracted file IDs:', fileIds);
      
      let response;
      
      if (analysisMode === 'simple') {
        // Use simple chat API
        response = await apiService.sendSimpleChatMessage(
          message,
          sessionId,
          fileIds.length > 0 ? fileIds : null
        );
      } else {
        // Use comprehensive analysis (V2 enhanced chat)
        response = await apiService.sendComprehensiveChatMessage(
          message,
          sessionId,
          fileIds.length > 0 ? fileIds : null,
          true // use_comprehensive_analysis = true
        );
      }
      
      const assistantMessage = {
        type: 'assistant',
        content: response.response || 'I apologize, but I encountered an issue processing your request.',
        timestamp: new Date().toISOString(),
        metadata: {
          workflowInitiated: response.workflow_initiated,
          analysisScope: response.analysis_scope,
          suggestions: response.suggestions
        }
      };
      
      setMessages(prev => [...prev, assistantMessage]);
      
      // If workflow was initiated, update parent component
      if (response.workflow_initiated && onAnalysisStart) {
        onAnalysisStart(response);
      }
      
    } catch (error) {
      console.error('Chat API error:', error);
      let errorContent = 'I\'m sorry, I encountered an error while processing your request. Please try again or check your connection.';
      
      // Check for specific LLM configuration errors
      if (error.message && (
          error.message.includes('No valid LLM providers configured') ||
          error.message.includes('API key not configured') ||
          error.message.includes('Cannot generate analysis') ||
          error.message.includes('LLM')
        )) {
        errorContent = `⚠️ **LLM Configuration Required**\n\n${error.message}\n\n**To use comprehensive analysis:**\n\n1. 🔑 Set up API keys:\n   \`\`\`bash\n   export GOOGLE_API_KEY="your_google_api_key"\n   export OPENAI_API_KEY="your_openai_api_key"\n   \`\`\`\n\n2. 🔄 Restart the backend\n3. ✅ Try your query again\n\n*Note: Simple mode works without API keys for basic queries.*`;
      }
      
      const errorMessage = {
        type: 'assistant',
        content: errorContent,
        timestamp: new Date().toISOString(),
        isError: true
      };
      setMessages(prev => [...prev, errorMessage]);
      
      if (onAnalysisError) {
        onAnalysisError(error);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (event) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <Box sx={{ p: { xs: 1, md: 3 } }}>
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
        <Box>
          <Typography variant="h4" gutterBottom>
            AI Assistant
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Choose between quick responses or comprehensive multi-temporal analysis
          </Typography>
        </Box>
        
        <Paper elevation={2} sx={{ p: 2, minWidth: 300 }}>
          <Typography variant="subtitle2" gutterBottom>
            Analysis Mode
          </Typography>
          
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <SimpleIcon fontSize="small" color={analysisMode === 'simple' ? 'primary' : 'disabled'} />
              <Typography variant="body2" color={analysisMode === 'simple' ? 'primary' : 'text.secondary'}>
                Simple
              </Typography>
            </Box>
            
            <Switch
              checked={analysisMode === 'comprehensive'}
              onChange={(e) => setAnalysisMode(e.target.checked ? 'comprehensive' : 'simple')}
              color="primary"
            />
            
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <ComprehensiveIcon fontSize="small" color={analysisMode === 'comprehensive' ? 'primary' : 'disabled'} />
              <Typography variant="body2" color={analysisMode === 'comprehensive' ? 'primary' : 'text.secondary'}>
                Comprehensive
              </Typography>
            </Box>
          </Box>
          
          <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 1 }}>
            {analysisMode === 'simple' 
              ? '💬 Quick conversational responses'
              : '🚀 Full LangGraph workflow with trends & insights'
            }
          </Typography>
        </Paper>
      </Box>

      {files.length === 0 && (
        <Alert severity="info" sx={{ mb: 2 }}>
          Upload data files first to enable AI-powered analysis capabilities.
        </Alert>
      )}
      
      {workflowProgress && (
        <Card sx={{ mb: 2, bgcolor: 'primary.light', color: 'white' }}>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <AnalysisIcon sx={{ mr: 1 }} />
              <Typography variant="h6">Analysis in Progress</Typography>
              <Chip 
                label={`${Math.round(workflowProgress.progress)}%`} 
                size="small" 
                sx={{ ml: 'auto', bgcolor: 'white', color: 'primary.main' }}
              />
            </Box>
            
            <LinearProgress 
              variant="determinate" 
              value={workflowProgress.progress} 
              sx={{ mb: 2, bgcolor: 'rgba(255,255,255,0.3)' }}
            />
            
            <Typography variant="body2" sx={{ mb: 1 }}>
              Current Step: <strong>{workflowProgress.currentNode}</strong>
            </Typography>
            
            <Typography variant="body2">
              {workflowProgress.statusMessage}
            </Typography>
            
            {workflowProgress.estimatedCompletion && (
              <Typography variant="caption" sx={{ mt: 1, display: 'block' }}>
                ⏱️ Estimated completion: ~{workflowProgress.estimatedCompletion} seconds
              </Typography>
            )}
          </CardContent>
        </Card>
      )}

      <Card sx={{ mb: 2, height: '60vh', display: 'flex', flexDirection: 'column' }}>
        <CardContent sx={{ flex: 1, overflow: 'auto' }}>
          <List>
            {messages.map((msg, index) => (
              <ListItem key={index} sx={{ 
                justifyContent: msg.type === 'user' ? 'flex-end' : 'flex-start',
                pb: 2,
                alignItems: 'flex-start'
              }}>
                <MessageBubble message={msg} type={msg.type} />
              </ListItem>
            ))}
          </List>
        </CardContent>
        
        <Box sx={{ p: 2, borderTop: 1, borderColor: 'divider' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
            <Chip 
              icon={analysisMode === 'simple' ? <SimpleIcon /> : <ComprehensiveIcon />}
              label={analysisMode === 'simple' ? 'Simple Mode' : 'Comprehensive Mode'}
              color={analysisMode === 'simple' ? 'default' : 'primary'}
              size="small"
            />
            {files.length === 0 && analysisMode === 'comprehensive' && (
              <Tooltip title="Upload files to enable comprehensive analysis">
                <Chip 
                  icon={<InfoIcon />}
                  label="No files uploaded"
                  color="warning"
                  size="small"
                />
              </Tooltip>
            )}
          </Box>
          
          <Box sx={{ display: 'flex', gap: 1 }}>
            <TextField
              fullWidth
              multiline
              maxRows={3}
              placeholder={analysisMode === 'simple' 
                ? "Ask me quick questions about your data..." 
                : "Describe what analysis you'd like me to perform..."
              }
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              disabled={isAnalyzing || loading || (analysisMode === 'comprehensive' && files.length === 0)}
              helperText={analysisMode === 'comprehensive' && files.length === 0 
                ? "Upload data files to enable comprehensive analysis" 
                : null
              }
            />
            <Button
              variant="contained"
              endIcon={loading ? <CircularProgress size={20} color="inherit" /> : <SendIcon />}
              onClick={handleSendMessage}
              disabled={!message.trim() || isAnalyzing || loading || (analysisMode === 'comprehensive' && files.length === 0)}
              sx={{ minWidth: 100, alignSelf: 'flex-start' }}
            >
              {loading ? 'Sending...' : 'Send'}
            </Button>
          </Box>
        </Box>
      </Card>
    </Box>
  );
};

export default ChatInterface;