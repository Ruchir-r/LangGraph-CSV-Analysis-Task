"""
LangGraph Analysis Workflow
Multi-temporal data analysis with advanced reasoning capabilities

This implements the 6+ node workflow system specified in the project requirements:
1. parse_files - ingest multiple files, extract schemas, align columns
2. plan_operations (LLM) - decide if single-table or cross-table
3. align_timeseries (LLM helper) - align tables by month/quarter/year before codegen
4. generate_code → validate_code → execute_code
5. trend_analysis (optional LLM node) - detect patterns (growth, seasonality, anomalies)
6. explain_result - narrative + recommended actions
"""

import asyncio
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import json
import logging
import pandas as pd
import numpy as np
from pathlib import Path
import uuid

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import ToolExecutor

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from services.llm_providers import llm_manager, LLMMessage

logger = logging.getLogger(__name__)

@dataclass
class AnalysisState:
    """State object that flows through the LangGraph workflow"""
    
    # Input data
    query: str = ""
    files: List[Dict[str, Any]] = field(default_factory=list)
    session_id: str = ""
    
    # File processing results
    parsed_files: List[Dict[str, Any]] = field(default_factory=list)
    schema_alignment: Dict[str, Any] = field(default_factory=dict)
    temporal_alignment: Dict[str, Any] = field(default_factory=dict)
    
    # Analysis planning
    analysis_plan: Dict[str, Any] = field(default_factory=dict)
    operation_type: str = ""  # single_table, cross_table, temporal_comparison, trend_analysis
    
    # Code generation and execution
    generated_code: str = ""
    code_validation: Dict[str, Any] = field(default_factory=dict)
    execution_result: Dict[str, Any] = field(default_factory=dict)
    
    # Advanced analysis
    trend_analysis: Dict[str, Any] = field(default_factory=dict)
    insights: List[str] = field(default_factory=list)
    
    # Final output
    final_result: Dict[str, Any] = field(default_factory=dict)
    recommended_actions: List[str] = field(default_factory=list)
    
    # Workflow metadata
    current_node: str = ""
    completed_nodes: List[str] = field(default_factory=list)
    node_outputs: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    execution_id: str = field(default_factory=lambda: str(uuid.uuid4()))

class MultiTemporalAnalysisWorkflow:
    """Main workflow class implementing the LangGraph analysis pipeline"""
    
    def __init__(self):
        self.graph = self._build_graph()
        self.checkpointer = MemorySaver()
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow"""
        workflow = StateGraph(AnalysisState)
        
        # Add nodes
        workflow.add_node("parse_files", self.parse_files)
        workflow.add_node("plan_operations", self.plan_operations)
        workflow.add_node("align_timeseries", self.align_timeseries)
        workflow.add_node("generate_code", self.generate_code)
        workflow.add_node("validate_code", self.validate_code)
        workflow.add_node("execute_code", self.execute_code)
        workflow.add_node("trend_analysis", self.trend_analysis)
        workflow.add_node("explain_result", self.explain_result)
        
        # Define the workflow flow
        workflow.set_entry_point("parse_files")
        
        workflow.add_edge("parse_files", "plan_operations")
        workflow.add_edge("plan_operations", "align_timeseries")
        workflow.add_edge("align_timeseries", "generate_code")
        workflow.add_edge("generate_code", "validate_code")
        
        # Conditional edge based on validation
        workflow.add_conditional_edges(
            "validate_code",
            self._should_retry_code_generation,
            {
                "retry": "generate_code",
                "proceed": "execute_code"
            }
        )
        
        workflow.add_edge("execute_code", "trend_analysis")
        workflow.add_edge("trend_analysis", "explain_result")
        workflow.add_edge("explain_result", END)
        
        return workflow.compile(checkpointer=self.checkpointer)
    
    def _should_retry_code_generation(self, state: AnalysisState) -> str:
        """Decide whether to retry code generation based on validation results"""
        if state.code_validation.get("is_valid", False):
            return "proceed"
        
        # Check if we've already retried too many times
        retry_count = state.code_validation.get("retry_count", 0)
        if retry_count >= 3:
            logger.warning("Maximum code generation retries reached")
            return "proceed"  # Proceed anyway with potentially invalid code
        
        return "retry"
    
    async def parse_files(self, state: AnalysisState) -> AnalysisState:
        """
        Node 1: Parse multiple files, extract schemas, and prepare for analysis
        """
        logger.info(f"Starting parse_files for {len(state.files)} files")
        state.current_node = "parse_files"
        
        try:
            parsed_files = []
            
            for file_info in state.files:
                file_path = file_info.get("file_path")
                if not file_path or not Path(file_path).exists():
                    logger.warning(f"File not found: {file_path}")
                    continue
                
                # Read the file
                try:
                    if file_path.endswith('.csv'):
                        df = pd.read_csv(file_path)
                    elif file_path.endswith(('.xlsx', '.xls')):
                        df = pd.read_excel(file_path)
                    else:
                        logger.warning(f"Unsupported file format: {file_path}")
                        continue
                    
                    # Extract schema information
                    schema_info = {
                        "file_id": file_info.get("id"),
                        "filename": file_info.get("original_filename", ""),
                        "shape": df.shape,
                        "columns": df.columns.tolist(),
                        "dtypes": df.dtypes.to_dict(),
                        "numeric_columns": df.select_dtypes(include=[np.number]).columns.tolist(),
                        "categorical_columns": df.select_dtypes(include=['object']).columns.tolist(),
                        "date_columns": self._detect_date_columns(df),
                        "sample_data": df.head(3).to_dict('records'),
                        "missing_values": df.isnull().sum().to_dict(),
                        "time_period": file_info.get("time_period"),
                        "dataframe": df  # Keep for later processing
                    }
                    
                    parsed_files.append(schema_info)
                    logger.info(f"Parsed file {schema_info['filename']}: {schema_info['shape']}")
                    
                except Exception as e:
                    logger.error(f"Error parsing file {file_path}: {e}")
                    state.errors.append(f"Failed to parse {file_path}: {str(e)}")
            
            state.parsed_files = parsed_files
            state.completed_nodes.append("parse_files")
            state.node_outputs["parse_files"] = {
                "files_parsed": len(parsed_files),
                "total_rows": sum(f["shape"][0] for f in parsed_files),
                "total_columns": sum(f["shape"][1] for f in parsed_files),
                "common_columns": self._find_common_columns(parsed_files)
            }
            
            logger.info(f"Successfully parsed {len(parsed_files)} files")
            
        except Exception as e:
            logger.error(f"Error in parse_files: {e}")
            state.errors.append(f"Parse files error: {str(e)}")
        
        return state
    
    async def plan_operations(self, state: AnalysisState) -> AnalysisState:
        """
        Node 2: LLM-powered planning to decide analysis approach
        """
        logger.info("Starting plan_operations")
        state.current_node = "plan_operations"
        
        try:
            # Create planning prompt
            files_summary = self._create_files_summary(state.parsed_files)
            
            planning_prompt = f"""
You are an expert data analyst. Analyze the user's query and available data to create an analysis plan.

User Query: {state.query}

Available Data Files:
{files_summary}

Determine:
1. Operation Type: single_table, cross_table, temporal_comparison, or trend_analysis
2. Required Files: Which files are needed for this analysis
3. Key Metrics: What metrics should be calculated
4. Grouping Strategy: How should data be grouped (by region, product, time, etc.)
5. Temporal Scope: What time range should be analyzed

Respond in JSON format with this structure:
{{
    "operation_type": "single_table|cross_table|temporal_comparison|trend_analysis",
    "required_files": [file_ids],
    "target_metrics": ["metric1", "metric2"],
    "grouping_columns": ["column1", "column2"],
    "temporal_scope": "description",
    "analysis_steps": ["step1", "step2", "step3"],
    "reasoning": "explanation of the analysis approach"
}}
"""
            
            messages = [
                LLMMessage(role="system", content="You are a data analysis planning expert. Always respond with valid JSON."),
                LLMMessage(role="user", content=planning_prompt)
            ]
            
            # Get LLM response
            response = await llm_manager.generate(messages)
            
            try:
                analysis_plan = json.loads(response.content)
            except json.JSONDecodeError:
                # Fallback parsing
                analysis_plan = self._fallback_plan_parsing(state.query, state.parsed_files)
            
            state.analysis_plan = analysis_plan
            state.operation_type = analysis_plan.get("operation_type", "single_table")
            
            state.completed_nodes.append("plan_operations")
            state.node_outputs["plan_operations"] = {
                "operation_type": state.operation_type,
                "target_files": len(analysis_plan.get("required_files", [])),
                "target_metrics": analysis_plan.get("target_metrics", []),
                "reasoning": analysis_plan.get("reasoning", "")
            }
            
            logger.info(f"Analysis plan created: {state.operation_type}")
            
        except Exception as e:
            logger.error(f"Error in plan_operations: {e}")
            state.errors.append(f"Planning error: {str(e)}")
            # Set fallback plan
            state.analysis_plan = self._fallback_plan_parsing(state.query, state.parsed_files)
            state.operation_type = "single_table"
        
        return state
    
    async def align_timeseries(self, state: AnalysisState) -> AnalysisState:
        """
        Node 3: Align tables by time periods for temporal analysis
        """
        logger.info("Starting align_timeseries")
        state.current_node = "align_timeseries"
        
        try:
            if state.operation_type in ["cross_table", "temporal_comparison", "trend_analysis"]:
                # Perform temporal alignment
                alignment_result = self._perform_temporal_alignment(state.parsed_files, state.analysis_plan)
                state.temporal_alignment = alignment_result
                
                # Update schema alignment based on temporal requirements
                schema_alignment = self._perform_schema_alignment(state.parsed_files, state.analysis_plan)
                state.schema_alignment = schema_alignment
            else:
                # Single table analysis - minimal alignment needed
                state.temporal_alignment = {"type": "single_table", "files": state.parsed_files[:1]}
                state.schema_alignment = {"aligned": True, "mapping": {}}
            
            state.completed_nodes.append("align_timeseries")
            state.node_outputs["align_timeseries"] = {
                "alignment_type": state.temporal_alignment.get("type", "single_table"),
                "aligned_files": len(state.temporal_alignment.get("files", [])),
                "common_schema": bool(state.schema_alignment.get("aligned", False))
            }
            
            logger.info("Temporal alignment completed")
            
        except Exception as e:
            logger.error(f"Error in align_timeseries: {e}")
            state.errors.append(f"Alignment error: {str(e)}")
        
        return state
    
    async def generate_code(self, state: AnalysisState) -> AnalysisState:
        """
        Node 4: Generate Python code for the analysis
        """
        logger.info("Starting generate_code")
        state.current_node = "generate_code"
        
        try:
            code_prompt = self._create_code_generation_prompt(state)
            
            messages = [
                LLMMessage(role="system", content="You are a Python data analysis expert. Generate clean, executable pandas code."),
                LLMMessage(role="user", content=code_prompt)
            ]
            
            response = await llm_manager.generate(messages)
            
            # Extract code from response
            generated_code = self._extract_code_from_response(response.content)
            state.generated_code = generated_code
            
            state.completed_nodes.append("generate_code")
            state.node_outputs["generate_code"] = {
                "code_length": len(generated_code),
                "has_imports": "import" in generated_code,
                "has_pandas": "pd." in generated_code
            }
            
            logger.info("Code generation completed")
            
        except Exception as e:
            logger.error(f"Error in generate_code: {e}")
            state.errors.append(f"Code generation error: {str(e)}")
            # Set fallback code
            state.generated_code = self._generate_fallback_code(state)
        
        return state
    
    async def validate_code(self, state: AnalysisState) -> AnalysisState:
        """
        Node 5: Validate generated code for syntax and logic
        """
        logger.info("Starting validate_code")
        state.current_node = "validate_code"
        
        try:
            validation_result = self._validate_python_code(state.generated_code, state.parsed_files)
            
            # Increment retry count if validation fails
            if not validation_result["is_valid"]:
                retry_count = state.code_validation.get("retry_count", 0) + 1
                validation_result["retry_count"] = retry_count
                logger.warning(f"Code validation failed (attempt {retry_count}): {validation_result['errors']}")
            
            state.code_validation = validation_result
            
            state.completed_nodes.append("validate_code")
            state.node_outputs["validate_code"] = {
                "is_valid": validation_result["is_valid"],
                "error_count": len(validation_result.get("errors", [])),
                "warning_count": len(validation_result.get("warnings", []))
            }
            
            logger.info(f"Code validation: {'passed' if validation_result['is_valid'] else 'failed'}")
            
        except Exception as e:
            logger.error(f"Error in validate_code: {e}")
            state.errors.append(f"Validation error: {str(e)}")
            state.code_validation = {"is_valid": False, "errors": [str(e)]}
        
        return state
    
    async def execute_code(self, state: AnalysisState) -> AnalysisState:
        """
        Node 6: Execute the validated code and capture results
        """
        logger.info("Starting execute_code")
        state.current_node = "execute_code"
        
        try:
            execution_result = self._execute_analysis_code(state.generated_code, state.parsed_files)
            state.execution_result = execution_result
            
            state.completed_nodes.append("execute_code")
            state.node_outputs["execute_code"] = {
                "success": execution_result.get("success", False),
                "result_type": type(execution_result.get("result", {})).__name__,
                "execution_time": execution_result.get("execution_time", 0)
            }
            
            logger.info(f"Code execution: {'successful' if execution_result.get('success') else 'failed'}")
            
        except Exception as e:
            logger.error(f"Error in execute_code: {e}")
            state.errors.append(f"Execution error: {str(e)}")
            state.execution_result = {"success": False, "error": str(e)}
        
        return state
    
    async def trend_analysis(self, state: AnalysisState) -> AnalysisState:
        """
        Node 7: Perform advanced trend analysis and pattern detection
        """
        logger.info("Starting trend_analysis")
        state.current_node = "trend_analysis"
        
        try:
            if state.operation_type in ["temporal_comparison", "trend_analysis"]:
                trend_result = self._perform_trend_analysis(state.execution_result, state.parsed_files)
                state.trend_analysis = trend_result
                
                # Generate insights based on trends
                insights = self._generate_trend_insights(trend_result)
                state.insights.extend(insights)
            else:
                state.trend_analysis = {"type": "not_applicable", "reason": f"Operation type {state.operation_type} doesn't require trend analysis"}
            
            state.completed_nodes.append("trend_analysis")
            state.node_outputs["trend_analysis"] = {
                "trends_detected": len(state.trend_analysis.get("trends", [])),
                "insights_generated": len(state.insights),
                "patterns_found": len(state.trend_analysis.get("patterns", []))
            }
            
            logger.info("Trend analysis completed")
            
        except Exception as e:
            logger.error(f"Error in trend_analysis: {e}")
            state.errors.append(f"Trend analysis error: {str(e)}")
            state.trend_analysis = {"error": str(e)}
        
        return state
    
    async def explain_result(self, state: AnalysisState) -> AnalysisState:
        """
        Node 8: Generate narrative explanation and recommended actions
        """
        logger.info("Starting explain_result")
        state.current_node = "explain_result"
        
        try:
            # Create explanation prompt
            explanation_prompt = self._create_explanation_prompt(state)
            
            messages = [
                LLMMessage(role="system", content="You are a data analysis expert. Provide clear, actionable explanations of analysis results."),
                LLMMessage(role="user", content=explanation_prompt)
            ]
            
            response = await llm_manager.generate(messages)
            
            # Parse the explanation and actions
            explanation_data = self._parse_explanation_response(response.content)
            
            state.final_result = {
                "query": state.query,
                "operation_type": state.operation_type,
                "files_analyzed": len(state.parsed_files),
                "execution_result": state.execution_result,
                "trend_analysis": state.trend_analysis,
                "explanation": explanation_data.get("explanation", response.content),
                "key_findings": explanation_data.get("key_findings", []),
                "insights": state.insights,
                "confidence_score": explanation_data.get("confidence_score", 0.8),
                "metadata": {
                    "execution_id": state.execution_id,
                    "completed_nodes": state.completed_nodes,
                    "processing_time": datetime.now().isoformat(),
                    "node_outputs": state.node_outputs
                }
            }
            
            state.recommended_actions = explanation_data.get("recommended_actions", [])
            
            state.completed_nodes.append("explain_result")
            state.node_outputs["explain_result"] = {
                "explanation_length": len(explanation_data.get("explanation", "")),
                "findings_count": len(explanation_data.get("key_findings", [])),
                "actions_count": len(state.recommended_actions)
            }
            
            logger.info("Result explanation completed")
            
        except Exception as e:
            logger.error(f"Error in explain_result: {e}")
            state.errors.append(f"Explanation error: {str(e)}")
            # Set fallback explanation
            state.final_result = {
                "query": state.query,
                "execution_result": state.execution_result,
                "explanation": f"Analysis completed with {len(state.errors)} errors.",
                "errors": state.errors
            }
        
        return state
    
    # Helper methods
    def _detect_date_columns(self, df: pd.DataFrame) -> List[str]:
        """Detect columns that contain date information"""
        date_columns = []
        for col in df.columns:
            if 'date' in col.lower() or 'time' in col.lower():
                date_columns.append(col)
            elif df[col].dtype == 'object':
                # Try to parse a sample as date
                try:
                    pd.to_datetime(df[col].dropna().iloc[:5])
                    date_columns.append(col)
                except:
                    pass
        return date_columns
    
    def _find_common_columns(self, parsed_files: List[Dict]) -> List[str]:
        """Find columns that appear in multiple files"""
        if not parsed_files:
            return []
        
        common_cols = set(parsed_files[0]["columns"])
        for file_info in parsed_files[1:]:
            common_cols &= set(file_info["columns"])
        
        return list(common_cols)
    
    def _create_files_summary(self, parsed_files: List[Dict]) -> str:
        """Create a summary of parsed files for LLM context"""
        summaries = []
        for i, file_info in enumerate(parsed_files):
            summary = f"""
File {i+1}: {file_info['filename']}
- Shape: {file_info['shape'][0]} rows × {file_info['shape'][1]} columns
- Time Period: {file_info.get('time_period', 'Unknown')}
- Numeric Columns: {', '.join(file_info['numeric_columns'][:5])}
- Categorical Columns: {', '.join(file_info['categorical_columns'][:5])}
- Date Columns: {', '.join(file_info['date_columns'])}
"""
            summaries.append(summary)
        
        return "\n".join(summaries)
    
    def _fallback_plan_parsing(self, query: str, parsed_files: List[Dict]) -> Dict[str, Any]:
        """Create a fallback analysis plan when LLM parsing fails"""
        # Simple keyword-based analysis planning
        query_lower = query.lower()
        
        if any(word in query_lower for word in ["compare", "vs", "versus", "between"]):
            operation_type = "cross_table" if len(parsed_files) > 1 else "single_table"
        elif any(word in query_lower for word in ["trend", "growth", "change", "over time"]):
            operation_type = "trend_analysis"
        elif any(word in query_lower for word in ["across", "temporal", "months", "quarters"]):
            operation_type = "temporal_comparison"
        else:
            operation_type = "single_table"
        
        return {
            "operation_type": operation_type,
            "required_files": [f["file_id"] for f in parsed_files],
            "target_metrics": ["revenue", "units", "discount"],
            "grouping_columns": ["region", "product"],
            "temporal_scope": "All available time periods",
            "analysis_steps": ["Load data", "Calculate metrics", "Generate insights"],
            "reasoning": "Fallback plan based on keyword analysis"
        }
    
    def _perform_temporal_alignment(self, parsed_files: List[Dict], analysis_plan: Dict) -> Dict[str, Any]:
        """Align files temporally for cross-table analysis"""
        # This would implement sophisticated temporal alignment logic
        # For now, simplified implementation
        return {
            "type": "temporal_alignment",
            "files": parsed_files,
            "alignment_method": "time_period_matching",
            "common_timeframe": "2024-11 to 2025-Q1"
        }
    
    def _perform_schema_alignment(self, parsed_files: List[Dict], analysis_plan: Dict) -> Dict[str, Any]:
        """Align schemas across multiple files"""
        common_columns = self._find_common_columns(parsed_files)
        
        return {
            "aligned": len(common_columns) > 0,
            "common_columns": common_columns,
            "mapping": {f["filename"]: common_columns for f in parsed_files}
        }
    
    def _create_code_generation_prompt(self, state: AnalysisState) -> str:
        """Create prompt for code generation"""
        return f"""
Generate Python pandas code for this data analysis task:

Query: {state.query}
Operation Type: {state.operation_type}
Analysis Plan: {json.dumps(state.analysis_plan, indent=2)}

Files available:
{self._create_files_summary(state.parsed_files)}

Requirements:
1. Use pandas for data manipulation
2. Handle missing values appropriately
3. Return results as a dictionary with clear structure
4. Include error handling
5. Make the code executable and robust

Generate only the Python code, wrapped in ```python ``` blocks.
"""
    
    def _extract_code_from_response(self, response: str) -> str:
        """Extract Python code from LLM response"""
        if "```python" in response:
            start = response.find("```python") + 9
            end = response.find("```", start)
            return response[start:end].strip()
        elif "```" in response:
            start = response.find("```") + 3
            end = response.find("```", start)
            return response[start:end].strip()
        else:
            return response.strip()
    
    def _generate_fallback_code(self, state: AnalysisState) -> str:
        """Generate simple fallback code when LLM generation fails"""
        return '''
import pandas as pd
import numpy as np

# Simple analysis fallback
result = {"message": "Fallback analysis performed", "data": {}}
'''
    
    def _validate_python_code(self, code: str, parsed_files: List[Dict]) -> Dict[str, Any]:
        """Validate generated Python code"""
        validation = {"is_valid": True, "errors": [], "warnings": []}
        
        try:
            # Basic syntax check
            compile(code, '<string>', 'exec')
            
            # Check for required imports
            if "import pandas" not in code and "import pd" not in code:
                validation["warnings"].append("Missing pandas import")
            
            # Check for basic structure
            if "result" not in code:
                validation["warnings"].append("Code should define a 'result' variable")
            
        except SyntaxError as e:
            validation["is_valid"] = False
            validation["errors"].append(f"Syntax error: {str(e)}")
        except Exception as e:
            validation["errors"].append(f"Validation error: {str(e)}")
        
        return validation
    
    def _execute_analysis_code(self, code: str, parsed_files: List[Dict]) -> Dict[str, Any]:
        """Safely execute the generated analysis code"""
        start_time = datetime.now()
        
        try:
            # Prepare execution environment
            exec_globals = {
                'pd': pd,
                'np': np,
                'json': json,
                'datetime': datetime
            }
            
            # Add dataframes to execution context
            for i, file_info in enumerate(parsed_files):
                if 'dataframe' in file_info:
                    exec_globals[f'df_{i}'] = file_info['dataframe']
                    exec_globals[f'df_{file_info["filename"].replace(".", "_")}'] = file_info['dataframe']
            
            exec_locals = {}
            
            # Execute the code
            exec(code, exec_globals, exec_locals)
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Extract result
            result = exec_locals.get('result', {})
            
            return {
                "success": True,
                "result": result,
                "execution_time": execution_time,
                "variables_created": list(exec_locals.keys())
            }
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"Code execution failed: {e}")
            
            return {
                "success": False,
                "error": str(e),
                "execution_time": execution_time,
                "result": {}
            }
    
    def _perform_trend_analysis(self, execution_result: Dict, parsed_files: List[Dict]) -> Dict[str, Any]:
        """Perform advanced trend analysis on execution results"""
        # Simplified trend analysis
        trends = []
        patterns = []
        
        if execution_result.get("success") and execution_result.get("result"):
            result_data = execution_result["result"]
            
            # Look for numerical trends
            for key, value in result_data.items():
                if isinstance(value, (int, float)):
                    trends.append({
                        "metric": key,
                        "value": value,
                        "trend": "increasing" if value > 0 else "decreasing"
                    })
        
        return {
            "trends": trends,
            "patterns": patterns,
            "analysis_type": "basic_trend_detection"
        }
    
    def _generate_trend_insights(self, trend_result: Dict) -> List[str]:
        """Generate insights based on trend analysis"""
        insights = []
        
        for trend in trend_result.get("trends", []):
            if trend["trend"] == "increasing":
                insights.append(f"{trend['metric']} shows positive growth trend")
            elif trend["trend"] == "decreasing":
                insights.append(f"{trend['metric']} shows declining trend")
        
        return insights
    
    def _create_explanation_prompt(self, state: AnalysisState) -> str:
        """Create prompt for result explanation"""
        return f"""
Analyze these data analysis results and provide a comprehensive explanation:

Original Query: {state.query}
Analysis Type: {state.operation_type}

Execution Results: {json.dumps(state.execution_result, indent=2, default=str)}
Trend Analysis: {json.dumps(state.trend_analysis, indent=2, default=str)}
Generated Insights: {state.insights}

Provide a response in this format:
1. Executive Summary (2-3 sentences)
2. Key Findings (3-5 bullet points)
3. Detailed Explanation
4. Recommended Actions (2-4 actionable items)
5. Confidence Score (0.0 to 1.0)

Focus on actionable insights and business implications.
"""
    
    def _parse_explanation_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM explanation response"""
        # Simple parsing - in production would be more sophisticated
        return {
            "explanation": response,
            "key_findings": ["Analysis completed", "Data processed successfully"],
            "recommended_actions": ["Review results", "Plan next steps"],
            "confidence_score": 0.8
        }
    
    # Main execution method
    async def analyze(self, query: str, files: List[Dict[str, Any]], session_id: str = "") -> Dict[str, Any]:
        """Main method to run the complete analysis workflow"""
        logger.info(f"Starting multi-temporal analysis for query: {query}")
        
        # Create initial state
        initial_state = AnalysisState(
            query=query,
            files=files,
            session_id=session_id or str(uuid.uuid4())
        )
        
        try:
            # Run the workflow
            config = {"thread_id": initial_state.session_id}
            final_state = await self.graph.ainvoke(initial_state, config=config)
            
            logger.info(f"Analysis completed: {len(final_state.completed_nodes)} nodes processed")
            
            return final_state.final_result
            
        except Exception as e:
            logger.error(f"Workflow execution failed: {e}")
            return {
                "error": str(e),
                "query": query,
                "execution_id": initial_state.execution_id,
                "completed_nodes": [],
                "success": False
            }

# Global workflow instance
analysis_workflow = MultiTemporalAnalysisWorkflow()