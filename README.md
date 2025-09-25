# OpenStack Information Export Tool

A comprehensive Python script to retrieve detailed OpenStack instance and hypervisor information and export it to CSV files. The tool supports multiple authentication methods for flexibility in different environments.

## Features

- Export detailed instance information (VMs, networks, volumes, etc.)
- Export hypervisor statistics and utilization
- Multiple authentication methods (environment variables, config files, command line, interactive)
- Automatic authentication method detection
- Comprehensive error handling and validation
- CSV output for easy data analysis

## Requirements

- Python 3.6+
- OpenStack SDK (`python-openstacksdk`)

### Installation

```bash
# Install production dependencies
pip install -r requirements.txt

# Or install OpenStack SDK directly
pip install openstacksdk

# For development (includes testing tools)
make install-dev
```

## Authentication Methods

The tool supports five different authentication methods:

### 1. Automatic (Default)
The script automatically tries different authentication methods in order:
1. Environment variables
2. Configuration files (in standard locations)
3. Interactive prompts

```bash
python os_info.py
```

### 2. Environment Variables
Use standard OpenStack environment variables:

```bash
export OS_AUTH_URL=https://keystone.example.com:5000/v3
export OS_USERNAME=your_username
export OS_PASSWORD=your_password
export OS_PROJECT_NAME=your_project
export OS_USER_DOMAIN_NAME=default
export OS_PROJECT_DOMAIN_NAME=default
export OS_REGION_NAME=RegionOne
export OS_INTERFACE=public

python os_info.py --auth-method env
```

### 3. Configuration File
Create a configuration file with your credentials:

```bash
# Copy the example and edit with your credentials
cp openstack.conf.example openstack.conf

python os_info.py --auth-method config --config-file openstack.conf
```

**Configuration file format:**
```ini
[openstack]
auth_url = https://keystone.example.com:5000/v3
username = your_username
password = your_password
project_name = your_project
user_domain_name = default
project_domain_name = default
region_name = RegionOne
interface = public
```

**Default configuration file locations:**
- `~/.config/openstack/clouds.ini`
- `~/.openstack/config`
- `./openstack.conf` (current directory)

### 4. Command Line Arguments
Pass credentials directly via command line:

```bash
python os_info.py --auth-method args \
    --auth-url https://keystone.example.com:5000/v3 \
    --username your_username \
    --password your_password \
    --project-name your_project \
    --user-domain-name default \
    --project-domain-name default \
    --region-name RegionOne \
    --interface public
```

### 5. Interactive Mode
Prompt for credentials interactively:

```bash
python os_info.py --auth-method interactive
```

## Command Line Options

```
usage: os_info.py [-h] [--auth-method {auto,env,config,interactive,args}]
                  [--config-file CONFIG_FILE] [--auth-url AUTH_URL]
                  [--username USERNAME] [--password PASSWORD]
                  [--project-name PROJECT_NAME]
                  [--user-domain-name USER_DOMAIN_NAME]
                  [--project-domain-name PROJECT_DOMAIN_NAME]
                  [--region-name REGION_NAME]
                  [--interface {public,internal,admin}]
                  [--instances-file INSTANCES_FILE]
                  [--hypervisors-file HYPERVISORS_FILE]
                  [--export-instances] [--no-export-instances]
                  [--export-hypervisors] [--no-export-hypervisors]
                  [--instances-only] [--hypervisors-only]

Authentication Arguments:
  --auth-url AUTH_URL   OpenStack authentication URL
  --username USERNAME   OpenStack username
  --password PASSWORD   OpenStack password
  --project-name PROJECT_NAME
                        OpenStack project name
  --user-domain-name USER_DOMAIN_NAME
                        User domain name (default: default)
  --project-domain-name PROJECT_DOMAIN_NAME
                        Project domain name (default: default)
  --region-name REGION_NAME
                        OpenStack region name
  --interface {public,internal,admin}
                        OpenStack interface (default: public)

Output Options:
  --instances-file INSTANCES_FILE
                        Output filename for instance data (default:
                        openstack_instances.csv)
  --hypervisors-file HYPERVISORS_FILE
                        Output filename for hypervisor data (default:
                        openstack_hypervisors.csv)
  --export-instances    Export instance data (default: True)
  --no-export-instances Skip instance data export
  --export-hypervisors  Export hypervisor data (default: True)
  --no-export-hypervisors
                        Skip hypervisor data export
  --instances-only      Export only instance data (shortcut for --no-export-hypervisors)
  --hypervisors-only    Export only hypervisor data (shortcut for --no-export-instances)
```

## Output Files

### Instance Data (openstack_instances.csv)
Contains detailed information about all instances including:
- Basic instance details (ID, name, status, power state)
- Project and user information
- Flavor details (VCPUs, RAM, disk)
- Image information
- Network configurations and IP addresses
- Attached volumes
- Hypervisor placement
- Uptime calculations
- Metadata

### Hypervisor Data (openstack_hypervisors.csv)
Contains comprehensive hypervisor statistics including:
- **Hypervisor identification**: ID, hostname, type, state, status
- **Physical CPU metrics**: Total CPUs, used CPUs, usage percentage
- **CPU allocation metrics**: Allocated VCPUs, allocation percentage, overcommit ratio
- **Physical memory metrics**: Total RAM, used RAM, usage percentage  
- **Memory allocation metrics**: Allocated RAM, allocation percentage, overcommit ratio
- **Disk utilization**: Total disk, used disk, usage percentage
- **Instance counts**: Running VMs, active instances
- **Overcommit analysis**: CPU/Memory overcommit flags and ratios
- **Network information**: Host IP address

#### Understanding Overcommit Ratios
- **CPU Overcommit Ratio**: Allocated VCPUs ÷ Physical CPUs
- **Memory Overcommit Ratio**: Allocated RAM ÷ Physical RAM
- **Ratio > 1.0**: Resources are overcommitted
- **Ratio ≤ 1.0**: Resources are not overcommitted

## Data Separation Benefits

The tool provides flexible export options to optimize for different use cases:

### **Why Separate Instances and Hypervisors?**

1. **Performance Optimization**
   - **Instances-only**: Faster execution when you only need VM inventory
   - **Hypervisors-only**: Quick capacity planning without processing all VMs
   - **Reduced API calls**: Skip unnecessary data retrieval

2. **Use Case Specialization**
   - **Instance CSV**: Perfect for VM inventory, billing, user management
   - **Hypervisor CSV**: Ideal for capacity planning, resource monitoring, infrastructure analysis

3. **Data Size Management**
   - **Large environments**: Separate files prevent overwhelming spreadsheet applications
   - **Focused analysis**: Import only relevant data into analysis tools
   - **Storage efficiency**: Store only needed data

4. **Operational Workflows**
   - **Different teams**: Infrastructure teams need hypervisor data, application teams need instance data
   - **Different schedules**: Run capacity reports less frequently than inventory updates
   - **Different consumers**: Feed different systems with appropriate data

### **When to Use Each Option**

| Use Case | Recommended Command | Benefit |
|----------|---------------------|---------|
| Daily VM inventory | `--instances-only` | Fast execution, focused data |
| Capacity planning | `--hypervisors-only` | Infrastructure focus, overcommit analysis |
| Complete audit | Default (both) | Comprehensive data collection |
| Performance monitoring | `--hypervisors-only` | Resource utilization trends |
| Billing/chargeback | `--instances-only` | User and project resource usage |
| Troubleshooting | Both with custom filenames | Correlation between VMs and hosts |

## Usage Examples

### Basic Usage
```bash
# Export both instances and hypervisors (default)
python os_info.py

# Use specific config file
python os_info.py --auth-method config --config-file /path/to/config

# Use environment variables only
python os_info.py --auth-method env
```

### Selective Data Export
```bash
# Export only instance data
python os_info.py --instances-only

# Export only hypervisor data
python os_info.py --hypervisors-only

# Export only instances (alternative syntax)
python os_info.py --no-export-hypervisors

# Export only hypervisors (alternative syntax)
python os_info.py --no-export-instances

# Custom output filenames
python os_info.py --instances-file my_instances.csv --hypervisors-file my_hypervisors.csv

# Export instances only with custom filename
python os_info.py --instances-only --instances-file vm_inventory.csv
```

### Authentication Examples
```bash
# Interactive authentication
python os_info.py --auth-method interactive

# Command line authentication with custom region
python os_info.py --auth-method args \
    --auth-url https://keystone.example.com:5000/v3 \
    --username myuser \
    --password mypass \
    --project-name myproject \
    --region-name us-east-1

# Export only hypervisors with specific authentication
python os_info.py --hypervisors-only --auth-method config --config-file prod.conf
```

### Advanced Usage
```bash
# Performance focused: Skip instances to get hypervisor data faster
python os_info.py --hypervisors-only --hypervisors-file capacity_report.csv

# Inventory focused: Get detailed instance information only
python os_info.py --instances-only --instances-file detailed_inventory.csv

# Different files for different purposes
python os_info.py \
    --instances-file "instances_$(date +%Y%m%d).csv" \
    --hypervisors-file "hypervisors_$(date +%Y%m%d).csv"
```

## Error Handling

The script includes comprehensive error handling for:
- Missing authentication credentials
- Invalid configuration files
- Network connectivity issues
- API authentication failures
- Permission errors

## Security Considerations

- Avoid passing passwords via command line arguments in production
- Use configuration files with proper file permissions (600)
- Consider using application credentials instead of user passwords
- Environment variables are recommended for automated deployments

## Troubleshooting

### Common Issues

1. **Missing credentials**: Use `--auth-method interactive` to verify credentials
2. **Network issues**: Check connectivity to the auth_url
3. **Permission errors**: Ensure your user has required OpenStack permissions
4. **File not found**: Check configuration file paths and permissions

### Debug Mode

For additional debugging information, you can modify the script to enable OpenStack SDK debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Development

### Setup Development Environment

```bash
# Clone the repository
git clone <repository-url>
cd os-info

# Install development dependencies
make install-dev

# Run tests
make test

# Run with coverage
make test-coverage

# Format code
make format

# Clean up generated files
make clean
```

### Project Structure

```
os-info/
├── os_info.py              # Main application
├── test_os_info.py         # Test suite
├── README.md              # Documentation
├── requirements.txt        # Production dependencies
├── requirements-test.txt   # Testing dependencies
├── pytest.ini            # Test configuration
├── Makefile              # Development commands
├── openstack.conf.example # Configuration template
├── test_config.conf      # Test configuration
└── .gitignore            # Git ignore rules
```

### Code Quality

The project follows Python best practices:
- **PEP 8** compliance
- **Type hints** where appropriate
- **Comprehensive testing** with pytest
- **Code formatting** with black and isort
- **Linting** with flake8

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `make test`
5. Format code: `make format`
6. Submit a pull request

## License

This project is open source and available under the MIT License.
