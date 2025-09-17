"""
Analytics Router
Version 2 - Enhanced analytics with LangGraph integration and multi-temporal support
Maintains backward compatibility with V1 endpoints
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from pathlib import Path
import pandas as pd
from typing import Optional, Dict, Any

from app.database import FileModel

router = APIRouter()

class AnalyticsRequest(BaseModel):
    file_id: int
    operation: str  # mean, sum, count, max, min
    column: str
    group_by: Optional[str] = None

def perform_basic_analytics(df: pd.DataFrame, operation: str, column: str, group_by: Optional[str] = None) -> Dict[str, Any]:
    """Perform basic analytics operations"""
    
    if column not in df.columns:
        raise ValueError(f"Column '{column}' not found in data")
    
    try:
        if group_by:
            if group_by not in df.columns:
                raise ValueError(f"Group by column '{group_by}' not found in data")
            
            # Group by operation
            grouped = df.groupby(group_by)[column]
            
            if operation == "mean":
                result = grouped.mean()
            elif operation == "sum":
                result = grouped.sum()
            elif operation == "count":
                result = grouped.count()
            elif operation == "max":
                result = grouped.max()
            elif operation == "min":
                result = grouped.min()
            else:
                raise ValueError(f"Unsupported operation: {operation}")
            
            # Convert to dictionary for JSON response
            result_dict = result.to_dict()
            
            return {
                "operation": operation,
                "column": column,
                "group_by": group_by,
                "results": result_dict,
                "summary": {
                    "total_groups": len(result_dict),
                    "operation_performed": f"{operation} of {column} grouped by {group_by}"
                }
            }
        
        else:
            # Single column operation
            import math
            
            if operation == "mean":
                result = df[column].mean()
            elif operation == "sum":
                result = df[column].sum()
            elif operation == "count":
                result = int(df[column].count())
            elif operation == "max":
                result = df[column].max()
            elif operation == "min":
                result = df[column].min()
            else:
                raise ValueError(f"Unsupported operation: {operation}")
            
            # Handle NaN results for JSON compliance
            if operation != "count":
                if pd.isna(result) or (isinstance(result, float) and math.isnan(result)):
                    result = None
                else:
                    result = float(result)
            
            return {
                "operation": operation,
                "column": column,
                "result": result,
                "summary": {
                    "operation_performed": f"{operation} of {column}",
                    "total_rows_processed": len(df)
                }
            }
    
    except Exception as e:
        raise ValueError(f"Error performing {operation} on {column}: {str(e)}")

@router.post("/basic")
async def basic_analytics(request: AnalyticsRequest):
    """Perform basic analytics operations"""
    
    # Validate operation
    allowed_operations = ["mean", "sum", "count", "max", "min"]
    if request.operation not in allowed_operations:
        raise HTTPException(
            status_code=400,
            detail=f"Operation '{request.operation}' not supported. Allowed: {', '.join(allowed_operations)}"
        )
    
    # Get file information
    file_info = FileModel.get_by_id(request.file_id)
    if not file_info:
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        # Load the data
        file_path = Path(file_info["file_path"])
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File data not found")
        
        # Read file based on extension
        file_ext = file_path.suffix.lower()
        if file_ext == ".csv":
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)
        
        # Perform analytics
        result = perform_basic_analytics(df, request.operation, request.column, request.group_by)
        
        return {
            "file_id": request.file_id,
            "filename": file_info["original_filename"],
            "analytics": result,
            "timestamp": pd.Timestamp.now().isoformat()
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error performing analytics: {str(e)}")

@router.get("/operations")
async def get_available_operations():
    """Get list of available analytics operations"""
    return {
        "operations": [
            {
                "name": "mean",
                "description": "Calculate average/mean of numeric column",
                "supports_groupby": True,
                "numeric_only": True
            },
            {
                "name": "sum", 
                "description": "Calculate sum of numeric column",
                "supports_groupby": True,
                "numeric_only": True
            },
            {
                "name": "count",
                "description": "Count non-null values in column",
                "supports_groupby": True,
                "numeric_only": False
            },
            {
                "name": "max",
                "description": "Find maximum value in column",
                "supports_groupby": True,
                "numeric_only": False
            },
            {
                "name": "min",
                "description": "Find minimum value in column",
                "supports_groupby": True,
                "numeric_only": False
            }
        ]
    }

@router.get("/summary/{file_id}")
async def get_file_summary(file_id: int):
    """Get comprehensive summary statistics for a file"""
    
    file_info = FileModel.get_by_id(file_id)
    if not file_info:
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        file_path = Path(file_info["file_path"])
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File data not found")
        
        # Read file
        file_ext = file_path.suffix.lower()
        if file_ext == ".csv":
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)
        
        # Generate comprehensive summary
        summary = {
            "file_info": {
                "filename": file_info["original_filename"],
                "rows": len(df),
                "columns": len(df.columns)
            },
            "column_summaries": {},
            "missing_data": {},
            "data_types": {}
        }
        
        # Analyze each column
        for column in df.columns:
            col_summary = {
                "dtype": str(df[column].dtype),
                "null_count": int(df[column].isnull().sum()),
                "unique_values": int(df[column].nunique()),
                "sample_values": df[column].dropna().head(3).tolist()
            }
            
            # Add statistics for numeric columns
            if df[column].dtype in ['int64', 'float64']:
                describe_stats = df[column].describe()
                import math
                
                # Handle NaN values in statistics
                stats = {
                    "min": describe_stats['min'],
                    "max": describe_stats['max'],
                    "mean": describe_stats['mean'],
                    "std": describe_stats['std'],
                    "q25": describe_stats['25%'],
                    "q50": describe_stats['50%'],
                    "q75": describe_stats['75%']
                }
                
                # Convert NaN to None for JSON compliance
                for key, value in stats.items():
                    if pd.isna(value) or (isinstance(value, float) and math.isnan(value)):
                        stats[key] = None
                    else:
                        stats[key] = float(value)
                        
                col_summary.update(stats)
            
            summary["column_summaries"][column] = col_summary
            summary["missing_data"][column] = int(df[column].isnull().sum())
            summary["data_types"][column] = str(df[column].dtype)
        
        return summary
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating summary: {str(e)}")

@router.post("/compare")
async def compare_columns(file_id: int, column1: str, column2: str):
    """Compare two numeric columns"""
    
    file_info = FileModel.get_by_id(file_id)
    if not file_info:
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        file_path = Path(file_info["file_path"])
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File data not found")
        
        # Read file
        file_ext = file_path.suffix.lower()
        if file_ext == ".csv":
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)
        
        # Validate columns exist and are numeric
        for col in [column1, column2]:
            if col not in df.columns:
                raise HTTPException(status_code=400, detail=f"Column '{col}' not found")
            if df[col].dtype not in ['int64', 'float64']:
                raise HTTPException(status_code=400, detail=f"Column '{col}' is not numeric")
        
        # Calculate comparison statistics with NaN handling
        import math
        
        def safe_float_convert(value):
            if pd.isna(value) or (isinstance(value, float) and math.isnan(value)):
                return None
            return float(value)
        
        col1_stats = {
            "mean": safe_float_convert(df[column1].mean()),
            "sum": safe_float_convert(df[column1].sum()),
            "max": safe_float_convert(df[column1].max()),
            "min": safe_float_convert(df[column1].min())
        }
        
        col2_stats = {
            "mean": safe_float_convert(df[column2].mean()),
            "sum": safe_float_convert(df[column2].sum()),
            "max": safe_float_convert(df[column2].max()),
            "min": safe_float_convert(df[column2].min())
        }
        
        # Calculate differences
        mean_diff = None
        sum_diff = None
        if col1_stats["mean"] is not None and col2_stats["mean"] is not None:
            mean_diff = col1_stats["mean"] - col2_stats["mean"]
        if col1_stats["sum"] is not None and col2_stats["sum"] is not None:
            sum_diff = col1_stats["sum"] - col2_stats["sum"]
        
        correlation = safe_float_convert(df[column1].corr(df[column2])) if len(df) > 1 else None
        
        comparison = {
            "column1": column1,
            "column2": column2,
            "statistics": {
                column1: col1_stats,
                column2: col2_stats
            },
            "differences": {
                "mean_diff": mean_diff,
                "sum_diff": sum_diff,
                "correlation": correlation
            }
        }
        
        return comparison
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error comparing columns: {str(e)}")
