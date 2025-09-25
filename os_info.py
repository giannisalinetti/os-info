import os
import csv
import argparse
import configparser
import getpass
import sys
from datetime import datetime, timezone

# Conditional import for OpenStack SDK
try:
    import openstack
    OPENSTACK_AVAILABLE = True
except ImportError:
    OPENSTACK_AVAILABLE = False
    openstack = None

def load_config_file(config_path):
    """
    Load OpenStack authentication credentials from a configuration file.
    
    Args:
        config_path (str): Path to the configuration file
        
    Returns:
        dict: Dictionary containing authentication parameters
    """
    config = configparser.ConfigParser()
    
    try:
        config.read(config_path)
        
        if 'openstack' not in config:
            raise ValueError("Configuration file must contain an [openstack] section")
            
        auth_config = {}
        section = config['openstack']
        
        # Map configuration keys to OpenStack connection parameters
        config_mapping = {
            'auth_url': 'auth_url',
            'username': 'username', 
            'password': 'password',
            'project_name': 'project_name',
            'user_domain_name': 'user_domain_name',
            'project_domain_name': 'project_domain_name',
            'region_name': 'region_name',
            'interface': 'interface'
        }
        
        for config_key, param_key in config_mapping.items():
            if config_key in section:
                auth_config[param_key] = section[config_key]
                
        return auth_config
        
    except Exception as e:
        print(f"Error loading configuration file '{config_path}': {e}")
        return None

def get_auth_from_environment():
    """
    Get OpenStack authentication credentials from environment variables.
    
    Returns:
        dict: Dictionary containing authentication parameters
    """
    env_mapping = {
        'OS_AUTH_URL': 'auth_url',
        'OS_USERNAME': 'username',
        'OS_PASSWORD': 'password', 
        'OS_PROJECT_NAME': 'project_name',
        'OS_USER_DOMAIN_NAME': 'user_domain_name',
        'OS_PROJECT_DOMAIN_NAME': 'project_domain_name',
        'OS_REGION_NAME': 'region_name',
        'OS_INTERFACE': 'interface'
    }
    
    auth_config = {}
    for env_var, param_key in env_mapping.items():
        value = os.environ.get(env_var)
        if value:
            auth_config[param_key] = value
            
    return auth_config

def get_auth_interactive():
    """
    Get OpenStack authentication credentials through interactive prompts.
    
    Returns:
        dict: Dictionary containing authentication parameters
    """
    print("\nInteractive authentication setup:")
    print("Enter your OpenStack credentials (required fields marked with *):")
    
    auth_config = {}
    
    # Required fields
    auth_config['auth_url'] = input("* Auth URL: ").strip()
    auth_config['username'] = input("* Username: ").strip()
    auth_config['password'] = getpass.getpass("* Password: ")
    auth_config['project_name'] = input("* Project Name: ").strip()
    
    # Optional fields with defaults
    user_domain = input("User Domain Name [default]: ").strip()
    auth_config['user_domain_name'] = user_domain if user_domain else 'default'
    
    project_domain = input("Project Domain Name [default]: ").strip()
    auth_config['project_domain_name'] = project_domain if project_domain else 'default'
    
    region = input("Region Name (optional): ").strip()
    if region:
        auth_config['region_name'] = region
        
    interface = input("Interface [public]: ").strip()
    auth_config['interface'] = interface if interface else 'public'
    
    return auth_config

def validate_auth_config(auth_config):
    """
    Validate that required authentication parameters are present.
    
    Args:
        auth_config (dict): Authentication configuration
        
    Returns:
        tuple: (is_valid, missing_fields)
    """
    required_fields = ['auth_url', 'username', 'password', 'project_name']
    missing_fields = [field for field in required_fields if not auth_config.get(field)]
    
    return len(missing_fields) == 0, missing_fields

def setup_openstack_connection(auth_method='auto', config_file=None, **kwargs):
    """
    Setup OpenStack connection with various authentication methods.
    
    Args:
        auth_method (str): Authentication method ('env', 'config', 'interactive', 'args', 'auto')
        config_file (str): Path to configuration file (if using 'config' method)
        **kwargs: Direct authentication parameters
        
    Returns:
        openstack.connection.Connection: OpenStack connection object
    """
    if not OPENSTACK_AVAILABLE:
        raise ImportError(
            "OpenStack SDK is not installed. Please install it with:\n"
            "pip install openstacksdk\n"
            "or\n"
            "pip install -r requirements-test.txt"
        )
    
    auth_config = {}
    
    if auth_method == 'auto':
        # Try environment variables first
        auth_config = get_auth_from_environment()
        if not validate_auth_config(auth_config)[0]:
            # Try config file if it exists
            default_config_paths = [
                os.path.expanduser('~/.config/openstack/clouds.ini'),
                os.path.expanduser('~/.openstack/config'),
                './openstack.conf'
            ]
            
            for config_path in default_config_paths:
                if os.path.exists(config_path):
                    file_config = load_config_file(config_path)
                    if file_config and validate_auth_config(file_config)[0]:
                        auth_config = file_config
                        print(f"Using configuration from: {config_path}")
                        break
            
            # If still not valid, try interactive
            if not validate_auth_config(auth_config)[0]:
                print("No valid authentication found in environment or config files.")
                auth_config = get_auth_interactive()
                
    elif auth_method == 'env':
        auth_config = get_auth_from_environment()
        
    elif auth_method == 'config':
        if not config_file:
            raise ValueError("Config file path must be provided when using 'config' auth method")
        auth_config = load_config_file(config_file)
        if not auth_config:
            raise ValueError(f"Failed to load configuration from {config_file}")
            
    elif auth_method == 'interactive':
        auth_config = get_auth_interactive()
        
    elif auth_method == 'args':
        auth_config = kwargs
        
    else:
        raise ValueError(f"Unknown authentication method: {auth_method}")
    
    # Validate configuration
    is_valid, missing_fields = validate_auth_config(auth_config)
    if not is_valid:
        raise ValueError(f"Missing required authentication fields: {', '.join(missing_fields)}")
    
    # Set defaults for optional fields
    auth_config.setdefault('user_domain_name', 'default')
    auth_config.setdefault('project_domain_name', 'default')
    auth_config.setdefault('interface', 'public')
    
    try:
        # Create OpenStack connection
        conn = openstack.connect(**auth_config)
        
        # Test the connection
        conn.authorize()
        print(f"Successfully connected to OpenStack at {auth_config['auth_url']}")
        print(f"Project: {auth_config['project_name']}")
        print(f"User: {auth_config['username']}")
        
        return conn
        
    except Exception as e:
        print(f"Error connecting to OpenStack: {e}")
        raise

def get_openstack_info_and_export_csv(instance_filename="openstack_instances.csv", hypervisor_filename="openstack_hypervisors.csv", conn=None, export_instances=True, export_hypervisors=True):
    """
    Connects to OpenStack, retrieves detailed instance and hypervisor information,
    and exports it to separate CSV files.
    
    Args:
        instance_filename (str): Output filename for instance data CSV
        hypervisor_filename (str): Output filename for hypervisor data CSV  
        conn (openstack.connection.Connection): Existing OpenStack connection (optional)
        export_instances (bool): Whether to export instance data (default: True)
        export_hypervisors (bool): Whether to export hypervisor data (default: True)
    """
    if conn is None:
        print("Error: OpenStack connection not provided")
        return
    
    if not export_instances and not export_hypervisors:
        print("Error: At least one export option (instances or hypervisors) must be enabled")
        return

    # --- Instance Data Retrieval and Export ---
    all_servers = []
    
    if export_instances:
        instance_data = []
        print("\n--- Retrieving All Instance Details ---")
        servers = conn.compute.servers(details=True, all_projects=True)
        all_servers = list(servers)  # Convert to list for reuse in hypervisor processing
        
        if all_servers:
            for server in all_servers:
                print(f"Processing instance: {server.name} ({server.id})")
                
                project = conn.identity.get_project(server.project_id) if server.project_id else None
                flavor = conn.compute.get_flavor(server.flavor['id']) if 'flavor' in server else None
                image = conn.image.get_image(server.image['id']) if 'image' in server else None
                
                network_ips = []
                if server.addresses:
                    for network_name, addresses in server.addresses.items():
                        for address in addresses:
                            network_ips.append(f"{network_name}:{address['addr']} ({address['OS-EXT-IPS:type']})")
                network_str = "; ".join(network_ips)

                volumes_info = []
                if server.attached_volumes:
                    for vol in server.attached_volumes:
                        try:
                            volume_details = conn.block_storage.get_volume(vol['id'])
                            volumes_info.append(f"ID:{volume_details.id}, Name:{volume_details.name}, Size:{volume_details.size}GB")
                        except Exception as e:
                            volumes_info.append(f"ID:{vol['id']}, Details: Error - {e}")
                volumes_str = "; ".join(volumes_info)
                
                uptime_seconds = None
                if server.status == "ACTIVE" and 'OS-SRV-USG:launched_at' in server:
                    launched_at_iso = server['OS-SRV-USG:launched_at']
                    if launched_at_iso:
                        launched_at_dt = datetime.fromisoformat(launched_at_iso.replace('Z', '+00:00'))
                        uptime_seconds = (datetime.now(timezone.utc) - launched_at_dt).total_seconds()
                
                # Retrieve the hypervisor hostname
                hypervisor_hostname = server.to_dict().get('OS-EXT-SRV-ATTR:hypervisor_hostname', 'N/A')
                
                instance_details = {
                    "ID": server.id, "Name": server.name, "Status": server.status,
                    "Power State": server['OS-EXT-STS:power_state'] if 'OS-EXT-STS:power_state' in server else "N/A",
                    "VM State": server['OS-EXT-STS:vm_state'] if 'OS-EXT-STS:vm_state' in server else "N/A",
                    "Project Name": project.name if project else "N/A",
                    "Availability Zone": server['OS-EXT-AZ:availability_zone'] if 'OS-EXT-AZ:availability_zone' in server else "N/A",
                    "Hypervisor Hostname": hypervisor_hostname,
                    "Image Name": image.name if image else "N/A",
                    "Flavor Name": flavor.name if flavor else "N/A",
                    "VCPUs": flavor.vcpus if flavor else "N/A",
                    "RAM (MB)": flavor.ram if flavor else "N/A",
                    "Disk (GB)": flavor.disk if flavor else "N/A",
                    "Uptime (s)": uptime_seconds,
                    "Created At": server.created_at,
                    "Public IP": network_ips[0].split(':')[1].split('(')[0].strip() if network_ips and 'floating' in network_ips[0] else 'N/A',
                    "Network IPs": network_str,
                    "Attached Volumes": volumes_str,
                    "Metadata": str(server.metadata)
                }
                instance_data.append(instance_details)

            if instance_data:
                keys = instance_data[0].keys()
                with open(instance_filename, 'w', newline='') as output_file:
                    dict_writer = csv.DictWriter(output_file, keys)
                    dict_writer.writeheader()
                    dict_writer.writerows(instance_data)
                print(f"Successfully exported instance details to {instance_filename}.")
        else:
            print("No instance data to export.")
    else:
        print("Instance export disabled - skipping instance data collection.")
        # Still need to get server list for hypervisor overcommit calculations
        if export_hypervisors:
            print("Retrieving server information for hypervisor overcommit calculations...")
            servers = conn.compute.servers(details=True, all_projects=True)
            all_servers = list(servers)
    
    print("--------------------------------------------------")

    # --- Hypervisor Data Retrieval and Export ---
    
    if export_hypervisors:
        hypervisor_data = []
        print("\n--- Retrieving All Hypervisor Details ---")
        hypervisors = conn.compute.hypervisors()
        
        if hypervisors:
            for hypervisor in hypervisors:
                print(f"Processing hypervisor: {hypervisor.name}")
                
                # Calculate allocated resources from instances on this hypervisor
                allocated_vcpus = 0
                allocated_memory = 0
                instances_on_hypervisor = []
                
                for server in all_servers:
                    # Check if server is on this hypervisor
                    server_hypervisor = server.to_dict().get('OS-EXT-SRV-ATTR:hypervisor_hostname', '')
                    if server_hypervisor == hypervisor.name and server.status in ['ACTIVE', 'PAUSED', 'SUSPENDED']:
                        instances_on_hypervisor.append(server)
                        
                        # Get flavor details to calculate allocated resources
                        if 'flavor' in server and server.flavor:
                            try:
                                flavor = conn.compute.get_flavor(server.flavor['id'])
                                if flavor:
                                    allocated_vcpus += flavor.vcpus or 0
                                    allocated_memory += flavor.ram or 0
                            except Exception as e:
                                print(f"Warning: Could not get flavor details for server {server.id}: {e}")
                
                # Calculate overcommit ratios
                cpu_overcommit_ratio = (allocated_vcpus / hypervisor.vcpus) if hypervisor.vcpus > 0 else 0
                memory_overcommit_ratio = (allocated_memory / hypervisor.memory_size) if hypervisor.memory_size > 0 else 0
                
                # Calculate physical resource usage vs allocated
                physical_cpu_usage = (hypervisor.vcpus_used / hypervisor.vcpus) * 100 if hypervisor.vcpus > 0 else 0
                physical_memory_usage = (hypervisor.memory_used / hypervisor.memory_size) * 100 if hypervisor.memory_size > 0 else 0
                
                allocated_cpu_percentage = (allocated_vcpus / hypervisor.vcpus) * 100 if hypervisor.vcpus > 0 else 0
                allocated_memory_percentage = (allocated_memory / hypervisor.memory_size) * 100 if hypervisor.memory_size > 0 else 0
                
                hypervisor_details = {
                    "ID": hypervisor.id,
                    "Hostname": hypervisor.name,
                    "Hypervisor Type": hypervisor.hypervisor_type,
                    "State": hypervisor.state,
                    "Status": hypervisor.status,
                    
                    # Physical CPU Information
                    "Physical CPUs": hypervisor.vcpus,
                    "Physical CPUs Used": hypervisor.vcpus_used,
                    "Physical CPU Usage (%)": round(physical_cpu_usage, 2),
                    
                    # Allocated CPU Information
                    "Allocated VCPUs": allocated_vcpus,
                    "Allocated CPU (%)": round(allocated_cpu_percentage, 2),
                    "CPU Overcommit Ratio": round(cpu_overcommit_ratio, 2),
                    
                    # Physical Memory Information
                    "Physical RAM Total (MB)": hypervisor.memory_size,
                    "Physical RAM Used (MB)": hypervisor.memory_used,
                    "Physical RAM Usage (%)": round(physical_memory_usage, 2),
                    
                    # Allocated Memory Information
                    "Allocated RAM (MB)": allocated_memory,
                    "Allocated RAM (%)": round(allocated_memory_percentage, 2),
                    "Memory Overcommit Ratio": round(memory_overcommit_ratio, 2),
                    
                    # Disk Information
                    "Disk Total (GB)": hypervisor.local_disk_size,
                    "Disk Used (GB)": hypervisor.local_disk_used,
                    "Disk Usage (%)": round((hypervisor.local_disk_used / hypervisor.local_disk_size) * 100, 2) if hypervisor.local_disk_size > 0 else 0,
                    
                    # Instance Information
                    "Running VMs": hypervisor.running_vms,
                    "Active Instances": len(instances_on_hypervisor),
                    
                    # Network Information
                    "Host IP": hypervisor.host_ip,
                    
                    # Overcommit Analysis
                    "CPU Overcommitted": "Yes" if cpu_overcommit_ratio > 1.0 else "No",
                    "Memory Overcommitted": "Yes" if memory_overcommit_ratio > 1.0 else "No"
                }
                hypervisor_data.append(hypervisor_details)
            
            if hypervisor_data:
                keys = hypervisor_data[0].keys()
                with open(hypervisor_filename, 'w', newline='') as output_file:
                    dict_writer = csv.DictWriter(output_file, keys)
                    dict_writer.writeheader()
                    dict_writer.writerows(hypervisor_data)
                print(f"Successfully exported hypervisor details to {hypervisor_filename}.")
        else:
            print("No hypervisor data to export.")
    else:
        print("Hypervisor export disabled - skipping hypervisor data collection.")

def parse_arguments():
    """
    Parse command line arguments for authentication and output options.
    
    Returns:
        argparse.Namespace: Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description='Retrieve OpenStack instance and hypervisor information and export to CSV files.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Authentication Methods:
  auto        : Try environment variables, then config files, then interactive (default)
  env         : Use environment variables only
  config      : Use configuration file
  interactive : Prompt for credentials interactively
  args        : Use command line arguments

Examples:
  # Use automatic authentication (try env vars, config files, then interactive)
  python os_info.py
  
  # Use specific config file
  python os_info.py --auth-method config --config-file /path/to/openstack.conf
  
  # Use command line arguments
  python os_info.py --auth-method args --auth-url https://keystone.example.com:5000/v3 \\
                    --username myuser --password mypass --project-name myproject
  
  # Use interactive mode
  python os_info.py --auth-method interactive
  
Configuration File Format (openstack.conf):
  [openstack]
  auth_url = https://keystone.example.com:5000/v3
  username = myuser
  password = mypass
  project_name = myproject
  user_domain_name = default
  project_domain_name = default
  region_name = RegionOne
  interface = public
        """
    )
    
    # Authentication method
    parser.add_argument(
        '--auth-method', 
        choices=['auto', 'env', 'config', 'interactive', 'args'],
        default='auto',
        help='Authentication method to use (default: auto)'
    )
    
    # Configuration file
    parser.add_argument(
        '--config-file',
        help='Path to configuration file (required when using --auth-method config)'
    )
    
    # Direct authentication arguments
    auth_group = parser.add_argument_group('Authentication Arguments')
    auth_group.add_argument('--auth-url', help='OpenStack authentication URL')
    auth_group.add_argument('--username', help='OpenStack username')
    auth_group.add_argument('--password', help='OpenStack password')
    auth_group.add_argument('--project-name', help='OpenStack project name')
    auth_group.add_argument('--user-domain-name', default='default', help='User domain name (default: default)')
    auth_group.add_argument('--project-domain-name', default='default', help='Project domain name (default: default)')
    auth_group.add_argument('--region-name', help='OpenStack region name')
    auth_group.add_argument('--interface', default='public', choices=['public', 'internal', 'admin'], help='OpenStack interface (default: public)')
    
    # Output options
    output_group = parser.add_argument_group('Output Options')
    output_group.add_argument('--instances-file', default='openstack_instances.csv', help='Output filename for instance data (default: openstack_instances.csv)')
    output_group.add_argument('--hypervisors-file', default='openstack_hypervisors.csv', help='Output filename for hypervisor data (default: openstack_hypervisors.csv)')
    output_group.add_argument('--export-instances', action='store_true', default=True, help='Export instance data (default: True)')
    output_group.add_argument('--no-export-instances', dest='export_instances', action='store_false', help='Skip instance data export')
    output_group.add_argument('--export-hypervisors', action='store_true', default=True, help='Export hypervisor data (default: True)')
    output_group.add_argument('--no-export-hypervisors', dest='export_hypervisors', action='store_false', help='Skip hypervisor data export')
    output_group.add_argument('--instances-only', action='store_true', help='Export only instance data (shortcut for --no-export-hypervisors)')
    output_group.add_argument('--hypervisors-only', action='store_true', help='Export only hypervisor data (shortcut for --no-export-instances)')
    
    return parser.parse_args()

if __name__ == "__main__":
    try:
        # Parse command line arguments
        args = parse_arguments()
        
        # Check if OpenStack SDK is available
        if not OPENSTACK_AVAILABLE:
            print("❌ OpenStack SDK is not installed!")
            print("\nTo use this tool, please install the OpenStack SDK:")
            print("  pip install openstacksdk")
            print("\nOr install all development dependencies:")
            print("  pip install -r requirements-test.txt")
            print("\nFor more information, see the README.md file.")
            sys.exit(1)
        
        # Handle export shortcuts
        if args.instances_only:
            args.export_instances = True
            args.export_hypervisors = False
        elif args.hypervisors_only:
            args.export_instances = False
            args.export_hypervisors = True
        
        # Setup authentication based on method
        if args.auth_method == 'args':
            # Use command line arguments
            auth_kwargs = {}
            if args.auth_url:
                auth_kwargs['auth_url'] = args.auth_url
            if args.username:
                auth_kwargs['username'] = args.username
            if args.password:
                auth_kwargs['password'] = args.password
            if args.project_name:
                auth_kwargs['project_name'] = args.project_name
            if args.user_domain_name:
                auth_kwargs['user_domain_name'] = args.user_domain_name
            if args.project_domain_name:
                auth_kwargs['project_domain_name'] = args.project_domain_name
            if args.region_name:
                auth_kwargs['region_name'] = args.region_name
            if args.interface:
                auth_kwargs['interface'] = args.interface
                
            conn = setup_openstack_connection(
                auth_method='args',
                **auth_kwargs
            )
        else:
            # Use other authentication methods
            conn = setup_openstack_connection(
                auth_method=args.auth_method,
                config_file=args.config_file
            )
        
        # Run the main function with the established connection
        get_openstack_info_and_export_csv(
            instance_filename=args.instances_file,
            hypervisor_filename=args.hypervisors_file,
            conn=conn,
            export_instances=args.export_instances,
            export_hypervisors=args.export_hypervisors
        )
        
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
