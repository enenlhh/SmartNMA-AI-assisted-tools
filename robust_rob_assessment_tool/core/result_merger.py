"""
Result merging utilities for parallel processing.

This module handles merging results from parallel batch processing,
generating consolidated outputs, and managing result organization.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pathlib import Path
import json
import shutil
from datetime import datetime
from dataclasses import dataclass, asdict
import pandas as pd
import logging


@dataclass
class DocumentResult:
    """Represents the result of processing a single document."""
    document_name: str
    study_id: str
    assessment_results: Dict[str, Any]
    processing_time: float
    token_usage: Dict[str, Any]
    errors: List[str]


@dataclass
class BatchResult:
    """Represents the result of processing a batch of documents."""
    batch_id: str
    documents_processed: int
    documents_failed: int
    total_processing_time: float
    results: List[DocumentResult]


class ResultMergerInterface(ABC):
    """Abstract interface for result merging components."""
    
    @abstractmethod
    def merge_batch_results(self, batch_results: List[BatchResult]) -> Dict[str, Any]:
        """Merge results from multiple batches."""
        pass
    
    @abstractmethod
    def generate_output_files(self, merged_results: Dict[str, Any], output_dir: str) -> List[str]:
        """Generate output files from merged results."""
        pass


class ResultMerger:
    """
    Handles merging results from parallel batch processing.
    
    This class consolidates results from multiple parallel workers,
    generates various output formats, and manages result organization.
    """
    
    def __init__(self, output_format: str = "excel"):
        """
        Initialize the result merger.
        
        Args:
            output_format: Preferred output format (excel, json, html)
        """
        self.output_format = output_format
        self.merged_results = {}
        self.logger = logging.getLogger(__name__)
        
    def merge_batch_results(self, batch_results: List[BatchResult]) -> Dict[str, Any]:
        """
        Merge results from multiple parallel batches.
        
        Args:
            batch_results: List of batch results to merge
            
        Returns:
            Dict[str, Any]: Merged results with consolidated statistics
        """
        if not batch_results:
            return {"documents": [], "statistics": {}, "errors": []}
        
        # Collect all document results
        all_documents = []
        all_errors = []
        
        for batch in batch_results:
            all_documents.extend(batch.results)
            # Collect batch-level errors
            for doc_result in batch.results:
                all_errors.extend(doc_result.errors)
        
        # Generate consolidated statistics
        statistics = self.consolidate_statistics(batch_results)
        
        # Add token usage statistics
        token_stats = self._consolidate_token_usage(all_documents)
        statistics.update(token_stats)
        
        merged_results = {
            "documents": [asdict(doc) for doc in all_documents],
            "statistics": statistics,
            "errors": all_errors,
            "batch_count": len(batch_results),
            "merge_timestamp": datetime.now().isoformat()
        }
        
        self.merged_results = merged_results
        return merged_results
    
    def generate_excel_output(self, results: Dict[str, Any], output_path: str) -> str:
        """
        Generate Excel output file from merged results.
        
        Args:
            results: Merged results data
            output_path: Path for output file
            
        Returns:
            str: Path to generated Excel file
        """
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            # Main results sheet
            if results.get("documents"):
                df_results = self._create_results_dataframe(results["documents"])
                df_results.to_excel(writer, sheet_name='ROB_Results', index=False)
            
            # Statistics sheet
            if results.get("statistics"):
                df_stats = self._create_statistics_dataframe(results["statistics"])
                df_stats.to_excel(writer, sheet_name='Statistics', index=False)
            
            # Errors sheet
            if results.get("errors"):
                df_errors = self._create_errors_dataframe(results["errors"])
                df_errors.to_excel(writer, sheet_name='Errors', index=False)
            
            # Token usage sheet
            if results.get("statistics", {}).get("token_usage"):
                df_tokens = self._create_token_usage_dataframe(results["statistics"]["token_usage"])
                df_tokens.to_excel(writer, sheet_name='Token_Usage', index=False)
        
        self.logger.info(f"Generated Excel output: {output_file}")
        return str(output_file)
    
    def generate_html_visualization(self, results: Dict[str, Any], output_path: str) -> str:
        """
        Generate HTML visualization from merged results.
        
        Args:
            results: Merged results data
            output_path: Path for output file
            
        Returns:
            str: Path to generated HTML file
        """
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        html_content = self._generate_html_content(results)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        self.logger.info(f"Generated HTML visualization: {output_file}")
        return str(output_file)
    
    def generate_json_output(self, results: Dict[str, Any], output_path: str) -> str:
        """
        Generate JSON output file from merged results.
        
        Args:
            results: Merged results data
            output_path: Path for output file
            
        Returns:
            str: Path to generated JSON file
        """
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False, default=str)
        
        self.logger.info(f"Generated JSON output: {output_file}")
        return str(output_file)
    
    def consolidate_statistics(self, batch_results: List[BatchResult]) -> Dict[str, Any]:
        """
        Consolidate statistics from all batch results.
        
        Args:
            batch_results: List of batch results
            
        Returns:
            Dict[str, Any]: Consolidated statistics
        """
        total_processed = sum(batch.documents_processed for batch in batch_results)
        total_failed = sum(batch.documents_failed for batch in batch_results)
        total_time = sum(batch.total_processing_time for batch in batch_results)
        
        return {
            "total_documents_processed": total_processed,
            "total_documents_failed": total_failed,
            "total_processing_time": total_time,
            "success_rate": total_processed / (total_processed + total_failed) if (total_processed + total_failed) > 0 else 0,
            "average_processing_time": total_time / total_processed if total_processed > 0 else 0,
            "batch_count": len(batch_results)
        }
    
    def _consolidate_token_usage(self, documents: List[DocumentResult]) -> Dict[str, Any]:
        """Consolidate token usage statistics from all documents."""
        total_input_tokens = 0
        total_output_tokens = 0
        model_usage = {}
        
        for doc in documents:
            if doc.token_usage:
                total_input_tokens += doc.token_usage.get('input_tokens', 0)
                total_output_tokens += doc.token_usage.get('output_tokens', 0)
                
                model = doc.token_usage.get('model', 'unknown')
                if model not in model_usage:
                    model_usage[model] = {'input_tokens': 0, 'output_tokens': 0, 'documents': 0}
                
                model_usage[model]['input_tokens'] += doc.token_usage.get('input_tokens', 0)
                model_usage[model]['output_tokens'] += doc.token_usage.get('output_tokens', 0)
                model_usage[model]['documents'] += 1
        
        return {
            "token_usage": {
                "total_input_tokens": total_input_tokens,
                "total_output_tokens": total_output_tokens,
                "total_tokens": total_input_tokens + total_output_tokens,
                "model_breakdown": model_usage
            }
        }
    
    def _create_results_dataframe(self, documents: List[Dict[str, Any]]) -> pd.DataFrame:
        """Create DataFrame for main results."""
        rows = []
        
        for doc in documents:
            row = {
                'Document Name': doc.get('document_name', ''),
                'Study ID': doc.get('study_id', ''),
                'Processing Time (s)': doc.get('processing_time', 0),
                'Error Count': len(doc.get('errors', []))
            }
            
            # Add assessment results
            assessment = doc.get('assessment_results', {})
            if isinstance(assessment, dict):
                for key, value in assessment.items():
                    if isinstance(value, (str, int, float, bool)):
                        row[f'Assessment_{key}'] = value
                    elif isinstance(value, dict):
                        for sub_key, sub_value in value.items():
                            if isinstance(sub_value, (str, int, float, bool)):
                                row[f'Assessment_{key}_{sub_key}'] = sub_value
            
            # Add token usage
            token_usage = doc.get('token_usage', {})
            row['Input Tokens'] = token_usage.get('input_tokens', 0)
            row['Output Tokens'] = token_usage.get('output_tokens', 0)
            row['Model'] = token_usage.get('model', '')
            
            rows.append(row)
        
        return pd.DataFrame(rows)
    
    def _create_statistics_dataframe(self, statistics: Dict[str, Any]) -> pd.DataFrame:
        """Create DataFrame for statistics."""
        stats_data = []
        
        for key, value in statistics.items():
            if key != 'token_usage' and not isinstance(value, dict):
                stats_data.append({'Metric': key, 'Value': value})
        
        return pd.DataFrame(stats_data)
    
    def _create_errors_dataframe(self, errors: List[str]) -> pd.DataFrame:
        """Create DataFrame for errors."""
        if not errors:
            return pd.DataFrame({'Error': ['No errors recorded']})
        
        error_counts = {}
        for error in errors:
            error_counts[error] = error_counts.get(error, 0) + 1
        
        error_data = [{'Error': error, 'Count': count} for error, count in error_counts.items()]
        return pd.DataFrame(error_data)
    
    def _create_token_usage_dataframe(self, token_usage: Dict[str, Any]) -> pd.DataFrame:
        """Create DataFrame for token usage."""
        rows = []
        
        # Overall totals
        rows.append({
            'Category': 'Total',
            'Model': 'All Models',
            'Input Tokens': token_usage.get('total_input_tokens', 0),
            'Output Tokens': token_usage.get('total_output_tokens', 0),
            'Total Tokens': token_usage.get('total_tokens', 0),
            'Documents': 'N/A'
        })
        
        # Model breakdown
        model_breakdown = token_usage.get('model_breakdown', {})
        for model, usage in model_breakdown.items():
            rows.append({
                'Category': 'Model',
                'Model': model,
                'Input Tokens': usage.get('input_tokens', 0),
                'Output Tokens': usage.get('output_tokens', 0),
                'Total Tokens': usage.get('input_tokens', 0) + usage.get('output_tokens', 0),
                'Documents': usage.get('documents', 0)
            })
        
        return pd.DataFrame(rows)
    
    def _generate_html_content(self, results: Dict[str, Any]) -> str:
        """Generate HTML content for visualization."""
        statistics = results.get('statistics', {})
        documents = results.get('documents', [])
        errors = results.get('errors', [])
        
        html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ROB Assessment Results</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .header {{
            text-align: center;
            color: #333;
            border-bottom: 2px solid #007bff;
            padding-bottom: 10px;
            margin-bottom: 30px;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .stat-card {{
            background-color: #f8f9fa;
            padding: 20px;
            border-radius: 6px;
            border-left: 4px solid #007bff;
        }}
        .stat-value {{
            font-size: 2em;
            font-weight: bold;
            color: #007bff;
        }}
        .stat-label {{
            color: #666;
            margin-top: 5px;
        }}
        .section {{
            margin-bottom: 30px;
        }}
        .section h2 {{
            color: #333;
            border-bottom: 1px solid #ddd;
            padding-bottom: 5px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background-color: #007bff;
            color: white;
        }}
        tr:hover {{
            background-color: #f5f5f5;
        }}
        .error-list {{
            background-color: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 4px;
            padding: 15px;
            max-height: 300px;
            overflow-y: auto;
        }}
        .success-rate {{
            color: #28a745;
        }}
        .failure-rate {{
            color: #dc3545;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>ROB Assessment Results</h1>
            <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value">{statistics.get('total_documents_processed', 0)}</div>
                <div class="stat-label">Documents Processed</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{statistics.get('total_documents_failed', 0)}</div>
                <div class="stat-label">Documents Failed</div>
            </div>
            <div class="stat-card">
                <div class="stat-value success-rate">{statistics.get('success_rate', 0):.1%}</div>
                <div class="stat-label">Success Rate</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{statistics.get('average_processing_time', 0):.1f}s</div>
                <div class="stat-label">Avg Processing Time</div>
            </div>
        </div>
        
        {self._generate_token_usage_html(statistics.get('token_usage', {}))}
        
        <div class="section">
            <h2>Document Results Summary</h2>
            <table>
                <thead>
                    <tr>
                        <th>Document Name</th>
                        <th>Study ID</th>
                        <th>Processing Time</th>
                        <th>Errors</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
                    {self._generate_document_rows_html(documents)}
                </tbody>
            </table>
        </div>
        
        {self._generate_errors_html(errors)}
    </div>
</body>
</html>
        """
        
        return html_template
    
    def _generate_token_usage_html(self, token_usage: Dict[str, Any]) -> str:
        """Generate HTML for token usage section."""
        if not token_usage:
            return ""
        
        model_breakdown = token_usage.get('model_breakdown', {})
        model_rows = ""
        
        for model, usage in model_breakdown.items():
            model_rows += f"""
                <tr>
                    <td>{model}</td>
                    <td>{usage.get('input_tokens', 0):,}</td>
                    <td>{usage.get('output_tokens', 0):,}</td>
                    <td>{usage.get('input_tokens', 0) + usage.get('output_tokens', 0):,}</td>
                    <td>{usage.get('documents', 0)}</td>
                </tr>
            """
        
        return f"""
        <div class="section">
            <h2>Token Usage</h2>
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-value">{token_usage.get('total_input_tokens', 0):,}</div>
                    <div class="stat-label">Input Tokens</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{token_usage.get('total_output_tokens', 0):,}</div>
                    <div class="stat-label">Output Tokens</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{token_usage.get('total_tokens', 0):,}</div>
                    <div class="stat-label">Total Tokens</div>
                </div>
            </div>
            
            <h3>Model Breakdown</h3>
            <table>
                <thead>
                    <tr>
                        <th>Model</th>
                        <th>Input Tokens</th>
                        <th>Output Tokens</th>
                        <th>Total Tokens</th>
                        <th>Documents</th>
                    </tr>
                </thead>
                <tbody>
                    {model_rows}
                </tbody>
            </table>
        </div>
        """
    
    def _generate_document_rows_html(self, documents: List[Dict[str, Any]]) -> str:
        """Generate HTML rows for document results."""
        rows = ""
        for doc in documents:
            error_count = len(doc.get('errors', []))
            status = "Success" if error_count == 0 else f"Errors ({error_count})"
            status_class = "success-rate" if error_count == 0 else "failure-rate"
            
            rows += f"""
                <tr>
                    <td>{doc.get('document_name', 'Unknown')}</td>
                    <td>{doc.get('study_id', 'N/A')}</td>
                    <td>{doc.get('processing_time', 0):.1f}s</td>
                    <td>{error_count}</td>
                    <td class="{status_class}">{status}</td>
                </tr>
            """
        
        return rows
    
    def _generate_errors_html(self, errors: List[str]) -> str:
        """Generate HTML for errors section."""
        if not errors:
            return """
            <div class="section">
                <h2>Errors</h2>
                <p style="color: #28a745;">No errors recorded during processing.</p>
            </div>
            """
        
        error_list = "<br>".join(f"• {error}" for error in errors[:50])  # Limit to first 50 errors
        if len(errors) > 50:
            error_list += f"<br>... and {len(errors) - 50} more errors"
        
        return f"""
        <div class="section">
            <h2>Errors ({len(errors)} total)</h2>
            <div class="error-list">
                {error_list}
            </div>
        </div>
        """


class ResultArchiver:
    """
    Handles backup and archival mechanisms for assessment results.
    """
    
    def __init__(self, base_archive_dir: str = "archive"):
        """
        Initialize the result archiver.
        
        Args:
            base_archive_dir: Base directory for archives
        """
        self.base_archive_dir = Path(base_archive_dir)
        self.logger = logging.getLogger(__name__)
    
    def create_archive(self, session_dir: str, archive_name: Optional[str] = None) -> str:
        """
        Create an archive of assessment session results.
        
        Args:
            session_dir: Path to session directory to archive
            archive_name: Optional custom archive name
            
        Returns:
            str: Path to created archive
        """
        session_path = Path(session_dir)
        if not session_path.exists():
            raise FileNotFoundError(f"Session directory not found: {session_dir}")
        
        # Generate archive name
        if archive_name is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            archive_name = f"{session_path.name}_{timestamp}"
        
        # Create archive directory
        self.base_archive_dir.mkdir(parents=True, exist_ok=True)
        archive_path = self.base_archive_dir / archive_name
        
        # Copy session directory to archive
        shutil.copytree(session_path, archive_path, dirs_exist_ok=True)
        
        # Create archive metadata
        self._create_archive_metadata(archive_path, session_path)
        
        self.logger.info(f"Created archive: {archive_path}")
        return str(archive_path)
    
    def create_compressed_archive(self, session_dir: str, 
                                archive_name: Optional[str] = None) -> str:
        """
        Create a compressed archive of assessment session results.
        
        Args:
            session_dir: Path to session directory to archive
            archive_name: Optional custom archive name
            
        Returns:
            str: Path to created compressed archive
        """
        session_path = Path(session_dir)
        if not session_path.exists():
            raise FileNotFoundError(f"Session directory not found: {session_dir}")
        
        # Generate archive name
        if archive_name is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            archive_name = f"{session_path.name}_{timestamp}"
        
        # Create archive directory
        self.base_archive_dir.mkdir(parents=True, exist_ok=True)
        archive_path = self.base_archive_dir / f"{archive_name}.tar.gz"
        
        # Create compressed archive
        shutil.make_archive(
            str(self.base_archive_dir / archive_name),
            'gztar',
            str(session_path.parent),
            session_path.name
        )
        
        self.logger.info(f"Created compressed archive: {archive_path}")
        return str(archive_path)
    
    def restore_from_archive(self, archive_path: str, restore_dir: str) -> str:
        """
        Restore session from archive.
        
        Args:
            archive_path: Path to archive to restore
            restore_dir: Directory to restore to
            
        Returns:
            str: Path to restored session directory
        """
        archive = Path(archive_path)
        restore_path = Path(restore_dir)
        
        if not archive.exists():
            raise FileNotFoundError(f"Archive not found: {archive_path}")
        
        restore_path.mkdir(parents=True, exist_ok=True)
        
        if archive.suffix == '.gz' and archive.stem.endswith('.tar'):
            # Extract compressed archive
            shutil.unpack_archive(archive, restore_path)
            # Find the extracted directory
            extracted_dirs = [d for d in restore_path.iterdir() if d.is_dir()]
            if extracted_dirs:
                restored_session = extracted_dirs[0]
            else:
                raise RuntimeError("No directory found in extracted archive")
        else:
            # Copy uncompressed archive
            session_name = archive.name
            restored_session = restore_path / session_name
            shutil.copytree(archive, restored_session, dirs_exist_ok=True)
        
        self.logger.info(f"Restored session from archive: {restored_session}")
        return str(restored_session)
    
    def list_archives(self) -> List[Dict[str, Any]]:
        """
        List all available archives.
        
        Returns:
            List[Dict[str, Any]]: List of archive information
        """
        archives = []
        
        if not self.base_archive_dir.exists():
            return archives
        
        for archive_path in self.base_archive_dir.iterdir():
            if archive_path.is_dir() or archive_path.suffix in ['.gz', '.zip']:
                try:
                    archive_info = self._get_archive_info(archive_path)
                    archives.append(archive_info)
                except Exception as e:
                    self.logger.warning(f"Could not read archive info for {archive_path}: {e}")
        
        # Sort by creation time (newest first)
        archives.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        return archives
    
    def cleanup_old_archives(self, days_old: int = 90, 
                           keep_recent: int = 10) -> List[str]:
        """
        Clean up old archives.
        
        Args:
            days_old: Remove archives older than this many days
            keep_recent: Always keep this many most recent archives
            
        Returns:
            List[str]: List of removed archive paths
        """
        if not self.base_archive_dir.exists():
            return []
        
        # Get all archives with their creation times
        archives = []
        for archive_path in self.base_archive_dir.iterdir():
            if archive_path.is_dir() or archive_path.suffix in ['.gz', '.zip']:
                stat = archive_path.stat()
                archives.append((archive_path, stat.st_ctime))
        
        # Sort by creation time (newest first)
        archives.sort(key=lambda x: x[1], reverse=True)
        
        # Keep recent archives
        archives_to_check = archives[keep_recent:]
        
        # Remove old archives
        removed_archives = []
        cutoff_time = datetime.now().timestamp() - (days_old * 24 * 60 * 60)
        
        for archive_path, creation_time in archives_to_check:
            if creation_time < cutoff_time:
                try:
                    if archive_path.is_dir():
                        shutil.rmtree(archive_path)
                    else:
                        archive_path.unlink()
                    removed_archives.append(str(archive_path))
                    self.logger.info(f"Removed old archive: {archive_path}")
                except Exception as e:
                    self.logger.error(f"Failed to remove archive {archive_path}: {e}")
        
        return removed_archives
    
    def _create_archive_metadata(self, archive_path: Path, original_path: Path) -> None:
        """Create metadata file for the archive."""
        metadata = {
            "archive_created_at": datetime.now().isoformat(),
            "original_session_path": str(original_path),
            "original_session_name": original_path.name,
            "archive_size_bytes": sum(f.stat().st_size for f in archive_path.rglob('*') if f.is_file())
        }
        
        metadata_file = archive_path / "archive_metadata.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    def _get_archive_info(self, archive_path: Path) -> Dict[str, Any]:
        """Get information about an archive."""
        stat = archive_path.stat()
        
        info = {
            "archive_name": archive_path.name,
            "archive_path": str(archive_path),
            "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
            "modified_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "is_compressed": archive_path.suffix in ['.gz', '.zip'],
            "size_bytes": stat.st_size if archive_path.is_file() else sum(f.stat().st_size for f in archive_path.rglob('*') if f.is_file())
        }
        
        # Try to read metadata if available
        if archive_path.is_dir():
            metadata_file = archive_path / "archive_metadata.json"
            if metadata_file.exists():
                try:
                    with open(metadata_file, 'r', encoding='utf-8') as f:
                        metadata = json.load(f)
                        info.update(metadata)
                except Exception:
                    pass
        
        return info


class ConsolidatedResultManager:
    """
    High-level manager for result merging, archival, and organization.
    """
    
    def __init__(self, output_dir: str = "output", archive_dir: str = "archive"):
        """
        Initialize the consolidated result manager.
        
        Args:
            output_dir: Base output directory
            archive_dir: Base archive directory
        """
        self.merger = ResultMerger()
        self.archiver = ResultArchiver(archive_dir)
        self.output_dir = Path(output_dir)
        self.logger = logging.getLogger(__name__)
    
    def process_session_results(self, session_dir: str, 
                              output_formats: List[str] = None) -> Dict[str, str]:
        """
        Process all results for a session and generate outputs.
        
        Args:
            session_dir: Path to session directory
            output_formats: List of output formats to generate
            
        Returns:
            Dict[str, str]: Mapping of format to output file path
        """
        if output_formats is None:
            output_formats = ['excel', 'html', 'json']
        
        session_path = Path(session_dir)
        if not session_path.exists():
            raise FileNotFoundError(f"Session directory not found: {session_dir}")
        
        # Load batch results
        batch_results = self._load_batch_results(session_path)
        
        # Merge results
        merged_results = self.merger.merge_batch_results(batch_results)
        
        # Generate output files
        output_files = {}
        results_dir = session_path / "results"
        
        for format_type in output_formats:
            if format_type == 'excel':
                output_path = results_dir / f"consolidated_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                output_files['excel'] = self.merger.generate_excel_output(merged_results, str(output_path))
            elif format_type == 'html':
                output_path = results_dir / f"results_visualization_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
                output_files['html'] = self.merger.generate_html_visualization(merged_results, str(output_path))
            elif format_type == 'json':
                output_path = results_dir / f"merged_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                output_files['json'] = self.merger.generate_json_output(merged_results, str(output_path))
        
        self.logger.info(f"Generated {len(output_files)} output files for session: {session_dir}")
        return output_files
    
    def archive_session(self, session_dir: str, compressed: bool = True) -> str:
        """
        Archive a session with all its results.
        
        Args:
            session_dir: Path to session directory
            compressed: Whether to create compressed archive
            
        Returns:
            str: Path to created archive
        """
        if compressed:
            return self.archiver.create_compressed_archive(session_dir)
        else:
            return self.archiver.create_archive(session_dir)
    
    def _load_batch_results(self, session_path: Path) -> List[BatchResult]:
        """Load batch results from session directory."""
        batch_results = []
        
        # Look for batch result files
        batch_results_dir = session_path / "results" / "batch_results"
        if batch_results_dir.exists():
            for batch_file in batch_results_dir.glob("batch_*.json"):
                try:
                    with open(batch_file, 'r', encoding='utf-8') as f:
                        batch_data = json.load(f)
                        batch_result = self._convert_to_batch_result(batch_data)
                        batch_results.append(batch_result)
                except Exception as e:
                    self.logger.error(f"Failed to load batch result {batch_file}: {e}")
        
        return batch_results
    
    def _convert_to_batch_result(self, batch_data: Dict[str, Any]) -> BatchResult:
        """Convert batch data dictionary to BatchResult object."""
        documents = []
        
        for doc_data in batch_data.get('documents', []):
            doc_result = DocumentResult(
                document_name=doc_data.get('document_name', ''),
                study_id=doc_data.get('study_id', ''),
                assessment_results=doc_data.get('assessment_results', {}),
                processing_time=doc_data.get('processing_time', 0.0),
                token_usage=doc_data.get('token_usage', {}),
                errors=doc_data.get('errors', [])
            )
            documents.append(doc_result)
        
        return BatchResult(
            batch_id=batch_data.get('batch_id', ''),
            documents_processed=batch_data.get('documents_processed', 0),
            documents_failed=batch_data.get('documents_failed', 0),
            total_processing_time=batch_data.get('total_processing_time', 0.0),
            results=documents
        )