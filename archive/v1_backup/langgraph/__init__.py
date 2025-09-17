"""
LangGraph Module for Historical Multi-Table Data Analysis
Version 2 - Advanced Query Processing with LLM Integration
"""

from .workflows.data_analysis_workflow import DataAnalysisWorkflow
from .nodes import (
    ParseQueryNode,
    AnalyzeIntentNode,
    RetrieveContextNode,
    PlanAnalysisNode,
    AlignTimeseriesNode,
    GenerateCodeNode,
    ValidateCodeNode,
    ExecuteCodeNode,
    TrendAnalysisNode,
    ExplainResultNode
)

__version__ = "2.0.0"
__all__ = [
    "DataAnalysisWorkflow",
    "ParseQueryNode", 
    "AnalyzeIntentNode",
    "RetrieveContextNode",
    "PlanAnalysisNode",
    "AlignTimeseriesNode",
    "GenerateCodeNode",
    "ValidateCodeNode",
    "ExecuteCodeNode",
    "TrendAnalysisNode",
    "ExplainResultNode",
]
