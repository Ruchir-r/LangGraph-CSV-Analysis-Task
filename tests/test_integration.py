"""
Integration tests for the complete LangGraph CSV Analysis workflow.
"""

import pytest
import asyncio
import pandas as pd
from unittest.mock import Mock, patch, AsyncMock
from conftest import TestDataGenerator


class TestWorkflowIntegration:
    """Test complete workflow integration."""
    
    @pytest.mark.asyncio
    async def test_parse_files_node(self, sample_csv_file):
        """Test the parse_files workflow node."""
        from langgraph_workflow import parse_files_node, AnalysisState
        
        initial_state = AnalysisState(
            query="Test query",
            files=[{"id": "test-123", "filename": sample_csv_file}],
            session_id="test-session",
            execution_id="test-exec",
            current_node="",
            completed_nodes=[],
            node_outputs={},
            errors=[],
            parsed_files=[],
            schema_aligned=False,
            common_columns=[],
            operation_type="",
            analysis_plan={},
            target_metrics=[],
            time_dimension="",
            aligned_data={},
            generated_code="",
            validated_code="",
            execution_results={},
            trends=[],
            patterns=[],
            anomalies=[],
            correlations=[],
            forecasts=[],
            statistical_tests=[],
            final_result={},
            insights=[],
            recommended_actions=[],
            confidence_score=0.0
        )
        
        with patch('app.database.FileModel') as mock_file_model:
            mock_file = Mock()
            mock_file.file_path = sample_csv_file
            mock_file_model.query.filter.return_value.first.return_value = mock_file
            
            result_state = await parse_files_node(initial_state)
            
            assert result_state["current_node"] == "parse_files"
            assert "parse_files" in result_state["completed_nodes"]
            assert len(result_state["parsed_files"]) > 0
    
    @pytest.mark.asyncio
    async def test_plan_operations_node(self, mock_openai_client):
        """Test the plan_operations workflow node."""
        from langgraph_workflow import plan_operations_node, AnalysisState
        
        initial_state = AnalysisState(
            query="Show average revenue by region",
            files=[],
            session_id="test-session",
            execution_id="test-exec",
            current_node="parse_files",
            completed_nodes=["parse_files"],
            node_outputs={},
            errors=[],
            parsed_files=[{"filename": "test.csv", "columns": ["Region", "Revenue"]}],
            schema_aligned=True,
            common_columns=["Region", "Revenue"],
            operation_type="",
            analysis_plan={},
            target_metrics=[],
            time_dimension="",
            aligned_data={},
            generated_code="",
            validated_code="",
            execution_results={},
            trends=[],
            patterns=[],
            anomalies=[],
            correlations=[],
            forecasts=[],
            statistical_tests=[],
            final_result={},
            insights=[],
            recommended_actions=[],
            confidence_score=0.0
        )
        
        with patch('services.llm_service.get_llm_service') as mock_llm_service:
            mock_service = Mock()
            mock_response = Mock()
            mock_response.content = '{"operation_type": "single_table", "analysis_plan": {"aggregation": "average"}}'
            mock_service.generate_response.return_value = mock_response
            mock_llm_service.return_value = mock_service
            
            result_state = await plan_operations_node(initial_state)
            
            assert result_state["current_node"] == "plan_operations"
            assert "plan_operations" in result_state["completed_nodes"]
            assert result_state["operation_type"] != ""
    
    @pytest.mark.asyncio
    async def test_generate_code_node(self, mock_openai_client):
        """Test the generate_code workflow node."""
        from langgraph_workflow import generate_code_node, AnalysisState
        
        initial_state = AnalysisState(
            query="Show average revenue by region",
            files=[],
            session_id="test-session",
            execution_id="test-exec",
            current_node="align_timeseries",
            completed_nodes=["parse_files", "plan_operations", "align_timeseries"],
            node_outputs={},
            errors=[],
            parsed_files=[{"filename": "test.csv", "dataframe": pd.DataFrame({"Region": ["APAC", "EU"], "Revenue": [1000, 2000]})}],
            schema_aligned=True,
            common_columns=["Region", "Revenue"],
            operation_type="single_table",
            analysis_plan={"aggregation": "average"},
            target_metrics=["Revenue"],
            time_dimension="",
            aligned_data={},
            generated_code="",
            validated_code="",
            execution_results={},
            trends=[],
            patterns=[],
            anomalies=[],
            correlations=[],
            forecasts=[],
            statistical_tests=[],
            final_result={},
            insights=[],
            recommended_actions=[],
            confidence_score=0.0
        )
        
        with patch('services.llm_service.get_llm_service') as mock_llm_service:
            mock_service = Mock()
            mock_response = Mock()
            mock_response.content = "df.groupby('Region')['Revenue'].mean()"
            mock_service.generate_response.return_value = mock_response
            mock_llm_service.return_value = mock_service
            
            result_state = await generate_code_node(initial_state)
            
            assert result_state["current_node"] == "generate_code"
            assert "generate_code" in result_state["completed_nodes"]
            assert result_state["generated_code"] != ""
    
    @pytest.mark.asyncio
    async def test_complete_workflow_flow(self, sample_csv_file, mock_openai_client):
        """Test complete workflow from start to finish."""
        from langgraph_workflow import create_workflow_graph, AnalysisState
        
        initial_state = AnalysisState(
            query="Show average revenue by region",
            files=[{"id": "test-123", "filename": sample_csv_file}],
            session_id="test-session",
            execution_id="test-exec",
            current_node="",
            completed_nodes=[],
            node_outputs={},
            errors=[],
            parsed_files=[],
            schema_aligned=False,
            common_columns=[],
            operation_type="",
            analysis_plan={},
            target_metrics=[],
            time_dimension="",
            aligned_data={},
            generated_code="",
            validated_code="",
            execution_results={},
            trends=[],
            patterns=[],
            anomalies=[],
            correlations=[],
            forecasts=[],
            statistical_tests=[],
            final_result={},
            insights=[],
            recommended_actions=[],
            confidence_score=0.0
        )
        
        with patch('services.llm_service.get_llm_service') as mock_llm_service:
            mock_service = Mock()
            mock_response = Mock()
            mock_response.content = '{"operation_type": "single_table"}'
            mock_service.generate_response.return_value = mock_response
            mock_llm_service.return_value = mock_service
            
            with patch('app.database.FileModel') as mock_file_model:
                mock_file = Mock()
                mock_file.file_path = sample_csv_file
                mock_file_model.query.filter.return_value.first.return_value = mock_file
                
                workflow = create_workflow_graph()
                compiled_workflow = workflow.compile()
                
                states = []
                async for state in compiled_workflow.astream(initial_state):
                    states.append(state)
                
                # Should have progressed through multiple workflow nodes
                assert len(states) > 1
                final_state = states[-1]
                assert len(final_state["completed_nodes"]) > 0


class TestMultiFileAnalysis:
    """Test multi-file analysis scenarios."""
    
    @pytest.mark.asyncio
    async def test_temporal_alignment(self):
        """Test temporal data alignment across multiple files."""
        from langgraph_workflow import align_timeseries_node, AnalysisState
        
        # Create multi-month test data
        data_nov = TestDataGenerator.create_multi_month_data()
        data_nov = data_nov[data_nov['Date'].str.contains('2024-11')]
        
        data_dec = TestDataGenerator.create_multi_month_data()
        data_dec = data_dec[data_dec['Date'].str.contains('2024-12')]
        
        initial_state = AnalysisState(
            query="Compare revenue across Nov and Dec 2024",
            files=[],
            session_id="test-session",
            execution_id="test-exec",
            current_node="plan_operations",
            completed_nodes=["parse_files", "plan_operations"],
            node_outputs={},
            errors=[],
            parsed_files=[
                {"filename": "nov_2024.csv", "dataframe": data_nov},
                {"filename": "dec_2024.csv", "dataframe": data_dec}
            ],
            schema_aligned=True,
            common_columns=["Region", "Revenue", "Date"],
            operation_type="cross_table",
            analysis_plan={"temporal_comparison": True},
            target_metrics=["Revenue"],
            time_dimension="month",
            aligned_data={},
            generated_code="",
            validated_code="",
            execution_results={},
            trends=[],
            patterns=[],
            anomalies=[],
            correlations=[],
            forecasts=[],
            statistical_tests=[],
            final_result={},
            insights=[],
            recommended_actions=[],
            confidence_score=0.0
        )
        
        with patch('services.llm_service.get_llm_service') as mock_llm_service:
            mock_service = Mock()
            mock_response = Mock()
            mock_response.content = '{"alignment_strategy": "monthly_aggregation"}'
            mock_service.generate_response.return_value = mock_response
            mock_llm_service.return_value = mock_service
            
            result_state = await align_timeseries_node(initial_state)
            
            assert result_state["current_node"] == "align_timeseries"
            assert "align_timeseries" in result_state["completed_nodes"]
            assert result_state["time_dimension"] == "month"
    
    def test_cross_table_operations(self):
        """Test cross-table data operations."""
        # Create test data with different schemas
        sales_data = pd.DataFrame({
            'Order_ID': ['ORD001', 'ORD002'],
            'Customer_ID': ['CUST001', 'CUST002'],
            'Revenue': [1000, 2000]
        })
        
        customer_data = pd.DataFrame({
            'Customer_ID': ['CUST001', 'CUST002'],
            'Region': ['APAC', 'EU'],
            'Segment': ['Enterprise', 'SMB']
        })
        
        # Test data alignment and merging logic
        merged_data = sales_data.merge(customer_data, on='Customer_ID', how='left')
        
        assert len(merged_data) == 2
        assert 'Region' in merged_data.columns
        assert 'Revenue' in merged_data.columns


class TestErrorHandling:
    """Test error handling in workflow."""
    
    @pytest.mark.asyncio
    async def test_invalid_csv_handling(self, tmp_path):
        """Test handling of invalid CSV files."""
        from langgraph_workflow import parse_files_node, AnalysisState
        
        # Create invalid CSV file
        invalid_csv = tmp_path / "invalid.csv"
        invalid_csv.write_text("invalid,csv,content\nwith,malformed\ndata")
        
        initial_state = AnalysisState(
            query="Test query",
            files=[{"id": "test-123", "filename": str(invalid_csv)}],
            session_id="test-session",
            execution_id="test-exec",
            current_node="",
            completed_nodes=[],
            node_outputs={},
            errors=[],
            parsed_files=[],
            schema_aligned=False,
            common_columns=[],
            operation_type="",
            analysis_plan={},
            target_metrics=[],
            time_dimension="",
            aligned_data={},
            generated_code="",
            validated_code="",
            execution_results={},
            trends=[],
            patterns=[],
            anomalies=[],
            correlations=[],
            forecasts=[],
            statistical_tests=[],
            final_result={},
            insights=[],
            recommended_actions=[],
            confidence_score=0.0
        )
        
        with patch('app.database.FileModel') as mock_file_model:
            mock_file = Mock()
            mock_file.file_path = str(invalid_csv)
            mock_file_model.query.filter.return_value.first.return_value = mock_file
            
            result_state = await parse_files_node(initial_state)
            
            # Should handle error gracefully
            assert len(result_state.get("errors", [])) > 0 or len(result_state.get("parsed_files", [])) == 0
    
    @pytest.mark.asyncio
    async def test_llm_service_failure(self):
        """Test handling of LLM service failures."""
        from langgraph_workflow import plan_operations_node, AnalysisState
        
        initial_state = AnalysisState(
            query="Test query",
            files=[],
            session_id="test-session",
            execution_id="test-exec",
            current_node="parse_files",
            completed_nodes=["parse_files"],
            node_outputs={},
            errors=[],
            parsed_files=[{"filename": "test.csv", "columns": ["Column1"]}],
            schema_aligned=True,
            common_columns=["Column1"],
            operation_type="",
            analysis_plan={},
            target_metrics=[],
            time_dimension="",
            aligned_data={},
            generated_code="",
            validated_code="",
            execution_results={},
            trends=[],
            patterns=[],
            anomalies=[],
            correlations=[],
            forecasts=[],
            statistical_tests=[],
            final_result={},
            insights=[],
            recommended_actions=[],
            confidence_score=0.0
        )
        
        with patch('services.llm_service.get_llm_service') as mock_llm_service:
            mock_service = Mock()
            mock_service.generate_response.side_effect = Exception("LLM API Error")
            mock_llm_service.return_value = mock_service
            
            result_state = await plan_operations_node(initial_state)
            
            # Should handle LLM failure gracefully
            assert len(result_state.get("errors", [])) > 0


class TestDataProcessing:
    """Test data processing capabilities."""
    
    def test_anomaly_detection(self):
        """Test anomaly detection functionality."""
        # Create data with known anomalies
        data = TestDataGenerator.create_anomaly_data()
        
        # Test statistical anomaly detection
        revenue_mean = data['Revenue'].mean()
        revenue_std = data['Revenue'].std()
        threshold = revenue_mean + 3 * revenue_std
        
        anomalies = data[data['Revenue'] > threshold]
        
        assert len(anomalies) > 0  # Should detect the planted anomaly
        assert anomalies['Revenue'].iloc[0] == 50000  # Should detect our planted value
    
    def test_correlation_analysis(self):
        """Test correlation analysis functionality."""
        data = TestDataGenerator.create_multi_month_data()
        
        # Test correlation between discount and revenue
        correlation = data['Discount'].corr(data['Revenue'])
        
        assert isinstance(correlation, float)
        assert -1 <= correlation <= 1
    
    def test_trend_analysis(self):
        """Test trend analysis functionality."""
        data = TestDataGenerator.create_multi_month_data()
        
        # Group by date and calculate monthly revenue
        monthly_revenue = data.groupby(data['Date'].str[:7])['Revenue'].sum()
        
        # Test trend calculation (simple linear trend)
        if len(monthly_revenue) > 1:
            x = range(len(monthly_revenue))
            y = monthly_revenue.values
            
            # Calculate basic trend
            trend = (y[-1] - y[0]) / len(y)
            
            assert isinstance(trend, (int, float))


if __name__ == "__main__":
    pytest.main([__file__, "-v"])