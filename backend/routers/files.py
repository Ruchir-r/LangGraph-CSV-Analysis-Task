"""
File Upload and Management Router
Version 1 - Basic CSV file handling
"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path
import pandas as pd
import uuid
import shutil
from typing import Dict, Any

from app.database import FileModel

router = APIRouter()

UPLOAD_DIR = Path("uploads")
ALLOWED_EXTENSIONS = {".csv", ".xlsx", ".xls"}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

def analyze_dataframe(df: pd.DataFrame) -> Dict[str, Any]:
    """Analyze DataFrame to categorize columns"""
    numeric_columns = df.select_dtypes(include=['number']).columns.tolist()
    
    # Detect date columns (simple heuristic)
    date_columns = []
    for col in df.columns:
        if 'date' in col.lower() or 'time' in col.lower():
            date_columns.append(col)
    
    # Categorical columns (excluding numeric and date)
    categorical_columns = [
        col for col in df.columns 
        if col not in numeric_columns and col not in date_columns
    ]
    
    return {
        "numeric_columns": numeric_columns,
        "categorical_columns": categorical_columns,
        "date_columns": date_columns,
        "total_columns": len(df.columns),
        "total_rows": len(df)
    }

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload and process CSV/Excel file"""
    
    # Validate file extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type {file_ext} not allowed. Supported: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Generate unique filename
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = UPLOAD_DIR / unique_filename
    
    try:
        # Save uploaded file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        file_size = file_path.stat().st_size
        
        # Validate file size
        if file_size > MAX_FILE_SIZE:
            file_path.unlink()  # Delete the file
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Maximum size: {MAX_FILE_SIZE // (1024*1024)}MB"
            )
        
        # Read and analyze the file
        if file_ext == ".csv":
            df = pd.read_csv(file_path)
        else:  # Excel files
            df = pd.read_excel(file_path)
        
        # Analyze the data
        analysis = analyze_dataframe(df)
        
        # Store file metadata in database
        file_id = FileModel.create(
            filename=unique_filename,
            original_filename=file.filename,
            file_path=str(file_path),
            file_size=file_size,
            columns=df.columns.tolist(),
            row_count=len(df),
            numeric_columns=analysis["numeric_columns"],
            categorical_columns=analysis["categorical_columns"],
            date_columns=analysis["date_columns"]
        )
        
        # Handle NaN values for JSON compliance
        preview_data = df.head(5).fillna("null").to_dict(orient="records")
        
        return {
            "file_id": file_id,
            "filename": file.filename,
            "file_size": file_size,
            "columns": df.columns.tolist(),
            "row_count": len(df),
            "analysis": analysis,
            "preview": preview_data,
            "message": f"File '{file.filename}' uploaded successfully!"
        }
        
    except pd.errors.EmptyDataError:
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(status_code=400, detail="The uploaded file is empty or corrupted")
    except pd.errors.ParserError as e:
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(status_code=400, detail=f"Error parsing file: {str(e)}")
    except Exception as e:
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@router.get("/{file_id}/preview")
async def get_file_preview(file_id: int, rows: int = 10):
    """Get preview of uploaded file"""
    
    file_info = FileModel.get_by_id(file_id)
    if not file_info:
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        file_path = Path(file_info["file_path"])
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File data not found")
        
        # Read file based on extension
        file_ext = file_path.suffix.lower()
        if file_ext == ".csv":
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)
        
        # Return preview data with NaN handling
        preview_data = df.head(rows).fillna("null").to_dict(orient="records")
        
        return {
            "file_id": file_id,
            "filename": file_info["original_filename"],
            "columns": file_info["columns"],
            "row_count": file_info["row_count"],
            "numeric_columns": file_info["numeric_columns"],
            "categorical_columns": file_info["categorical_columns"],
            "date_columns": file_info["date_columns"],
            "preview_data": preview_data,
            "preview_rows": len(preview_data)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading file: {str(e)}")

@router.get("/")
async def list_files():
    """List all uploaded files"""
    files = FileModel.get_all()
    return {
        "files": files,
        "count": len(files)
    }

@router.get("/{file_id}/schema")
async def get_file_schema(file_id: int):
    """Get detailed schema information for a file"""
    
    file_info = FileModel.get_by_id(file_id)
    if not file_info:
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        file_path = Path(file_info["file_path"])
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File data not found")
        
        # Read file to get detailed schema
        file_ext = file_path.suffix.lower()
        if file_ext == ".csv":
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)
        
        # Generate detailed schema information
        schema_info = {}
        for column in df.columns:
            col_info = {
                "dtype": str(df[column].dtype),
                "null_count": int(df[column].isnull().sum()),
                "unique_count": int(df[column].nunique()),
                "sample_values": df[column].dropna().head(3).tolist()
            }
            
            # Add statistics for numeric columns
            if df[column].dtype in ['int64', 'float64']:
                # Handle NaN values in statistics
                import math
                stats = {
                    "min": df[column].min(),
                    "max": df[column].max(), 
                    "mean": df[column].mean(),
                    "std": df[column].std()
                }
                
                # Convert NaN to None for JSON compliance
                for key, value in stats.items():
                    if pd.isna(value) or (isinstance(value, float) and math.isnan(value)):
                        stats[key] = None
                    else:
                        stats[key] = float(value)
                
                col_info.update(stats)
            
            schema_info[column] = col_info
        
        return {
            "file_id": file_id,
            "filename": file_info["original_filename"],
            "schema": schema_info,
            "summary": {
                "total_rows": len(df),
                "total_columns": len(df.columns),
                "numeric_columns": file_info["numeric_columns"],
                "categorical_columns": file_info["categorical_columns"],
                "date_columns": file_info["date_columns"]
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing file schema: {str(e)}")
