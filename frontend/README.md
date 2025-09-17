# Frontend - React Application

## Version 1 Features

### Core Components
- **File Upload**: Drag-and-drop CSV file upload interface
- **Data Preview**: Table view of uploaded data with column information
- **Analytics Panel**: Simple controls for basic analysis operations
- **Chat Interface**: Basic chat UI with predefined responses
- **Results Display**: Tables and simple charts for analysis results

### User Interface
- Clean, responsive design using Material-UI
- Single-page application with React Router
- Real-time communication with backend API
- File upload progress indicators
- Error handling and user feedback

## Component Structure

```
src/
├── components/
│   ├── FileUpload/
│   │   ├── FileUpload.jsx     # Main upload component
│   │   └── FileUpload.css     # Styling
│   ├── DataPreview/
│   │   ├── DataPreview.jsx    # Data table display
│   │   └── DataPreview.css    # Table styling
│   ├── Analytics/
│   │   ├── AnalyticsPanel.jsx # Analysis controls
│   │   └── ResultsDisplay.jsx # Results visualization
│   ├── Chat/
│   │   ├── ChatInterface.jsx  # Chat UI
│   │   ├── MessageBubble.jsx  # Individual messages
│   │   └── Chat.css           # Chat styling
│   └── Common/
│       ├── Header.jsx         # App header
│       ├── Sidebar.jsx        # Navigation sidebar
│       └── Layout.jsx         # Main layout wrapper
├── pages/
│   ├── Home.jsx               # Landing page
│   ├── Upload.jsx             # File upload page
│   ├── Analysis.jsx           # Analysis dashboard
│   └── Chat.jsx               # Chat page
├── services/
│   ├── api.js                 # API client functions
│   ├── fileService.js         # File handling utilities
│   └── chatService.js         # Chat functionality
├── hooks/
│   ├── useFileUpload.js       # File upload custom hook
│   └── useAnalytics.js        # Analytics custom hook
├── utils/
│   ├── constants.js           # App constants
│   └── helpers.js             # Utility functions
├── App.jsx                    # Main app component
├── App.css                    # Global styles
└── index.js                   # App entry point
```

## Setup Instructions

### Prerequisites
- Node.js 18+
- npm or yarn

### Installation
```bash
npm install
# or
yarn install
```

### Development Server
```bash
npm start
# or
yarn start
```

The app will be available at `http://localhost:3000`

### Build for Production
```bash
npm run build
# or
yarn build
```

## API Integration

### Configuration
The frontend uses a proxy configuration to communicate with the backend:
- Backend API: `http://localhost:8000`
- Frontend Dev Server: `http://localhost:3000`

### API Services

#### File Upload
```javascript
// Upload a CSV file
const uploadFile = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  return await api.post('/api/files/upload', formData);
};
```

#### Analytics
```javascript
// Get basic analytics
const getAnalytics = async (fileId, operation, column) => {
  return await api.post('/api/analytics/basic', {
    file_id: fileId,
    operation,
    column
  });
};
```

#### Chat
```javascript
// Send chat message
const sendMessage = async (message, sessionId) => {
  return await api.post('/api/chat/query', {
    message,
    session_id: sessionId
  });
};
```

## User Flow (Version 1)

1. **Landing Page**: Introduction and getting started guide
2. **File Upload**: User uploads a CSV file
3. **Data Preview**: System shows file structure and first few rows
4. **Analytics**: User selects columns and operations for analysis
5. **Results**: Display analysis results in tables and simple charts
6. **Chat**: Basic conversational interface for common queries

## Styling Guidelines

### Material-UI Theme
- Primary Color: `#1976d2` (Blue)
- Secondary Color: `#dc004e` (Pink)
- Background: `#f5f5f5` (Light Grey)
- Typography: Roboto font family

### Responsive Design
- Mobile-first approach
- Breakpoints: xs, sm, md, lg, xl
- Flexible layouts using Grid and Flexbox

## Testing

```bash
# Run tests
npm test

# Run tests with coverage
npm test -- --coverage
```

## Development Notes

### Version 1 Limitations
- Single file upload only
- Basic chart types (bar, line, pie)
- Simple chat with pattern matching
- No authentication or user management
- Local state management only

### Version 2 Enhancements
- Multiple file handling
- Advanced visualizations
- Real-time chat with WebSocket
- State management with Redux/Context
- User authentication
- Data export functionality

## Environment Variables

Create a `.env` file in the frontend directory:

```bash
REACT_APP_API_URL=http://localhost:8000
REACT_APP_VERSION=1.0.0
REACT_APP_ENVIRONMENT=development
```
