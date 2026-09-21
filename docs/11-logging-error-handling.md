# Logging & Error Handling

## Logging Mechanisms

### Validation Logging System

#### Log Entry Structure
The application maintains comprehensive logs of all validation events with structured data format for analysis and audit purposes.

**Log Entry Format**:
```json
{
  "timestamp": "2026-04-15 14:30:25.123",
  "scanned_code": "89012345678901234567",
  "expected_code": "89012345678901234567", 
  "status": "OK",
  "card_index": 150,
  "scan_direction": "top_to_bottom",
  "head_id": "A",
  "output_signal": "09\r\n"
}
```

#### Status Code Definitions
```python
VALIDATION_STATUSES = {
    "OK": "Correct card scanned in sequence",
    "NOT OK": "Wrong card or sequence error", 
    "OK (JUMPED)": "Approved skip-ahead in sequence",
    "SKIPPED": "Cards jumped over in sequence",
    "EXTRA SCAN": "Scanning beyond sequence end",
    "NOT IN SEQUENCE": "Card not found in loaded file",
    "NO FILE": "No sequence file loaded",
    "INDEX ERROR": "Array bounds violation",
    "DATA ERROR": "Missing or corrupt card data",
    "SCAN ERROR": "Unexpected exception during scan"
}
```

#### Real-Time Logging Implementation
```python
class ValidationLogger:
    def __init__(self, head_id):
        self.head_id = head_id
        self.log_data = []
        self.log_lock = threading.RLock()
        
    def add_log_entry(self, scanned_code, expected_code, status, card_index):
        """Add new log entry with thread safety"""
        with self.log_lock:
            entry = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
                "scanned_code": scanned_code,
                "expected_code": expected_code,
                "status": status,
                "card_index": card_index,
                "scan_direction": self.scan_direction,
                "head_id": self.head_id
            }
            
            self.log_data.append(entry)
            self.emit_log_update()
            
            # Auto-save trigger
            self.check_auto_save()
    
    def emit_log_update(self):
        """Emit signal for UI updates"""
        self.log_updated.emit(self.log_data)
```

### System Event Logging

#### Application Event Categories
1. **Startup Events**: Application initialization, license validation
2. **Configuration Events**: Settings changes, network configuration
3. **File Operations**: File loading, parsing, validation
4. **Network Events**: Connection status, communication errors
5. **Validation Events**: All scan processing and results
6. **Error Events**: Exceptions, failures, recovery attempts
7. **Shutdown Events**: Application termination, cleanup

#### Event Logging Implementation
```python
class SystemLogger:
    def __init__(self):
        self.log_file = "debug_output.txt"
        self.log_level = "INFO"
        self.max_log_size = 10 * 1024 * 1024  # 10MB
        
    def log_event(self, level, category, message, context=None):
        """Log system event with context"""
        timestamp = datetime.now().isoformat()
        
        log_entry = {
            "timestamp": timestamp,
            "level": level,
            "category": category,
            "message": message,
            "context": context or {},
            "thread": threading.current_thread().name
        }
        
        self.write_log_entry(log_entry)
        
    def write_log_entry(self, entry):
        """Write log entry to file with rotation"""
        try:
            # Check file size and rotate if needed
            if os.path.exists(self.log_file):
                if os.path.getsize(self.log_file) > self.max_log_size:
                    self.rotate_log_file()
            
            # Write entry
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(f"{entry['timestamp']} [{entry['level']}] "
                       f"{entry['category']}: {entry['message']}\n")
                if entry['context']:
                    f.write(f"  Context: {json.dumps(entry['context'])}\n")
                    
        except Exception as e:
            # Fallback logging to console if file write fails
            print(f"Logging error: {e}")
```

### Network Communication Logging

#### UDP Communication Events
```python
class NetworkLogger:
    def log_udp_event(self, event_type, local_addr, remote_addr, data=None, error=None):
        """Log UDP communication events"""
        context = {
            "local_ip": local_addr[0],
            "local_port": local_addr[1],
            "remote_ip": remote_addr[0] if remote_addr else None,
            "remote_port": remote_addr[1] if remote_addr else None,
            "data_length": len(data) if data else 0,
            "error": str(error) if error else None
        }
        
        if event_type == "DATA_RECEIVED":
            message = f"Received {len(data)} bytes from {remote_addr[0]}:{remote_addr[1]}"
        elif event_type == "DATA_SENT":
            message = f"Sent {len(data)} bytes to {remote_addr[0]}:{remote_addr[1]}"
        elif event_type == "CONNECTION_ERROR":
            message = f"Connection error: {error}"
        elif event_type == "BIND_SUCCESS":
            message = f"Successfully bound to {local_addr[0]}:{local_addr[1]}"
        
        self.system_logger.log_event("INFO", "NETWORK", message, context)
```

#### Serial Communication Events
```python
def log_serial_event(self, event_type, port, data=None, error=None):
    """Log serial communication events"""
    context = {
        "port": port,
        "baudrate": self.baudrate,
        "data_length": len(data) if data else 0,
        "error": str(error) if error else None
    }
    
    if event_type == "PORT_OPENED":
        message = f"Serial port {port} opened successfully"
    elif event_type == "DATA_RECEIVED":
        message = f"Received {len(data)} bytes from {port}"
    elif event_type == "PORT_ERROR":
        message = f"Serial port error on {port}: {error}"
    elif event_type == "PORT_CLOSED":
        message = f"Serial port {port} closed"
    
    self.system_logger.log_event("INFO", "SERIAL", message, context)
```

### Performance Logging

#### Performance Metrics Collection
```python
class PerformanceLogger:
    def __init__(self):
        self.metrics = {
            "validation_times": [],
            "network_response_times": [],
            "file_load_times": [],
            "cache_save_times": []
        }
        
    def log_validation_performance(self, start_time, end_time, result):
        """Log validation performance metrics"""
        duration = (end_time - start_time) * 1000  # Convert to milliseconds
        
        self.metrics["validation_times"].append({
            "timestamp": datetime.now().isoformat(),
            "duration_ms": duration,
            "result": result,
            "memory_usage": self.get_memory_usage()
        })
        
        # Alert if performance degrades
        if duration > 100:  # Alert if validation takes >100ms
            self.system_logger.log_event("WARNING", "PERFORMANCE", 
                                        f"Slow validation: {duration:.2f}ms")
    
    def get_memory_usage(self):
        """Get current memory usage"""
        import psutil
        process = psutil.Process()
        return process.memory_info().rss / 1024 / 1024  # MB
```

## Error Handling Strategies

### Hierarchical Error Handling

#### Error Classification System
```python
class ErrorClassification:
    CRITICAL = "CRITICAL"    # System failure, requires restart
    HIGH = "HIGH"           # Feature failure, requires user action
    MEDIUM = "MEDIUM"       # Recoverable error, automatic retry
    LOW = "LOW"            # Warning, informational only
    
    ERROR_CATEGORIES = {
        "NETWORK_ERROR": MEDIUM,
        "FILE_ERROR": HIGH,
        "VALIDATION_ERROR": LOW,
        "SYSTEM_ERROR": CRITICAL,
        "CONFIG_ERROR": HIGH,
        "LICENSE_ERROR": CRITICAL
    }
```

#### Error Handler Implementation
```python
class ErrorHandler:
    def __init__(self):
        self.error_handlers = {
            "NETWORK_ERROR": self.handle_network_error,
            "FILE_ERROR": self.handle_file_error,
            "VALIDATION_ERROR": self.handle_validation_error,
            "SYSTEM_ERROR": self.handle_system_error,
            "CONFIG_ERROR": self.handle_config_error,
            "LICENSE_ERROR": self.handle_license_error
        }
        
    def handle_error(self, error_type, error_context, exception=None):
        """Central error handling dispatcher"""
        try:
            # Log the error
            self.log_error(error_type, error_context, exception)
            
            # Get appropriate handler
            handler = self.error_handlers.get(error_type, self.handle_unknown_error)
            
            # Execute handler
            recovery_action = handler(error_context, exception)
            
            # Log recovery action
            self.log_recovery_action(error_type, recovery_action)
            
            return recovery_action
            
        except Exception as handler_error:
            # Handler itself failed - log and use fallback
            self.log_handler_failure(error_type, handler_error)
            return self.fallback_error_handling(error_type, error_context)
```

### Network Error Handling

#### Connection Failure Recovery
```python
def handle_network_error(self, context, exception):
    """Handle network communication errors"""
    error_details = {
        "local_ip": context.get("local_ip"),
        "local_port": context.get("local_port"),
        "remote_ip": context.get("remote_ip"),
        "remote_port": context.get("remote_port"),
        "error_message": str(exception)
    }
    
    # Determine recovery strategy
    if "Connection refused" in str(exception):
        return self.handle_connection_refused(error_details)
    elif "Network unreachable" in str(exception):
        return self.handle_network_unreachable(error_details)
    elif "Timeout" in str(exception):
        return self.handle_network_timeout(error_details)
    else:
        return self.handle_generic_network_error(error_details)

def handle_connection_refused(self, error_details):
    """Handle connection refused errors"""
    recovery_steps = [
        "verify_remote_device_power",
        "check_remote_port_configuration", 
        "test_network_connectivity",
        "retry_connection_with_backoff"
    ]
    
    return {
        "action": "RETRY_WITH_BACKOFF",
        "steps": recovery_steps,
        "user_message": "Remote device not responding. Checking connection...",
        "retry_count": 3,
        "backoff_seconds": [1, 5, 15]
    }
```

#### Network Retry Logic
```python
class NetworkRetryManager:
    def __init__(self):
        self.max_retries = 3
        self.base_delay = 1.0
        self.max_delay = 30.0
        
    def retry_with_exponential_backoff(self, operation, context):
        """Retry network operation with exponential backoff"""
        for attempt in range(self.max_retries):
            try:
                result = operation(context)
                
                # Success - reset retry state
                self.reset_retry_state(context)
                return result
                
            except Exception as e:
                if attempt == self.max_retries - 1:
                    # Final attempt failed
                    raise e
                
                # Calculate delay for next attempt
                delay = min(self.base_delay * (2 ** attempt), self.max_delay)
                
                self.log_retry_attempt(attempt + 1, delay, str(e))
                time.sleep(delay)
        
        raise Exception(f"Operation failed after {self.max_retries} attempts")
```

### File Error Handling

#### File Processing Error Recovery
```python
def handle_file_error(self, context, exception):
    """Handle file processing errors"""
    file_path = context.get("file_path")
    error_type = type(exception).__name__
    
    if error_type == "FileNotFoundError":
        return self.handle_file_not_found(file_path)
    elif error_type == "PermissionError":
        return self.handle_permission_error(file_path)
    elif error_type == "UnicodeDecodeError":
        return self.handle_encoding_error(file_path)
    elif "corrupted" in str(exception).lower():
        return self.handle_corrupted_file(file_path)
    else:
        return self.handle_generic_file_error(file_path, exception)

def handle_corrupted_file(self, file_path):
    """Handle corrupted file recovery"""
    recovery_actions = []
    
    # Try to create backup if possible
    try:
        backup_path = file_path + ".backup"
        if os.path.exists(file_path):
            shutil.copy2(file_path, backup_path)
            recovery_actions.append(f"Created backup: {backup_path}")
    except Exception:
        pass
    
    # Attempt file repair
    repair_result = self.attempt_file_repair(file_path)
    recovery_actions.extend(repair_result.get("actions", []))
    
    return {
        "action": "FILE_REPAIR_ATTEMPTED",
        "success": repair_result.get("success", False),
        "recovery_actions": recovery_actions,
        "user_message": "File corruption detected. Attempting repair...",
        "fallback_action": "REQUEST_NEW_FILE"
    }
```

### Validation Error Handling

#### Scan Processing Error Recovery
```python
def handle_validation_error(self, context, exception):
    """Handle validation processing errors"""
    scan_data = context.get("scan_data")
    expected_data = context.get("expected_data")
    error_type = context.get("error_type")
    
    if error_type == "INDEX_ERROR":
        return self.handle_index_error(context)
    elif error_type == "DATA_ERROR":
        return self.handle_data_error(context)
    elif error_type == "SEQUENCE_ERROR":
        return self.handle_sequence_error(context)
    else:
        return self.handle_generic_validation_error(context, exception)

def handle_index_error(self, context):
    """Handle array bounds violations"""
    # Reset to safe state
    recovery_actions = [
        "reset_card_index_to_safe_value",
        "validate_sequence_bounds",
        "log_index_error_details"
    ]
    
    return {
        "action": "RESET_TO_SAFE_STATE",
        "log_status": "INDEX ERROR",
        "recovery_actions": recovery_actions,
        "user_message": "Sequence index error detected. Resetting to safe state.",
        "continue_validation": True
    }
```

### System Error Handling

#### Critical System Failures
```python
def handle_system_error(self, context, exception):
    """Handle critical system errors"""
    error_severity = self.assess_error_severity(exception)
    
    if error_severity == "CRITICAL":
        return self.handle_critical_system_error(context, exception)
    elif error_severity == "SEVERE":
        return self.handle_severe_system_error(context, exception)
    else:
        return self.handle_recoverable_system_error(context, exception)

def handle_critical_system_error(self, context, exception):
    """Handle errors requiring application restart"""
    # Attempt to save critical data
    self.emergency_data_save()
    
    # Log critical error details
    self.log_critical_error(exception, context)
    
    # Notify user and prepare for shutdown
    return {
        "action": "EMERGENCY_SHUTDOWN",
        "save_data": True,
        "user_message": "Critical system error detected. Application will restart.",
        "restart_required": True,
        "error_report": self.generate_error_report(exception, context)
    }
```

## Recovery Mechanisms

### Automatic Recovery Strategies

#### Session Recovery System
```python
class SessionRecoveryManager:
    def __init__(self):
        self.recovery_data = {}
        self.recovery_file = "session_recovery.json"
        
    def save_recovery_checkpoint(self, head_id, state_data):
        """Save recovery checkpoint for session restoration"""
        checkpoint = {
            "timestamp": datetime.now().isoformat(),
            "head_id": head_id,
            "file_path": state_data.get("file_path"),
            "current_card_index": state_data.get("current_card_index"),
            "scan_direction": state_data.get("scan_direction"),
            "log_count": len(state_data.get("log_data", [])),
            "validation_state": state_data.get("validation_state")
        }
        
        self.recovery_data[head_id] = checkpoint
        self.save_recovery_file()
    
    def restore_session(self, head_id):
        """Restore session from recovery data"""
        if head_id not in self.recovery_data:
            return None
            
        checkpoint = self.recovery_data[head_id]
        
        # Validate checkpoint age (don't restore very old sessions)
        checkpoint_time = datetime.fromisoformat(checkpoint["timestamp"])
        age_hours = (datetime.now() - checkpoint_time).total_seconds() / 3600
        
        if age_hours > 24:  # Don't restore sessions older than 24 hours
            return None
            
        return checkpoint
```

#### Data Integrity Recovery
```python
class DataIntegrityManager:
    def __init__(self):
        self.integrity_checks = [
            self.check_cache_integrity,
            self.check_log_integrity,
            self.check_config_integrity
        ]
    
    def perform_integrity_check(self):
        """Perform comprehensive data integrity check"""
        results = {}
        
        for check in self.integrity_checks:
            try:
                check_name = check.__name__
                result = check()
                results[check_name] = result
                
                if not result["passed"]:
                    self.handle_integrity_failure(check_name, result)
                    
            except Exception as e:
                results[check_name] = {
                    "passed": False,
                    "error": str(e),
                    "action": "CHECK_FAILED"
                }
        
        return results
    
    def check_cache_integrity(self):
        """Check cache file integrity"""
        try:
            cache_file = get_unified_cache_file_path()
            
            if not os.path.exists(cache_file):
                return {"passed": True, "message": "No cache file exists"}
            
            # Check file size
            file_size = os.path.getsize(cache_file)
            if file_size == 0:
                return {"passed": False, "message": "Cache file is empty"}
            
            # Check JSON validity
            with open(cache_file, 'r') as f:
                json.load(f)
            
            return {"passed": True, "message": "Cache integrity OK"}
            
        except json.JSONDecodeError:
            return {"passed": False, "message": "Cache file corrupted (invalid JSON)"}
        except Exception as e:
            return {"passed": False, "message": f"Cache check failed: {e}"}
```

### User-Initiated Recovery

#### Manual Recovery Options
```python
class ManualRecoveryTools:
    def __init__(self):
        self.recovery_options = {
            "reset_configuration": self.reset_configuration,
            "clear_cache": self.clear_cache,
            "repair_cache": self.repair_cache,
            "export_logs": self.emergency_log_export,
            "reset_network": self.reset_network_config
        }
    
    def reset_configuration(self):
        """Reset configuration to defaults"""
        try:
            # Backup current configuration
            backup_path = self.create_config_backup()
            
            # Reset to defaults
            default_config = self.get_default_configuration()
            self.save_configuration(default_config)
            
            return {
                "success": True,
                "message": "Configuration reset to defaults",
                "backup_location": backup_path
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Configuration reset failed: {e}"
            }
    
    def repair_cache(self):
        """Attempt to repair corrupted cache file"""
        try:
            cache_file = get_unified_cache_file_path()
            
            # Create backup of corrupted file
            backup_file = cache_file + ".corrupted.backup"
            if os.path.exists(cache_file):
                shutil.copy2(cache_file, backup_file)
            
            # Attempt to parse and repair
            repaired_data = self.attempt_cache_repair(cache_file)
            
            if repaired_data:
                # Save repaired data
                with open(cache_file, 'w') as f:
                    json.dump(repaired_data, f, indent=4)
                
                return {
                    "success": True,
                    "message": "Cache file repaired successfully",
                    "backup_location": backup_file
                }
            else:
                # Repair failed, create new cache
                self.create_new_cache()
                return {
                    "success": True,
                    "message": "Cache file recreated (repair failed)",
                    "backup_location": backup_file
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"Cache repair failed: {e}"
            }
```

### Emergency Procedures

#### Emergency Data Preservation
```python
class EmergencyDataManager:
    def __init__(self):
        self.emergency_dir = os.path.join(os.path.expanduser("~"), "Desktop", "CardValidator_Emergency")
        
    def emergency_save_all_data(self):
        """Save all critical data in emergency situation"""
        try:
            # Create emergency directory
            os.makedirs(self.emergency_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Save logs for both heads
            self.save_emergency_logs(timestamp)
            
            # Save configuration
            self.save_emergency_config(timestamp)
            
            # Save system state
            self.save_emergency_state(timestamp)
            
            return {
                "success": True,
                "location": self.emergency_dir,
                "timestamp": timestamp
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def save_emergency_logs(self, timestamp):
        """Save logs in emergency situation"""
        for head_id in ['A', 'B']:
            try:
                head = self.get_head_instance(head_id)
                if head and head.log_data:
                    filename = f"emergency_logs_head_{head_id}_{timestamp}.csv"
                    filepath = os.path.join(self.emergency_dir, filename)
                    
                    with open(filepath, 'w', newline='', encoding='utf-8') as f:
                        writer = csv.writer(f)
                        writer.writerow(['Timestamp', 'Scanned Code', 'Expected Code', 
                                       'Status', 'Card Index', 'Direction'])
                        
                        for log_entry in head.log_data:
                            writer.writerow([
                                log_entry.get('timestamp', ''),
                                log_entry.get('scanned_code', ''),
                                log_entry.get('expected_code', ''),
                                log_entry.get('status', ''),
                                log_entry.get('card_index', ''),
                                log_entry.get('scan_direction', '')
                            ])
                            
            except Exception as e:
                # Log error but continue with other heads
                print(f"Emergency log save failed for head {head_id}: {e}")
```

## Error Reporting and Diagnostics

### Diagnostic Information Collection
```python
class DiagnosticCollector:
    def collect_diagnostic_info(self, error_context=None):
        """Collect comprehensive diagnostic information"""
        diagnostics = {
            "timestamp": datetime.now().isoformat(),
            "system_info": self.get_system_info(),
            "application_info": self.get_application_info(),
            "network_info": self.get_network_info(),
            "error_context": error_context,
            "recent_logs": self.get_recent_logs(),
            "performance_metrics": self.get_performance_metrics()
        }
        
        return diagnostics
    
    def get_system_info(self):
        """Collect system information"""
        import platform
        import psutil
        
        return {
            "os": platform.system(),
            "os_version": platform.version(),
            "python_version": platform.python_version(),
            "cpu_count": psutil.cpu_count(),
            "memory_total": psutil.virtual_memory().total,
            "memory_available": psutil.virtual_memory().available,
            "disk_usage": psutil.disk_usage('/').percent if os.name != 'nt' else psutil.disk_usage('C:').percent
        }
    
    def generate_diagnostic_report(self, diagnostics):
        """Generate formatted diagnostic report"""
        report_lines = [
            "=== CARD SEQUENCE VALIDATOR DIAGNOSTIC REPORT ===",
            f"Generated: {diagnostics['timestamp']}",
            "",
            "SYSTEM INFORMATION:",
            f"  OS: {diagnostics['system_info']['os']} {diagnostics['system_info']['os_version']}",
            f"  Python: {diagnostics['system_info']['python_version']}",
            f"  Memory: {diagnostics['system_info']['memory_available'] / 1024**3:.1f}GB available",
            "",
            "APPLICATION INFORMATION:",
            f"  Version: {diagnostics['application_info']['version']}",
            f"  Uptime: {diagnostics['application_info']['uptime']}",
            f"  Active Heads: {diagnostics['application_info']['active_heads']}",
            ""
        ]
        
        if diagnostics.get('error_context'):
            report_lines.extend([
                "ERROR CONTEXT:",
                f"  Error Type: {diagnostics['error_context'].get('error_type')}",
                f"  Error Message: {diagnostics['error_context'].get('message')}",
                f"  Stack Trace: {diagnostics['error_context'].get('stack_trace')}",
                ""
            ])
        
        return "\n".join(report_lines)
```

### Performance Monitoring and Alerting
```python
class PerformanceMonitor:
    def __init__(self):
        self.thresholds = {
            "validation_time_ms": 100,
            "memory_usage_mb": 500,
            "network_timeout_count": 5,
            "error_rate_percent": 5
        }
        
    def check_performance_thresholds(self, metrics):
        """Check if performance metrics exceed thresholds"""
        alerts = []
        
        # Check validation time
        avg_validation_time = sum(metrics["validation_times"]) / len(metrics["validation_times"])
        if avg_validation_time > self.thresholds["validation_time_ms"]:
            alerts.append({
                "type": "PERFORMANCE_DEGRADATION",
                "metric": "validation_time",
                "value": avg_validation_time,
                "threshold": self.thresholds["validation_time_ms"],
                "severity": "WARNING"
            })
        
        # Check memory usage
        current_memory = self.get_current_memory_usage()
        if current_memory > self.thresholds["memory_usage_mb"]:
            alerts.append({
                "type": "HIGH_MEMORY_USAGE",
                "metric": "memory_usage",
                "value": current_memory,
                "threshold": self.thresholds["memory_usage_mb"],
                "severity": "WARNING"
            })
        
        return alerts
```

---

*This comprehensive logging and error handling documentation provides detailed information about all logging mechanisms, error handling strategies, and recovery procedures implemented in the Card Sequence Validator system.*