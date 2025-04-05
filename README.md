# real-url-plugin
real-url project test

python test_plugins.py                   # Test all platforms
python test_plugins.py -p douyu huya     # Test specific platforms
python test_plugins.py -s                # Run tests sequentially
python test_plugins.py -w 10             # Use 10 worker threads
python test_plugins.py -o results.json   # Save results to JSON file

This script provides comprehensive testing of live streaming plugins with these features:
Automated Testing: Tests all or specified platforms against predefined test URLs
Parallel Processing: Uses ThreadPoolExecutor to test multiple plugins simultaneously
Detailed Logging: Creates log files with timestamps to track test history
Comprehensive Reporting: Generates detailed reports showing success/failure rates and reasons
Plugin Status: Identifies which plugins need updates and why
Usage Instructions:

Technical Implementation:
Plugin Registry Integration: Works with the existing plugin system
Error Handling: Captures and classifies different types of failures
Performance Metrics: Times how long each plugin takes to respond
Recommendations: Provides specific suggestions for fixing failed plugins
Reporting: Generates both human-readable and machine-readable (JSON) reports
The script helps developers quickly identify which plugins need updates when streaming platforms change their APIs, saving significant debugging time.