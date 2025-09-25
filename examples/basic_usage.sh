#!/bin/bash
# Basic Usage Examples for OpenStack Information Export Tool
# This script demonstrates common usage patterns

echo "🚀 OpenStack Info Tool - Basic Usage Examples"
echo "=============================================="

# Check if the script exists
if [ ! -f "../os_info.py" ]; then
    echo "❌ Error: os_info.py not found. Run this script from the examples directory."
    exit 1
fi

echo ""
echo "📋 Example 1: Show help information"
echo "Command: python ../os_info.py --help"
echo "---"
python ../os_info.py --help | head -20
echo ""

echo "📋 Example 2: Export both instances and hypervisors (default)"
echo "Command: python ../os_info.py"
echo "Description: Exports complete OpenStack information to CSV files"
echo ""

echo "📋 Example 3: Export only instance data"
echo "Command: python ../os_info.py --instances-only"
echo "Description: Fast execution for VM inventory only"
echo ""

echo "📋 Example 4: Export only hypervisor data"
echo "Command: python ../os_info.py --hypervisors-only"
echo "Description: Focus on infrastructure capacity and overcommit analysis"
echo ""

echo "📋 Example 5: Custom output filenames"
echo "Command: python ../os_info.py --instances-file vm_inventory.csv --hypervisors-file capacity_report.csv"
echo "Description: Use descriptive filenames for different purposes"
echo ""

echo "📋 Example 6: Using environment variables for authentication"
echo "Commands:"
echo "export OS_AUTH_URL=https://keystone.example.com:5000/v3"
echo "export OS_USERNAME=your_username"
echo "export OS_PASSWORD=your_password"
echo "export OS_PROJECT_NAME=your_project"
echo "export OS_USER_DOMAIN_NAME=default"
echo "export OS_PROJECT_DOMAIN_NAME=default"
echo "python ../os_info.py --auth-method env"
echo ""

echo "📋 Example 7: Using configuration file"
echo "Commands:"
echo "cp openstack.conf.example openstack.conf"
echo "# Edit openstack.conf with your credentials"
echo "python ../os_info.py --auth-method config --config-file openstack.conf"
echo ""

echo "📋 Example 8: Interactive authentication"
echo "Command: python ../os_info.py --auth-method interactive"
echo "Description: Prompts for credentials - good for testing"
echo ""

echo "🎯 Pro Tips:"
echo "- Use --instances-only for faster daily VM inventory"
echo "- Use --hypervisors-only for capacity planning"
echo "- Use configuration files for automated scripts"
echo "- Use environment variables in CI/CD pipelines"
echo ""

echo "📖 For more examples, see advanced_usage.sh and the automation/ directory"
