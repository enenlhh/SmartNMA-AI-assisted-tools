# Checkpoint and Resume System Guide

This guide explains the checkpoint and resume functionality of the ROB Assessment Tool v2.0, which allows you to safely interrupt and resume long-running assessments.

## Table of Contents

1. [Overview](#overview)
2. [How Checkpoints Work](#how-checkpoints-work)
3. [Configuration](#configuration)
4. [Using Checkpoints](#using-checkpoints)
5. [Resume Operations](#resume-operations)
6. [Checkpoint Management](#checkpoint-management)
7. [Troubleshooting](#troubleshooting)
8. [Best Practices](#best-practices)
9. [Advanced Usage](#advanced-usage)

## Overview

The checkpoint and resume system provides:

- **Automatic State Saving**: Periodic saving of assessment progress
- **Intelligent Resume**: Continue from the exact point of interruption
- **State Validation**: Automatic detection and recovery from corrupted checkpoints
- **Progress Preservation**: Never lose work due to system failures or interruptions
- **Flexible Recovery**: Resume with modified configurations or resource allocations

## How Checkpoints Work

### Checkpoint Creation Process

1. **Automatic Triggers**:
   - Every N documents processed (configurable interval)
   - Before starting each new batch
   - After completing each batch
   - On graceful shutdown

2. **Manual Triggers**:
   - User interruption (Ctrl+C)
   - System shutdown detection
   - Memory pressure warnings

3. **Checkpoint Content**:
   - Session metadata (ID, start time, configuration)
   - Processing progress (completed documents, current batch)
   - Worker states and batch assignments
   - Cost tracking information
   - Error logs and recovery data

### Checkpoint File Structure

```json
{
  "session_id": "rob_session_20241201_143022",
  "start_time": "2024-12-01T14:30:22.123456",
  "checkpoint_time": "2024-12-01T15:45:33.789012",
  "total_documents": 150,
  "completed_documents": 75,
  "failed_documents": 2,
  "current_batch": 4,
  "total_batches": 6,
  "config_snapshot": {
    "paths": {...},
    "parallel": {...},
    "llm_models": [...]
  },
  "batch_states": [
    {
      "batch_id": "batch_001",
      "status": "completed",
      "documents": ["doc1.pdf", "doc2.pdf"],
      "start_time": "2024-12-01T14:30:25.000000",
      "end_time": "2024-12-01T14:45:12.000000"
    }
  ],
  "cost_tracking": {
    "total_cost": 12.45,
    "cost_by_model": {...},
    "token_usage": {...}
  },
  "error_log": [
    {
      "document": "problematic_doc.pdf",
      "error": "API timeout",
      "timestamp": "2024-12-01T15:30:15.000000"
    }
  ]
}
```

## Configuration

### Basic Checkpoint Configuration

```json
{
  "processing": {
    "enable_resume": true
  },
  "parallel": {
    "checkpoint_interval": 10,
    "checkpoint_on_batch_complete": true,
    "checkpoint_on_error": true
  },
  "paths": {
    "checkpoint_file": "checkpoints/assessment.json",
    "checkpoint_backup_dir": "checkpoints/backups"
  }
}
```

### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `enable_resume` | boolean | true | Enable checkpoint/resume functionality |
| `checkpoint_interval` | integer | 10 | Save checkpoint every N documents |
| `checkpoint_on_batch_complete` | boolean | true | Save checkpoint after each batch |
| `checkpoint_on_error` | boolean | true | Save checkpoint when errors occur |
| `checkpoint_file` | string | "checkpoint.json" | Primary checkpoint file path |
| `checkpoint_backup_dir` | string | "checkpoints" | Directory for checkpoint backups |
| `max_checkpoint_backups` | integer | 5 | Maximum number of backup checkpoints |

### Advanced Configuration

```json
{
  "checkpoint_system": {
    "compression": true,
    "encryption": false,
    "validation_on_save": true,
    "auto_cleanup_old": true,
    "backup_interval": 50,
    "recovery_mode": "automatic"
  }
}
```

## Using Checkpoints

### Automatic Checkpoint Creation

Checkpoints are created automatically during normal operation:

```bash
# Start assessment - checkpoints created automatically
python main.py start -c config/config.json

# Monitor shows checkpoint creation
# [14:30:22] Starting ROB assessment...
# [14:35:15] Checkpoint created: checkpoint_20241201_143022.json
# [14:40:33] Batch 1 completed, checkpoint updated
# [14:45:12] Checkpoint created: checkpoint_20241201_143022.json
```

### Manual Checkpoint Creation

```bash
# Graceful interruption creates checkpoint
python main.py start -c config/config.json
# Press Ctrl+C during processing
# [14:47:25] Interrupt signal received
# [14:47:26] Creating checkpoint before shutdown...
# [14:47:27] Checkpoint saved: checkpoint_20241201_143022.json
# [14:47:28] Graceful shutdown completed
```

### Checkpoint Verification

```bash
# Verify checkpoint integrity
python main.py resume -s checkpoint_20241201_143022.json --validate-only

# View checkpoint information
python -c "
import json
with open('checkpoint_20241201_143022.json', 'r') as f:
    checkpoint = json.load(f)
print(f'Session: {checkpoint[\"session_id\"]}')
print(f'Progress: {checkpoint[\"completed_documents\"]}/{checkpoint[\"total_documents\"]}')
print(f'Status: {checkpoint[\"completed_documents\"]/checkpoint[\"total_documents\"]*100:.1f}% complete')
"
```

## Resume Operations

### Basic Resume

```bash
# Resume from most recent checkpoint
python main.py resume -s checkpoint_20241201_143022.json

# Resume with interactive confirmation
python main.py resume -s checkpoint_20241201_143022.json --interactive

# Resume with different worker count
python main.py resume -s checkpoint_20241201_143022.json -w 8
```

### Resume with Modified Configuration

```bash
# Resume with updated configuration
python main.py resume -s checkpoint_20241201_143022.json -c config/updated_config.json

# Resume with specific overrides
python main.py resume -s checkpoint_20241201_143022.json \
  --workers 4 \
  --batch-size 25 \
  --output-dir output/resumed_results
```

### Resume Process Flow

1. **Checkpoint Validation**:
   - Verify checkpoint file integrity
   - Validate JSON structure
   - Check for required fields

2. **State Restoration**:
   - Load session metadata
   - Restore processing progress
   - Rebuild batch assignments

3. **Configuration Merge**:
   - Use saved configuration as base
   - Apply command-line overrides
   - Validate merged configuration

4. **Work Detection**:
   - Identify completed documents
   - Skip already processed files
   - Resume from interruption point

5. **Processing Continuation**:
   - Start remaining workers
   - Continue with pending batches
   - Maintain cost tracking

### Resume Examples

#### Example 1: Simple Resume
```bash
# Assessment was interrupted at 60% completion
python main.py resume -s checkpoint_20241201_143022.json

# Output:
# [15:30:22] Loading checkpoint: checkpoint_20241201_143022.json
# [15:30:23] Checkpoint validated successfully
# [15:30:24] Session: rob_session_20241201_143022
# [15:30:25] Progress: 90/150 documents completed (60.0%)
# [15:30:26] Resuming from batch 4 of 6
# [15:30:27] Starting 4 parallel workers...
# [15:30:28] Resuming assessment...
```

#### Example 2: Resume with Resource Changes
```bash
# Original assessment used 8 workers, resume with 4 due to system constraints
python main.py resume -s checkpoint_20241201_143022.json -w 4

# Output:
# [15:30:22] Loading checkpoint: checkpoint_20241201_143022.json
# [15:30:23] Configuration override: workers changed from 8 to 4
# [15:30:24] Redistributing remaining work across 4 workers
# [15:30:25] Resuming assessment with modified configuration...
```

#### Example 3: Resume After System Upgrade
```bash
# Resume after system maintenance with updated API keys
python main.py resume -s checkpoint_20241201_143022.json -c config/updated_config.json

# Output:
# [15:30:22] Loading checkpoint: checkpoint_20241201_143022.json
# [15:30:23] Merging with updated configuration: config/updated_config.json
# [15:30:24] API configuration updated
# [15:30:25] Resuming assessment with updated settings...
```

## Checkpoint Management

### Listing Available Checkpoints

```bash
# List all checkpoint files
ls -la *.checkpoint.json

# Show checkpoint details
python -c "
import json
import glob
from datetime import datetime

for checkpoint_file in glob.glob('*.checkpoint.json'):
    with open(checkpoint_file, 'r') as f:
        data = json.load(f)
    
    progress = data['completed_documents'] / data['total_documents'] * 100
    start_time = datetime.fromisoformat(data['start_time'])
    
    print(f'{checkpoint_file}:')
    print(f'  Session: {data[\"session_id\"]}')
    print(f'  Started: {start_time.strftime(\"%Y-%m-%d %H:%M:%S\")}')
    print(f'  Progress: {progress:.1f}% ({data[\"completed_documents\"]}/{data[\"total_documents\"]})')
    print(f'  Status: {\"Completed\" if progress == 100 else \"Incomplete\"}')
    print()
"
```

### Checkpoint Cleanup

```bash
# Clean up old checkpoints (keep last 5)
python main.py cleanup --checkpoints --keep 5

# Remove specific checkpoint
rm checkpoint_20241201_143022.json

# Archive completed checkpoints
mkdir -p archive/checkpoints
mv completed_*.checkpoint.json archive/checkpoints/
```

### Checkpoint Backup and Recovery

```bash
# Create manual backup
cp checkpoint_20241201_143022.json checkpoint_20241201_143022.backup.json

# Restore from backup
cp checkpoint_20241201_143022.backup.json checkpoint_20241201_143022.json

# Automated backup script
#!/bin/bash
CHECKPOINT_DIR="checkpoints"
BACKUP_DIR="checkpoints/backups"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR
for checkpoint in $CHECKPOINT_DIR/*.checkpoint.json; do
    if [ -f "$checkpoint" ]; then
        cp "$checkpoint" "$BACKUP_DIR/$(basename $checkpoint .json)_$DATE.json"
    fi
done
```

## Troubleshooting

### Common Checkpoint Issues

#### Issue 1: Corrupted Checkpoint File

**Symptoms:**
```
JSONDecodeError: Expecting ',' delimiter
Checkpoint validation failed
Invalid checkpoint format
```

**Solutions:**
```bash
# Validate JSON structure
python -m json.tool checkpoint_20241201_143022.json

# Restore from backup
cp checkpoint_20241201_143022.backup.json checkpoint_20241201_143022.json

# Start fresh if no backup available
python main.py start -c config/config.json
```

#### Issue 2: Missing Checkpoint File

**Symptoms:**
```
FileNotFoundError: Checkpoint file not found
No checkpoint available for resume
```

**Solutions:**
```bash
# List available checkpoints
ls -la *.checkpoint.json

# Use different checkpoint file
python main.py resume -s alternative_checkpoint.json

# Start new assessment if no checkpoints available
python main.py start -c config/config.json
```

#### Issue 3: Configuration Mismatch

**Symptoms:**
```
Configuration validation failed during resume
API key mismatch in checkpoint
Path not found in resumed configuration
```

**Solutions:**
```bash
# Resume with updated configuration
python main.py resume -s checkpoint.json -c config/current_config.json

# Override specific settings
python main.py resume -s checkpoint.json --api-key new_key

# Validate configuration before resume
python main.py resume -s checkpoint.json --validate-only
```

#### Issue 4: Incomplete Resume

**Symptoms:**
- Resume starts from beginning instead of checkpoint
- Documents processed multiple times
- Progress not preserved

**Solutions:**
```bash
# Check checkpoint integrity
python -c "
import json
with open('checkpoint.json', 'r') as f:
    data = json.load(f)
print('Completed documents:', len(data.get('completed_documents', [])))
print('Batch states:', len(data.get('batch_states', [])))
"

# Force clean resume
python main.py resume -s checkpoint.json --force-clean

# Manual verification of completed work
ls -la output/results/
```

### Diagnostic Commands

```bash
# Validate checkpoint file
python main.py resume -s checkpoint.json --validate-only

# Show detailed checkpoint information
python main.py resume -s checkpoint.json --info

# Test resume without execution
python main.py resume -s checkpoint.json --dry-run

# Enable verbose logging for resume
python main.py resume -s checkpoint.json --verbose --log-file resume_debug.log
```

## Best Practices

### Checkpoint Strategy

1. **Frequent Checkpoints**: Set checkpoint_interval to 5-10 documents for long assessments
2. **Batch Checkpoints**: Always enable checkpoint_on_batch_complete
3. **Error Checkpoints**: Enable checkpoint_on_error to preserve progress before failures
4. **Backup Strategy**: Maintain multiple checkpoint backups
5. **Validation**: Regularly validate checkpoint integrity

### Configuration Management

```json
{
  "checkpoint_best_practices": {
    "checkpoint_interval": 5,
    "checkpoint_on_batch_complete": true,
    "checkpoint_on_error": true,
    "max_checkpoint_backups": 10,
    "validation_on_save": true,
    "auto_cleanup_old": true
  }
}
```

### Resume Strategy

1. **Validate First**: Always validate checkpoints before resuming
2. **Resource Check**: Verify system resources before resume
3. **Configuration Review**: Check for configuration changes since checkpoint
4. **Progress Verification**: Confirm resume starts from correct point
5. **Monitor Resume**: Watch initial resume progress carefully

### Maintenance

```bash
# Weekly checkpoint maintenance script
#!/bin/bash

# Archive old completed checkpoints
find . -name "*.checkpoint.json" -mtime +7 -exec grep -l '"completed_documents": 100' {} \; | \
    xargs -I {} mv {} archive/

# Clean up temporary checkpoint files
find . -name "*.checkpoint.tmp" -mtime +1 -delete

# Validate remaining checkpoints
for checkpoint in *.checkpoint.json; do
    if ! python -m json.tool "$checkpoint" > /dev/null 2>&1; then
        echo "Warning: Corrupted checkpoint $checkpoint"
    fi
done
```

## Advanced Usage

### Programmatic Checkpoint Management

```python
# checkpoint_manager.py
import json
import glob
from datetime import datetime, timedelta
from pathlib import Path

class CheckpointManager:
    def __init__(self, checkpoint_dir="checkpoints"):
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(exist_ok=True)
    
    def list_checkpoints(self):
        """List all available checkpoints with metadata"""
        checkpoints = []
        for checkpoint_file in self.checkpoint_dir.glob("*.checkpoint.json"):
            try:
                with open(checkpoint_file, 'r') as f:
                    data = json.load(f)
                
                checkpoints.append({
                    'file': checkpoint_file,
                    'session_id': data['session_id'],
                    'start_time': datetime.fromisoformat(data['start_time']),
                    'progress': data['completed_documents'] / data['total_documents'],
                    'total_documents': data['total_documents'],
                    'completed_documents': data['completed_documents']
                })
            except (json.JSONDecodeError, KeyError):
                continue
        
        return sorted(checkpoints, key=lambda x: x['start_time'], reverse=True)
    
    def find_latest_checkpoint(self):
        """Find the most recent checkpoint"""
        checkpoints = self.list_checkpoints()
        return checkpoints[0] if checkpoints else None
    
    def cleanup_old_checkpoints(self, keep_count=5):
        """Remove old checkpoint files, keeping the most recent ones"""
        checkpoints = self.list_checkpoints()
        
        if len(checkpoints) > keep_count:
            for checkpoint in checkpoints[keep_count:]:
                checkpoint['file'].unlink()
                print(f"Removed old checkpoint: {checkpoint['file']}")
    
    def validate_checkpoint(self, checkpoint_file):
        """Validate checkpoint file integrity"""
        try:
            with open(checkpoint_file, 'r') as f:
                data = json.load(f)
            
            required_fields = ['session_id', 'start_time', 'total_documents', 'completed_documents']
            for field in required_fields:
                if field not in data:
                    return False, f"Missing required field: {field}"
            
            return True, "Checkpoint is valid"
        
        except json.JSONDecodeError as e:
            return False, f"JSON decode error: {e}"
        except Exception as e:
            return False, f"Validation error: {e}"

# Usage example
if __name__ == "__main__":
    manager = CheckpointManager()
    
    # List all checkpoints
    checkpoints = manager.list_checkpoints()
    for cp in checkpoints:
        print(f"Session: {cp['session_id']}")
        print(f"Progress: {cp['progress']:.1%}")
        print(f"Started: {cp['start_time']}")
        print()
    
    # Find latest checkpoint
    latest = manager.find_latest_checkpoint()
    if latest:
        print(f"Latest checkpoint: {latest['file']}")
        
        # Validate it
        is_valid, message = manager.validate_checkpoint(latest['file'])
        print(f"Validation: {message}")
    
    # Cleanup old checkpoints
    manager.cleanup_old_checkpoints(keep_count=3)
```

### Custom Resume Logic

```python
# custom_resume.py
import json
import subprocess
from pathlib import Path

def smart_resume(checkpoint_file, config_file=None, max_workers=None):
    """Smart resume with automatic configuration adjustment"""
    
    # Load checkpoint
    with open(checkpoint_file, 'r') as f:
        checkpoint = json.load(f)
    
    # Calculate remaining work
    remaining = checkpoint['total_documents'] - checkpoint['completed_documents']
    progress = checkpoint['completed_documents'] / checkpoint['total_documents']
    
    print(f"Resuming session: {checkpoint['session_id']}")
    print(f"Progress: {progress:.1%} ({checkpoint['completed_documents']}/{checkpoint['total_documents']})")
    print(f"Remaining documents: {remaining}")
    
    # Adjust workers based on remaining work
    if max_workers is None:
        if remaining < 10:
            max_workers = 1
        elif remaining < 50:
            max_workers = 2
        else:
            max_workers = 4
    
    print(f"Using {max_workers} workers for remaining work")
    
    # Build resume command
    cmd = ['python', 'main.py', 'resume', '-s', checkpoint_file, '-w', str(max_workers)]
    
    if config_file:
        cmd.extend(['-c', config_file])
    
    # Execute resume
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("Resume completed successfully")
    else:
        print(f"Resume failed: {result.stderr}")
    
    return result.returncode == 0

# Usage
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python custom_resume.py <checkpoint_file> [config_file]")
        sys.exit(1)
    
    checkpoint_file = sys.argv[1]
    config_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    smart_resume(checkpoint_file, config_file)
```

The checkpoint and resume system provides robust protection against data loss and enables flexible workflow management for long-running ROB assessments. By following the best practices and using the advanced features, you can ensure reliable and efficient processing of large document sets.