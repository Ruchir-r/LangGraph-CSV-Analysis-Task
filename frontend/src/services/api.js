// API Service for V2 Backend Integration
// Supports LangGraph workflows and multi-temporal analysis

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

class APIService {
  constructor() {
    this.baseURL = API_BASE_URL;
  }

  // Helper method to handle API requests
  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const defaultOptions = {
      headers: {
        'Content-Type': 'application/json',
      },
    };

    const finalOptions = { ...defaultOptions, ...options };

    try {
      const response = await fetch(url, finalOptions);
      
      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`API Error ${response.status}: ${errorText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  }

  // File Upload API
  async uploadFile(file) {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${this.baseURL}/api/files/upload`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`Upload failed: ${response.statusText}`);
    }

    return await response.json();
  }

  // Upload multiple files
  async uploadFiles(files) {
    const uploadPromises = files.map(file => this.uploadFile(file));
    return Promise.all(uploadPromises);
  }

  // Get file preview
  async getFilePreview(fileId, rows = 10) {
    return this.request(`/api/files/${fileId}/preview?rows=${rows}`);
  }

  // Get file schema information
  async getFileSchema(fileId) {
    return this.request(`/api/files/${fileId}/schema`);
  }

  // List all uploaded files
  async listFiles() {
    return this.request('/api/files/');
  }

  // V2 Multi-temporal Analysis via LangGraph
  async performMultiTemporalAnalysis(query, fileIds, sessionId) {
    return this.request('/api/v2/analyze', {
      method: 'POST',
      body: JSON.stringify({
        query,
        file_ids: fileIds,
        session_id: sessionId,
      }),
    });
  }

  // Simple Chat Interface - Quick responses without workflow
  async sendSimpleChatMessage(message, sessionId, fileIds = null) {
    const requestBody = {
      message,
      session_id: sessionId,
      include_file_context: fileIds ? true : false,
    };
    
    // Add file_ids if provided
    if (fileIds && fileIds.length > 0) {
      requestBody.file_ids = fileIds;
    }
    
    return this.request('/api/chat/simple', {
      method: 'POST', 
      body: JSON.stringify(requestBody),
    });
  }
  
  // Comprehensive Chat Interface - Full LangGraph workflow
  async sendComprehensiveChatMessage(message, sessionId, fileContext = null, useComprehensiveAnalysis = true) {
    return this.request('/api/v2/chat/query', {
      method: 'POST',
      body: JSON.stringify({
        message,
        session_id: sessionId,
        file_context: fileContext,
        use_comprehensive_analysis: useComprehensiveAnalysis,
        analysis_mode: "comprehensive",
      }),
    });
  }
  
  // Legacy Chat Interface - Backward compatibility
  async sendChatMessage(message, sessionId, fileContext = null, enableWorkflow = true) {
    if (enableWorkflow && fileContext) {
      return this.sendComprehensiveChatMessage(message, sessionId, fileContext, true);
    } else {
      return this.sendSimpleChatMessage(message, sessionId, fileContext);
    }
  }

  // Get chat history
  async getChatHistory(sessionId, limit = 50) {
    return this.request(`/api/chat/sessions/${sessionId}/history?limit=${limit}`);
  }
  
  // Get complete session history including chat and analysis results
  async getSessionCompleteHistory(sessionId) {
    return this.request(`/api/v2/sessions/${sessionId}/history`);
  }
  
  // Get comprehensive analysis results for a session
  async getSessionAnalyses(sessionId, limit = 10) {
    return this.request(`/api/v2/sessions/${sessionId}/analyses?limit=${limit}`);
  }

  // V2 Background Task Management
  async getTaskStatus(taskId) {
    return this.request(`/api/v2/tasks/${taskId}/status`);
  }

  // Poll task until completion
  async pollTaskCompletion(taskId, onProgress = null) {
    return new Promise((resolve, reject) => {
      const pollInterval = setInterval(async () => {
        try {
          const status = await this.getTaskStatus(taskId);
          
          if (onProgress) {
            onProgress(status);
          }

          if (status.status === 'completed') {
            clearInterval(pollInterval);
            resolve(status.result_data);
          } else if (status.status === 'failed') {
            clearInterval(pollInterval);
            reject(new Error(status.error_message || 'Task failed'));
          }
        } catch (error) {
          clearInterval(pollInterval);
          reject(error);
        }
      }, 1000); // Poll every second

      // Timeout after 5 minutes
      setTimeout(() => {
        clearInterval(pollInterval);
        reject(new Error('Task timeout'));
      }, 300000);
    });
  }

  // V2 Advanced Analytics
  async getAnalyticsSummary(fileId) {
    return this.request(`/api/analytics/summary/${fileId}`);
  }

  // Compare columns across files
  async compareColumns(fileId, column1, column2) {
    return this.request(`/api/analytics/compare`, {
      method: 'POST',
      body: JSON.stringify({
        file_id: fileId,
        column1,
        column2,
      }),
    });
  }

  // Get analysis results by session
  async getAnalysisResults(sessionId) {
    return this.request(`/api/v2/results/${sessionId}`);
  }

  // Health check
  async healthCheck() {
    return this.request('/health');
  }

  // Get system status
  async getSystemStatus() {
    return this.request('/api/v2/system/status');
  }

  // V2 Example queries for user guidance
  async getExampleQueries() {
    return this.request('/api/chat/examples');
  }

  // WebSocket connection for real-time updates (V2 enhancement)
  createWebSocketConnection(sessionId, onMessage) {
    const wsURL = this.baseURL.replace('http', 'ws') + `/ws/${sessionId}`;
    const ws = new WebSocket(wsURL);

    ws.onopen = () => {
      console.log('WebSocket connected');
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        onMessage(data);
      } catch (error) {
        console.error('WebSocket message parsing error:', error);
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    ws.onclose = () => {
      console.log('WebSocket disconnected');
    };

    return ws;
  }
}

// Mock API Service for development when backend is not available
class MockAPIService extends APIService {
  constructor() {
    super();
    this.mockFiles = [];
    this.mockMessages = [];
  }

  async uploadFile(file) {
    // Simulate upload delay
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    const mockFile = {
      file_id: Date.now(),
      filename: file.name,
      file_size: file.size,
      columns: ['Order_ID', 'Customer_ID', 'Region', 'Product', 'Units', 'Revenue', 'Discount'],
      row_count: Math.floor(Math.random() * 1000) + 100,
      analysis: {
        numeric_columns: ['Units', 'Revenue', 'Discount'],
        categorical_columns: ['Region', 'Product', 'Customer_ID'],
        date_columns: ['Order_Date']
      },
      preview: [
        { Order_ID: 1001, Customer_ID: 'CUST-01', Region: 'APAC', Product: 'Widget-A', Units: 32, Revenue: 319.2 },
        { Order_ID: 1002, Customer_ID: 'CUST-02', Region: 'EU', Product: 'Widget-B', Units: 100, Revenue: 1800.0 },
        { Order_ID: 1003, Customer_ID: 'CUST-03', Region: 'NA', Product: 'Widget-A', Units: 15, Revenue: 157.5 }
      ],
      message: `File '${file.name}' uploaded successfully!`
    };

    this.mockFiles.push(mockFile);
    return mockFile;
  }

  async listFiles() {
    return {
      files: this.mockFiles,
      count: this.mockFiles.length
    };
  }

  async performMultiTemporalAnalysis(query, fileIds, sessionId) {
    // Simulate analysis delay
    await new Promise(resolve => setTimeout(resolve, 2000));

    return {
      query,
      operation_type: 'temporal_comparison',
      files_analyzed: fileIds.length,
      execution_result: {
        success: true,
        result: {
          average_revenue_nov: 825.6,
          average_revenue_dec: 980.3,
          growth_rate: 18.7,
          top_region: 'EU'
        }
      },
      explanation: `Analysis of ${fileIds.length} files shows a 18.7% growth in average revenue from November to December 2024. The EU region demonstrated the strongest performance with consistent growth across all product categories.`,
      key_findings: [
        'Revenue increased by 18.7% month-over-month',
        'EU region led growth with 25% increase',
        'Widget-B showed strongest product performance',
        'Online channel outperformed retail by 12%'
      ],
      recommended_actions: [
        'Increase inventory for Widget-B in EU region',
        'Expand online marketing campaigns',
        'Analyze discount impact on margins',
        'Prepare for Q1 2025 demand surge'
      ],
      confidence_score: 0.92,
      metadata: {
        execution_id: `exec_${Date.now()}`,
        processing_time: '2.1s',
        nodes_completed: ['parse_files', 'plan_operations', 'align_timeseries', 'generate_code', 'validate_code', 'execute_code', 'trend_analysis', 'explain_result']
      }
    };
  }

  async sendChatMessage(message, sessionId) {
    await new Promise(resolve => setTimeout(resolve, 800));

    const mockResponse = {
      response: `I understand you're asking about "${message}". Based on the uploaded data files, I can help you analyze trends, compare time periods, and generate insights. Would you like me to perform a detailed multi-temporal analysis?`,
      session_id: sessionId,
      analysis_results: {
        intent: 'analysis_request',
        confidence: 0.85,
        suggested_operations: ['temporal_comparison', 'trend_analysis']
      },
      suggestions: [
        'Compare revenue growth across months',
        'Analyze regional performance trends',
        'Show top performing products',
        'Calculate discount impact on revenue'
      ]
    };

    this.mockMessages.push({
      id: Date.now(),
      message_type: 'user',
      content: message,
      timestamp: new Date().toISOString()
    });

    this.mockMessages.push({
      id: Date.now() + 1,
      message_type: 'assistant',
      content: mockResponse.response,
      timestamp: new Date().toISOString()
    });

    return mockResponse;
  }

  async getChatHistory(sessionId) {
    return {
      session_id: sessionId,
      messages: this.mockMessages,
      count: this.mockMessages.length
    };
  }

  async healthCheck() {
    return {
      status: 'healthy',
      version: '2.0.0',
      mode: 'mock',
      message: 'Mock API service running for development'
    };
  }
}

// Export the APIService class as default
export default APIService;

// Also export a factory function for flexibility
export const createAPIService = () => {
  const isDevelopment = process.env.NODE_ENV === 'development';
  const useMock = process.env.REACT_APP_USE_MOCK_API === 'true';
  
  if (isDevelopment && useMock) {
    console.log('Using Mock API Service for development');
    return new MockAPIService();
  } else {
    console.log('Using Real API Service');
    return new APIService();
  }
};

// Export mock service for testing
export { MockAPIService };
