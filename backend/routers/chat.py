"""
Chat Router - Clean & Simple
Provides direct conversational responses for basic questions
Integrates with V2 analytics for complex analysis
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import uuid
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from app.database import SessionModel, MessageModel, FileModel
from services.llm_providers import llm_manager, LLMMessage

logger = logging.getLogger(__name__)

router = APIRouter()

class SimpleChatRequest(BaseModel):
    """Simple chat request for direct conversational responses"""
    message: str
    session_id: Optional[str] = None
    file_ids: Optional[List[int]] = None  # Specific files to use as context
    include_file_context: bool = True

class SimpleChatResponse(BaseModel):
    """Simple chat response with suggestions"""
    response: str
    session_id: str
    response_type: str  # 'simple', 'help', 'file_info', 'suggestion'
    suggestions: Optional[List[str]] = None
    file_context: Optional[Dict[str, Any]] = None
    
    class Config:
        schema_extra = {
            "example": {
                "response": "Hello! I can help you analyze your data files.",
                "session_id": "abc123",
                "response_type": "simple",
                "suggestions": ["Upload a file", "Ask about data analysis", "Get help"]
            }
        }

def generate_session_id() -> str:
    """Generate a new session ID"""
    return str(uuid.uuid4())

async def generate_simple_response(message: str, files: List[Dict] = None, session_id: str = None, conversation_history: List[Dict] = None) -> SimpleChatResponse:
    """Generate simple conversational response using LLM or fallback patterns with conversation context"""
    message_lower = message.lower().strip()
    
    # Quick pattern-based responses for common queries
    if any(word in message_lower for word in ['hello', 'hi', 'hey', 'good morning', 'good afternoon']):
        return SimpleChatResponse(
            response="# Hello! 👋\n\nI'm your **data analysis assistant**. I can help you understand your data through:\n\n- **Quick Q&A** for simple questions\n- **Comprehensive analysis workflows** for deep insights\n\nHow can I assist you today?",
            session_id="",  # Will be set by calling function
            response_type="greeting",
            suggestions=[
                "What can you help me with?",
                "Upload data files", 
                "Show me example questions",
                "Run comprehensive analysis"
            ]
        )
    
    elif any(word in message_lower for word in ['help', 'what can you do', 'capabilities']):
        return SimpleChatResponse(
            response="""# My Capabilities 🤖

I'm your **AI data analysis assistant** with these features:

## 📊 Quick Q&A
- Ask simple questions about your data
- Get instant answers about file contents
- Basic data exploration guidance

## 🔍 File Information
- View details about uploaded files
- Check data quality and structure
- Preview column information

## 📈 Comprehensive Analysis
- **8-node LangGraph workflow**
- Multi-temporal data analysis
- Trend detection and pattern analysis
- Python code generation
- Business insights and recommendations

## 💡 Smart Suggestions
- Get recommendations for data exploration
- Actionable next steps
- Analysis guidance

---

## Two Analysis Modes:

### 💬 **Simple Mode**
> Quick conversational responses for basic questions

### 🚀 **Comprehensive Mode** 
> Full LangGraph workflow with trend detection and detailed insights

**Switch modes** using the toggle in the interface!""",
            session_id="",
            response_type="help",
            suggestions=[
                "Show my uploaded files",
                "What's the difference between simple and analysis mode?",
                "Run a comprehensive analysis",
                "Give me example questions"
            ]
        )
    
    elif any(phrase in message_lower for phrase in ['show my files', 'list my files', 'what files do i have', 'what files are uploaded', 'show uploaded files']):
        if not files or len(files) == 0:
            return SimpleChatResponse(
                response="## No Files Uploaded Yet 📁\n\n**Upload CSV or Excel files** to start analyzing your data. Once uploaded, I can help you explore the data through:\n\n- **Simple questions** for quick insights\n- **Comprehensive analysis** for detailed reports\n\n📝 *Supported formats: CSV, Excel (.xlsx, .xls)*",
                session_id="",
                response_type="file_info",
                suggestions=[
                    "Upload a data file",
                    "What file formats are supported?",
                    "Show example data"
                ]
            )
        else:
            # Create markdown table for files
            file_table_rows = []
            for file in files[:5]:  # Show first 5 files
                columns_display = ', '.join(file.get('columns', [])[:3])
                if len(file.get('columns', [])) > 3:
                    columns_display += '...'
                file_table_rows.append(f"| {file.get('original_filename', 'Unknown')} | {file.get('row_count', 0)} | {columns_display} |")
            
            file_table = "| Filename | Rows | Key Columns |\n|----------|------|-------------|\n" + "\n".join(file_table_rows)
            more_files = f"\n\n*+{len(files) - 5} more files available*" if len(files) > 5 else ""
            
            return SimpleChatResponse(
                response=f"## Your Data Files 📂\n\nYou have **{len(files)} files** uploaded and ready for analysis:\n\n{file_table}{more_files}\n\n---\n\n🚀 **Ready to analyze!** Ask specific questions or switch to comprehensive mode for detailed insights.",
                session_id="",
                response_type="file_info",
                file_context={"file_count": len(files), "files": files[:3]},
                suggestions=[
                    "What's the average revenue?",
                    "Run comprehensive analysis", 
                    "Compare data across time periods",
                    "Show data quality summary"
                ]
            )
    
    # For other queries, try to use LLM for more intelligent responses
    try:
        file_context = ""
        if files and len(files) > 0:
            # Create detailed file context with structure information
            file_details = []
            for file in files[:3]:  # Limit to first 3 files for context length
                columns = file.get('columns', [])
                numeric_cols = file.get('numeric_columns', [])
                categorical_cols = file.get('categorical_columns', [])
                date_cols = file.get('date_columns', [])
                
                file_detail = f"'{file['original_filename']}' ({file['row_count']} rows)"
                file_detail += f" - Columns: {', '.join(columns[:6])}"
                if len(columns) > 6:
                    file_detail += f" + {len(columns)-6} more"
                
                # Add column type information
                if numeric_cols:
                    file_detail += f" | Numeric: {', '.join(numeric_cols[:3])}"
                if categorical_cols:
                    file_detail += f" | Categorical: {', '.join(categorical_cols[:3])}"
                if date_cols:
                    file_detail += f" | Dates: {', '.join(date_cols)}"
                    
                file_details.append(file_detail)
            
            files_info = "\n".join([f"  - {detail}" for detail in file_details])
            file_context = f"\n\nAVAILABLE DATA FILES:\n{files_info}"
            
            if len(files) > 3:
                file_context += f"\n  - ... and {len(files)-3} more files"
        
        # Build conversation context
        conversation_context = ""
        if conversation_history and len(conversation_history) > 0:
            # Include recent conversation for context (last 6 messages)
            recent_messages = conversation_history[-6:] if len(conversation_history) > 6 else conversation_history
            context_parts = []
            for msg in recent_messages:
                role = "User" if msg['message_type'] == 'user' else "Assistant"
                content = msg['content'][:200] + "..." if len(msg['content']) > 200 else msg['content']
                context_parts.append(f"{role}: {content}")
            
            conversation_context = f"\n\nRECENT CONVERSATION CONTEXT:\n" + "\n".join(context_parts)
        
        system_prompt = (
            "You are an AI data analysis assistant with access to the user's uploaded data files via a database. "
            "You CAN analyze, examine, and provide insights about the uploaded data. "
            "When users ask about datatypes, columns, or data analysis, you can provide specific information based on the file schemas provided. "
            "For complex analysis requiring code execution, suggest using comprehensive analysis mode. "
            "Be conversational, helpful, and specific about what you can see in their data. "
            "Use the conversation context to understand follow-up questions and maintain conversational flow. "
            "If the user refers to 'it', 'that', 'the previous analysis', etc., use the conversation context to understand what they're referring to."
            f"{file_context}"
            f"{conversation_context}"
        )
        
        messages = [
            LLMMessage(role="system", content=system_prompt),
            LLMMessage(role="user", content=message)
        ]
        
        llm_response = await llm_manager.generate(messages)
        
        return SimpleChatResponse(
            response=llm_response.content,
            session_id="",
            response_type="simple",
            suggestions=[
                "Ask another question",
                "Run comprehensive analysis" if files else "Upload data files",
                "Get help with data analysis"
            ],
            file_context={"has_files": bool(files)} if files else None
        )
        
    except Exception as e:
        # Log the error and re-raise it  
        logger.error(f"Simple chat LLM generation failed: {e}")
        return SimpleChatResponse(
            response=f"Sorry, I encountered an error processing your question: {str(e)}",
            session_id="",
            response_type="error",
            suggestions=[
                "Try rephrasing your question",
                "Check if the backend services are running",
                "Contact support if the issue persists"
            ]
        )

@router.post("/simple", response_model=SimpleChatResponse)
async def simple_chat_query(request: SimpleChatRequest):
    """
    Simple conversational chat interface
    
    Provides quick, direct responses to basic questions without triggering
    complex analysis workflows. Perfect for:
    - Getting information about uploaded files
    - Understanding system capabilities 
    - Quick Q&A about data
    - Help and guidance
    """
    try:
        # Generate or use existing session ID
        session_id = request.session_id or generate_session_id()
        
        # Create/update session
        SessionModel.create_or_get(session_id)
        
        # Store user message
        MessageModel.create(session_id, "user", request.message)
        
        # Get conversation history for context
        conversation_history = MessageModel.get_session_history(session_id, limit=10)
        
        # Get file context - use specific file_ids if provided, otherwise all files
        files = []
        if request.include_file_context:
            if request.file_ids:
                # Use only the specified files
                files = []
                for file_id in request.file_ids:
                    file_info = FileModel.get_by_id(file_id)
                    if file_info:
                        files.append(file_info)
            else:
                # Fallback to all files (for backward compatibility)
                files = FileModel.get_all()
        
        # Generate simple response with conversation context
        response_data = await generate_simple_response(
            request.message, 
            files, 
            session_id, 
            conversation_history
        )
        response_data.session_id = session_id
        
        # Store assistant response
        MessageModel.create(
            session_id,
            "assistant", 
            response_data.response,
            {
                "response_type": response_data.response_type,
                "suggestions": response_data.suggestions
            }
        )
        
        return response_data
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Simple chat processing failed: {str(e)}"
        )

@router.post("/query") 
async def legacy_chat_query(request: SimpleChatRequest):
    """
    Legacy chat endpoint - redirects to simple chat for backward compatibility
    
    This endpoint maintains compatibility with existing clients while
    providing the improved simple chat functionality.
    """
    # Convert to simple chat and process
    return await simple_chat_query(request)

@router.get("/sessions")
async def get_chat_sessions():
    """Get list of all chat sessions"""
    # This is a simplified version - in practice you'd want pagination
    try:
        # For now, we'll return a basic response
        # In a full implementation, you'd query the sessions table
        return {
            "sessions": [],
            "message": "Session listing not fully implemented in Version 1"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching sessions: {str(e)}")

@router.get("/sessions/{session_id}/history")
async def get_session_history(session_id: str, limit: int = 50):
    """Get chat history for a session"""
    
    try:
        messages = MessageModel.get_session_history(session_id, limit)
        return {
            "session_id": session_id,
            "messages": messages,
            "count": len(messages)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching session history: {str(e)}")

@router.get("/examples")
async def get_example_queries():
    """Get example queries users can try"""
    return {
        "categories": {
            "Basic Analytics": [
                "What's the average revenue?",
                "Show me total sales",
                "Count the number of orders",
                "What's the maximum discount?"
            ],
            "Grouped Analysis": [
                "Average revenue by region",
                "Total units by product",
                "Sales count by region",
                "Maximum price by product type"
            ],
            "Comparisons": [
                "Compare revenue and units",
                "Show revenue vs discount correlation",
                "Compare sales across regions"
            ],
            "Data Exploration": [
                "Analyze my data",
                "Show me a summary",
                "What columns do I have?",
                "Check data quality"
            ]
        },
        "tips": [
            "Upload a CSV file first to start analyzing",
            "Be specific about which column you want to analyze",
            "Use 'by [column]' to group your analysis",
            "Ask for help anytime with 'What can you do?'"
        ]
    }
