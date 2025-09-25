#!/bin/bash
# Advanced Usage Examples for OpenStack Information Export Tool
# This script demonstrates advanced scenarios and automation patterns

echo "🚀 OpenStack Info Tool - Advanced Usage Examples"
echo "================================================"

# Check if the script exists
if [ ! -f "../os_info.py" ]; then
    echo "❌ Error: os_info.py not found. Run this script from the examples directory."
    exit 1
fi

# Get current date for timestamped files
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DATE=$(date +%Y%m%d)

echo ""
echo "📋 Advanced Example 1: Timestamped Reports"
echo "Description: Create reports with timestamps for historical tracking"
echo "Commands:"
echo "python ../os_info.py \\"
echo "    --instances-file instances_${TIMESTAMP}.csv \\"
echo "    --hypervisors-file hypervisors_${TIMESTAMP}.csv"
echo ""

echo "📋 Advanced Example 2: Daily Capacity Report"
echo "Description: Generate daily capacity reports with overcommit analysis"
echo "Commands:"
echo "python ../os_info.py \\"
echo "    --hypervisors-only \\"
echo "    --hypervisors-file daily_capacity_${DATE}.csv"
echo ""

echo "📋 Advanced Example 3: Multi-Region Data Collection"
echo "Description: Collect data from multiple OpenStack regions"
echo "Commands:"
echo "# Region 1"
echo "python ../os_info.py \\"
echo "    --region-name us-east-1 \\"
echo "    --instances-file instances_us_east_${DATE}.csv \\"
echo "    --hypervisors-file hypervisors_us_east_${DATE}.csv"
echo ""
echo "# Region 2"
echo "python ../os_info.py \\"
echo "    --region-name us-west-1 \\"
echo "    --instances-file instances_us_west_${DATE}.csv \\"
echo "    --hypervisors-file hypervisors_us_west_${DATE}.csv"
echo ""

echo "📋 Advanced Example 4: Command Line Authentication"
echo "Description: Pass credentials directly via command line (use carefully!)"
echo "Commands:"
echo "python ../os_info.py \\"
echo "    --auth-method args \\"
echo "    --auth-url https://keystone.example.com:5000/v3 \\"
echo "    --username \$OS_USERNAME \\"
echo "    --password \$OS_PASSWORD \\"
echo "    --project-name \$OS_PROJECT_NAME \\"
echo "    --region-name RegionOne"
echo ""

echo "📋 Advanced Example 5: Automated Weekly Reports"
echo "Description: Script for weekly infrastructure reporting"
echo "Commands:"
cat << 'EOF'
#!/bin/bash
# Weekly OpenStack Infrastructure Report
WEEK=$(date +%Y_week_%U)
REPORT_DIR="reports/$WEEK"
mkdir -p "$REPORT_DIR"

# Full infrastructure snapshot
python ../os_info.py \
    --instances-file "$REPORT_DIR/instances_$WEEK.csv" \
    --hypervisors-file "$REPORT_DIR/hypervisors_$WEEK.csv"

# Create summary
echo "Weekly Report: $WEEK" > "$REPORT_DIR/summary.txt"
echo "Generated: $(date)" >> "$REPORT_DIR/summary.txt"
echo "Instance count: $(tail -n +2 "$REPORT_DIR/instances_$WEEK.csv" | wc -l)" >> "$REPORT_DIR/summary.txt"
echo "Hypervisor count: $(tail -n +2 "$REPORT_DIR/hypervisors_$WEEK.csv" | wc -l)" >> "$REPORT_DIR/summary.txt"
EOF
echo ""

echo "📋 Advanced Example 6: Performance Monitoring Integration"
echo "Description: Integration with monitoring systems"
echo "Commands:"
echo "# Extract specific metrics for monitoring"
echo "python ../os_info.py --hypervisors-only | \\"
echo "  python -c \""
echo "import csv, sys"
echo "reader = csv.DictReader(sys.stdin)"
echo "for row in reader:"
echo "    if float(row['CPU Overcommit Ratio']) > 1.5:"
echo "        print(f'ALERT: {row[\"Hostname\"]} CPU overcommit: {row[\"CPU Overcommit Ratio\"]}')"
echo "\""
echo ""

echo "📋 Advanced Example 7: Backup and Archive"
echo "Description: Automated backup with compression and archival"
echo "Commands:"
echo "# Create compressed archive of reports"
echo "ARCHIVE_NAME=\"openstack_report_${DATE}.tar.gz\""
echo "python ../os_info.py"
echo "tar -czf \$ARCHIVE_NAME *.csv"
echo "# Optional: Upload to cloud storage"
echo "# aws s3 cp \$ARCHIVE_NAME s3://your-bucket/openstack-reports/"
echo ""

echo "📋 Advanced Example 8: Configuration Management"
echo "Description: Use different configs for different environments"
echo "Commands:"
echo "# Production environment"
echo "python ../os_info.py \\"
echo "    --auth-method config \\"
echo "    --config-file configs/production.conf \\"
echo "    --instances-file prod_instances_${DATE}.csv"
echo ""
echo "# Staging environment"
echo "python ../os_info.py \\"
echo "    --auth-method config \\"
echo "    --config-file configs/staging.conf \\"
echo "    --instances-file staging_instances_${DATE}.csv"
echo ""

echo "🎯 Advanced Pro Tips:"
echo "- Use timestamped files for historical analysis"
echo "- Combine with shell scripts for automation"
echo "- Integrate with cron for scheduled reports"
echo "- Use different configs for different environments"
echo "- Compress large CSV files for storage"
echo "- Consider uploading reports to cloud storage"
echo "- Use --hypervisors-only for capacity monitoring alerts"
echo "- Parse CSV output with other tools for custom analysis"
echo ""

echo "📖 These examples can be adapted for automation systems like cron, systemd timers, or CI/CD pipelines"
