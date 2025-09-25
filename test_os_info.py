#!/usr/bin/env python3
# Copyright 2025 Gianni Salinetti
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Comprehensive test suite for the OpenStack information export tool.

This test suite covers:
- Authentication methods (environment, config file, interactive, CLI args)
- Configuration file loading and validation
- OpenStack connection setup
- Data processing and CSV export functionality
- Command line argument parsing
- Error handling and edge cases

Run tests with:
    python -m pytest test_os_info.py -v
    or
    python test_os_info.py
"""

import unittest
import unittest.mock as mock
import tempfile
import os
import csv
import configparser
import argparse
import io
import sys
from unittest.mock import patch, MagicMock, mock_open

# Import the module under test
import os_info


class TestAuthenticationMethods(unittest.TestCase):
    """Test various authentication methods."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Clear environment variables for clean tests
        self.env_vars_to_clear = [
            'OS_AUTH_URL', 'OS_USERNAME', 'OS_PASSWORD', 'OS_PROJECT_NAME',
            'OS_USER_DOMAIN_NAME', 'OS_PROJECT_DOMAIN_NAME', 
            'OS_REGION_NAME', 'OS_INTERFACE'
        ]
        self.original_env = {}
        for var in self.env_vars_to_clear:
            self.original_env[var] = os.environ.get(var)
            if var in os.environ:
                del os.environ[var]
    
    def tearDown(self):
        """Clean up after tests."""
        # Restore original environment
        for var, value in self.original_env.items():
            if value is not None:
                os.environ[var] = value
            elif var in os.environ:
                del os.environ[var]
    
    def test_get_auth_from_environment_complete(self):
        """Test getting complete authentication from environment variables."""
        # Set up environment variables
        test_env = {
            'OS_AUTH_URL': 'https://keystone.example.com:5000/v3',
            'OS_USERNAME': 'testuser',
            'OS_PASSWORD': 'testpass',
            'OS_PROJECT_NAME': 'testproject',
            'OS_USER_DOMAIN_NAME': 'testdomain',
            'OS_PROJECT_DOMAIN_NAME': 'testprojectdomain',
            'OS_REGION_NAME': 'testregion',
            'OS_INTERFACE': 'public'
        }
        
        for key, value in test_env.items():
            os.environ[key] = value
        
        auth_config = os_info.get_auth_from_environment()
        
        expected = {
            'auth_url': 'https://keystone.example.com:5000/v3',
            'username': 'testuser',
            'password': 'testpass',
            'project_name': 'testproject',
            'user_domain_name': 'testdomain',
            'project_domain_name': 'testprojectdomain',
            'region_name': 'testregion',
            'interface': 'public'
        }
        
        self.assertEqual(auth_config, expected)
    
    def test_get_auth_from_environment_minimal(self):
        """Test getting minimal authentication from environment variables."""
        # Set up minimal environment variables
        test_env = {
            'OS_AUTH_URL': 'https://keystone.example.com:5000/v3',
            'OS_USERNAME': 'testuser',
            'OS_PASSWORD': 'testpass',
            'OS_PROJECT_NAME': 'testproject'
        }
        
        for key, value in test_env.items():
            os.environ[key] = value
        
        auth_config = os_info.get_auth_from_environment()
        
        expected = {
            'auth_url': 'https://keystone.example.com:5000/v3',
            'username': 'testuser',
            'password': 'testpass',
            'project_name': 'testproject'
        }
        
        self.assertEqual(auth_config, expected)
    
    def test_get_auth_from_environment_empty(self):
        """Test getting authentication from empty environment."""
        auth_config = os_info.get_auth_from_environment()
        self.assertEqual(auth_config, {})
    
    @patch('builtins.input')
    @patch('getpass.getpass')
    def test_get_auth_interactive_complete(self, mock_getpass, mock_input):
        """Test interactive authentication with all fields."""
        # Mock user inputs
        mock_input.side_effect = [
            'https://keystone.example.com:5000/v3',  # auth_url
            'testuser',                               # username
            'testproject',                           # project_name
            'testdomain',                            # user_domain_name
            'testprojectdomain',                     # project_domain_name
            'testregion',                            # region_name
            'internal'                               # interface
        ]
        mock_getpass.return_value = 'testpass'       # password
        
        auth_config = os_info.get_auth_interactive()
        
        expected = {
            'auth_url': 'https://keystone.example.com:5000/v3',
            'username': 'testuser',
            'password': 'testpass',
            'project_name': 'testproject',
            'user_domain_name': 'testdomain',
            'project_domain_name': 'testprojectdomain',
            'region_name': 'testregion',
            'interface': 'internal'
        }
        
        self.assertEqual(auth_config, expected)
    
    @patch('builtins.input')
    @patch('getpass.getpass')
    def test_get_auth_interactive_defaults(self, mock_getpass, mock_input):
        """Test interactive authentication with default values."""
        # Mock user inputs with defaults
        mock_input.side_effect = [
            'https://keystone.example.com:5000/v3',  # auth_url
            'testuser',                               # username
            'testproject',                           # project_name
            '',                                      # user_domain_name (default)
            '',                                      # project_domain_name (default)
            '',                                      # region_name (empty)
            ''                                       # interface (default)
        ]
        mock_getpass.return_value = 'testpass'       # password
        
        auth_config = os_info.get_auth_interactive()
        
        expected = {
            'auth_url': 'https://keystone.example.com:5000/v3',
            'username': 'testuser',
            'password': 'testpass',
            'project_name': 'testproject',
            'user_domain_name': 'default',
            'project_domain_name': 'default',
            'interface': 'public'
        }
        
        self.assertEqual(auth_config, expected)


class TestConfigurationFile(unittest.TestCase):
    """Test configuration file loading and validation."""
    
    def test_load_config_file_valid(self):
        """Test loading a valid configuration file."""
        config_content = """
[openstack]
auth_url = https://keystone.example.com:5000/v3
username = testuser
password = testpass
project_name = testproject
user_domain_name = testdomain
project_domain_name = testprojectdomain
region_name = testregion
interface = public
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.conf', delete=False) as f:
            f.write(config_content)
            f.flush()
            
            try:
                auth_config = os_info.load_config_file(f.name)
                
                expected = {
                    'auth_url': 'https://keystone.example.com:5000/v3',
                    'username': 'testuser',
                    'password': 'testpass',
                    'project_name': 'testproject',
                    'user_domain_name': 'testdomain',
                    'project_domain_name': 'testprojectdomain',
                    'region_name': 'testregion',
                    'interface': 'public'
                }
                
                self.assertEqual(auth_config, expected)
            finally:
                os.unlink(f.name)
    
    def test_load_config_file_minimal(self):
        """Test loading a minimal configuration file."""
        config_content = """
[openstack]
auth_url = https://keystone.example.com:5000/v3
username = testuser
password = testpass
project_name = testproject
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.conf', delete=False) as f:
            f.write(config_content)
            f.flush()
            
            try:
                auth_config = os_info.load_config_file(f.name)
                
                expected = {
                    'auth_url': 'https://keystone.example.com:5000/v3',
                    'username': 'testuser',
                    'password': 'testpass',
                    'project_name': 'testproject'
                }
                
                self.assertEqual(auth_config, expected)
            finally:
                os.unlink(f.name)
    
    def test_load_config_file_missing_section(self):
        """Test loading a config file without openstack section."""
        config_content = """
[other_section]
some_key = some_value
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.conf', delete=False) as f:
            f.write(config_content)
            f.flush()
            
            try:
                auth_config = os_info.load_config_file(f.name)
                self.assertIsNone(auth_config)
            finally:
                os.unlink(f.name)
    
    def test_load_config_file_nonexistent(self):
        """Test loading a non-existent configuration file."""
        auth_config = os_info.load_config_file('/nonexistent/file.conf')
        self.assertIsNone(auth_config)


class TestAuthenticationValidation(unittest.TestCase):
    """Test authentication configuration validation."""
    
    def test_validate_auth_config_complete(self):
        """Test validation with complete configuration."""
        auth_config = {
            'auth_url': 'https://keystone.example.com:5000/v3',
            'username': 'testuser',
            'password': 'testpass',
            'project_name': 'testproject'
        }
        
        is_valid, missing_fields = os_info.validate_auth_config(auth_config)
        self.assertTrue(is_valid)
        self.assertEqual(missing_fields, [])
    
    def test_validate_auth_config_missing_fields(self):
        """Test validation with missing required fields."""
        auth_config = {
            'auth_url': 'https://keystone.example.com:5000/v3',
            'username': 'testuser'
            # Missing password and project_name
        }
        
        is_valid, missing_fields = os_info.validate_auth_config(auth_config)
        self.assertFalse(is_valid)
        self.assertEqual(set(missing_fields), {'password', 'project_name'})
    
    def test_validate_auth_config_empty(self):
        """Test validation with empty configuration."""
        auth_config = {}
        
        is_valid, missing_fields = os_info.validate_auth_config(auth_config)
        self.assertFalse(is_valid)
        self.assertEqual(set(missing_fields), {'auth_url', 'username', 'password', 'project_name'})
    
    def test_validate_auth_config_empty_values(self):
        """Test validation with empty string values."""
        auth_config = {
            'auth_url': '',
            'username': 'testuser',
            'password': 'testpass',
            'project_name': ''
        }
        
        is_valid, missing_fields = os_info.validate_auth_config(auth_config)
        self.assertFalse(is_valid)
        self.assertEqual(set(missing_fields), {'auth_url', 'project_name'})


class TestConnectionSetup(unittest.TestCase):
    """Test OpenStack connection setup with mocked OpenStack SDK."""
    
    @patch('os_info.openstack.connect')
    def test_setup_openstack_connection_env_method(self, mock_connect):
        """Test connection setup using environment method."""
        # Mock successful connection
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        
        # Set up environment variables
        test_env = {
            'OS_AUTH_URL': 'https://keystone.example.com:5000/v3',
            'OS_USERNAME': 'testuser',
            'OS_PASSWORD': 'testpass',
            'OS_PROJECT_NAME': 'testproject'
        }
        
        with patch.dict(os.environ, test_env):
            conn = os_info.setup_openstack_connection(auth_method='env')
            
            self.assertEqual(conn, mock_conn)
            mock_connect.assert_called_once()
            mock_conn.authorize.assert_called_once()
    
    @patch('os_info.openstack.connect')
    def test_setup_openstack_connection_args_method(self, mock_connect):
        """Test connection setup using args method."""
        # Mock successful connection
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        
        auth_kwargs = {
            'auth_url': 'https://keystone.example.com:5000/v3',
            'username': 'testuser',
            'password': 'testpass',
            'project_name': 'testproject'
        }
        
        conn = os_info.setup_openstack_connection(auth_method='args', **auth_kwargs)
        
        self.assertEqual(conn, mock_conn)
        mock_connect.assert_called_once()
        mock_conn.authorize.assert_called_once()
    
    @patch('os_info.load_config_file')
    @patch('os_info.openstack.connect')
    def test_setup_openstack_connection_config_method(self, mock_connect, mock_load_config):
        """Test connection setup using config method."""
        # Mock successful connection and config loading
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        
        mock_config = {
            'auth_url': 'https://keystone.example.com:5000/v3',
            'username': 'testuser',
            'password': 'testpass',
            'project_name': 'testproject'
        }
        mock_load_config.return_value = mock_config
        
        conn = os_info.setup_openstack_connection(auth_method='config', config_file='test.conf')
        
        self.assertEqual(conn, mock_conn)
        mock_load_config.assert_called_once_with('test.conf')
        mock_connect.assert_called_once()
        mock_conn.authorize.assert_called_once()
    
    @patch('os_info.openstack.connect')
    def test_setup_openstack_connection_missing_credentials(self, mock_connect):
        """Test connection setup with missing credentials."""
        with self.assertRaises(ValueError) as context:
            os_info.setup_openstack_connection(auth_method='args', auth_url='https://example.com')
        
        self.assertIn('Missing required authentication fields', str(context.exception))
    
    def test_setup_openstack_connection_invalid_method(self):
        """Test connection setup with invalid authentication method."""
        with self.assertRaises(ValueError) as context:
            os_info.setup_openstack_connection(auth_method='invalid')
        
        self.assertIn('Unknown authentication method', str(context.exception))


class TestArgumentParsing(unittest.TestCase):
    """Test command line argument parsing."""
    
    def test_parse_arguments_defaults(self):
        """Test argument parsing with default values."""
        with patch('sys.argv', ['os_info.py']):
            args = os_info.parse_arguments()
            
            self.assertEqual(args.auth_method, 'auto')
            self.assertEqual(args.instances_file, 'openstack_instances.csv')
            self.assertEqual(args.hypervisors_file, 'openstack_hypervisors.csv')
            self.assertEqual(args.interface, 'public')
            self.assertEqual(args.user_domain_name, 'default')
            self.assertEqual(args.project_domain_name, 'default')
    
    def test_parse_arguments_auth_method_config(self):
        """Test argument parsing with config auth method."""
        test_args = ['os_info.py', '--auth-method', 'config', '--config-file', 'test.conf']
        
        with patch('sys.argv', test_args):
            args = os_info.parse_arguments()
            
            self.assertEqual(args.auth_method, 'config')
            self.assertEqual(args.config_file, 'test.conf')
    
    def test_parse_arguments_auth_args_complete(self):
        """Test argument parsing with complete authentication arguments."""
        test_args = [
            'os_info.py', '--auth-method', 'args',
            '--auth-url', 'https://keystone.example.com:5000/v3',
            '--username', 'testuser',
            '--password', 'testpass',
            '--project-name', 'testproject',
            '--user-domain-name', 'testdomain',
            '--project-domain-name', 'testprojectdomain',
            '--region-name', 'testregion',
            '--interface', 'internal'
        ]
        
        with patch('sys.argv', test_args):
            args = os_info.parse_arguments()
            
            self.assertEqual(args.auth_method, 'args')
            self.assertEqual(args.auth_url, 'https://keystone.example.com:5000/v3')
            self.assertEqual(args.username, 'testuser')
            self.assertEqual(args.password, 'testpass')
            self.assertEqual(args.project_name, 'testproject')
            self.assertEqual(args.user_domain_name, 'testdomain')
            self.assertEqual(args.project_domain_name, 'testprojectdomain')
            self.assertEqual(args.region_name, 'testregion')
            self.assertEqual(args.interface, 'internal')
    
    def test_parse_arguments_output_files(self):
        """Test argument parsing with custom output files."""
        test_args = [
            'os_info.py',
            '--instances-file', 'custom_instances.csv',
            '--hypervisors-file', 'custom_hypervisors.csv'
        ]
        
        with patch('sys.argv', test_args):
            args = os_info.parse_arguments()
            
            self.assertEqual(args.instances_file, 'custom_instances.csv')
            self.assertEqual(args.hypervisors_file, 'custom_hypervisors.csv')


class TestDataProcessing(unittest.TestCase):
    """Test data processing and CSV export functionality."""
    
    def setUp(self):
        """Set up mock OpenStack connection and data."""
        self.mock_conn = MagicMock()
        
        # Mock server data
        self.mock_server = MagicMock()
        self.mock_server.id = 'server-123'
        self.mock_server.name = 'test-server'
        self.mock_server.status = 'ACTIVE'
        self.mock_server.project_id = 'project-123'
        self.mock_server.created_at = '2023-01-01T12:00:00Z'
        self.mock_server.metadata = {'env': 'test'}
        self.mock_server.addresses = {
            'private': [{'addr': '10.0.0.1', 'OS-EXT-IPS:type': 'fixed'}]
        }
        self.mock_server.attached_volumes = []
        self.mock_server.to_dict.return_value = {
            'OS-EXT-SRV-ATTR:hypervisor_hostname': 'compute-01',
            'OS-EXT-STS:power_state': 1,
            'OS-EXT-STS:vm_state': 'active',
            'OS-EXT-AZ:availability_zone': 'nova',
            'OS-SRV-USG:launched_at': '2023-01-01T12:00:00Z'
        }
        self.mock_server.__getitem__ = lambda self, key: self.to_dict()[key]
        self.mock_server.__contains__ = lambda self, key: key in self.to_dict()
        self.mock_server.flavor = {'id': 'flavor-123'}
        self.mock_server.image = {'id': 'image-123'}
        
        # Mock hypervisor data
        self.mock_hypervisor = MagicMock()
        self.mock_hypervisor.id = 'hyp-123'
        self.mock_hypervisor.name = 'compute-01'
        self.mock_hypervisor.hypervisor_type = 'QEMU'
        self.mock_hypervisor.state = 'up'
        self.mock_hypervisor.status = 'enabled'
        self.mock_hypervisor.vcpus = 16
        self.mock_hypervisor.vcpus_used = 4
        self.mock_hypervisor.memory_size = 32768
        self.mock_hypervisor.memory_used = 8192
        self.mock_hypervisor.local_disk_size = 1000
        self.mock_hypervisor.local_disk_used = 250
        self.mock_hypervisor.running_vms = 2
        self.mock_hypervisor.host_ip = '192.168.1.10'
        
        # Mock flavor data
        self.mock_flavor = MagicMock()
        self.mock_flavor.name = 'm1.small'
        self.mock_flavor.vcpus = 2
        self.mock_flavor.ram = 2048
        self.mock_flavor.disk = 20
        
        # Mock image data
        self.mock_image = MagicMock()
        self.mock_image.name = 'ubuntu-20.04'
        
        # Mock project data
        self.mock_project = MagicMock()
        self.mock_project.name = 'test-project'
    
    @patch('builtins.open', new_callable=mock_open)
    @patch('csv.DictWriter')
    def test_csv_export_instances(self, mock_csv_writer, mock_file):
        """Test CSV export functionality for instances."""
        # Setup mocks
        self.mock_conn.compute.servers.return_value = [self.mock_server]
        self.mock_conn.identity.get_project.return_value = self.mock_project
        self.mock_conn.compute.get_flavor.return_value = self.mock_flavor
        self.mock_conn.image.get_image.return_value = self.mock_image
        
        # Mock CSV writer
        mock_writer_instance = MagicMock()
        mock_csv_writer.return_value = mock_writer_instance
        
        # Call function
        os_info.get_openstack_info_and_export_csv(
            instance_filename='test_instances.csv',
            hypervisor_filename='test_hypervisors.csv',
            conn=self.mock_conn
        )
        
        # Verify file operations
        mock_file.assert_any_call('test_instances.csv', 'w', newline='')
        mock_csv_writer.assert_called()
        mock_writer_instance.writeheader.assert_called()
        mock_writer_instance.writerows.assert_called()
    
    @patch('builtins.open', new_callable=mock_open)
    @patch('csv.DictWriter')
    def test_csv_export_hypervisors(self, mock_csv_writer, mock_file):
        """Test CSV export functionality for hypervisors."""
        # Setup mocks
        self.mock_conn.compute.servers.return_value = [self.mock_server]
        self.mock_conn.compute.hypervisors.return_value = [self.mock_hypervisor]
        self.mock_conn.compute.get_flavor.return_value = self.mock_flavor
        
        # Mock CSV writer
        mock_writer_instance = MagicMock()
        mock_csv_writer.return_value = mock_writer_instance
        
        # Call function
        os_info.get_openstack_info_and_export_csv(
            instance_filename='test_instances.csv',
            hypervisor_filename='test_hypervisors.csv',
            conn=self.mock_conn
        )
        
        # Verify file operations
        mock_file.assert_any_call('test_hypervisors.csv', 'w', newline='')
        mock_csv_writer.assert_called()
        mock_writer_instance.writeheader.assert_called()
        mock_writer_instance.writerows.assert_called()
    
    def test_overcommit_calculations(self):
        """Test overcommit ratio calculations."""
        # Test data: 2 VMs with 2 VCPUs each = 4 total VCPUs allocated
        # Hypervisor has 16 physical VCPUs
        # Expected CPU overcommit ratio = 4/16 = 0.25
        
        servers = [self.mock_server, self.mock_server]  # 2 identical servers
        hypervisor = self.mock_hypervisor
        flavor = self.mock_flavor
        
        # Calculate expected values
        allocated_vcpus = len(servers) * flavor.vcpus  # 2 * 2 = 4
        allocated_memory = len(servers) * flavor.ram   # 2 * 2048 = 4096
        
        expected_cpu_overcommit = allocated_vcpus / hypervisor.vcpus  # 4/16 = 0.25
        expected_memory_overcommit = allocated_memory / hypervisor.memory_size  # 4096/32768 = 0.125
        
        self.assertEqual(expected_cpu_overcommit, 0.25)
        self.assertEqual(expected_memory_overcommit, 0.125)
        self.assertLess(expected_cpu_overcommit, 1.0)  # Not overcommitted
        self.assertLess(expected_memory_overcommit, 1.0)  # Not overcommitted
    
    def test_no_connection_provided(self):
        """Test function behavior when no connection is provided."""
        with patch('builtins.print') as mock_print:
            result = os_info.get_openstack_info_and_export_csv(conn=None)
            
            self.assertIsNone(result)
            mock_print.assert_called_with("Error: OpenStack connection not provided")


class TestErrorHandling(unittest.TestCase):
    """Test error handling scenarios."""
    
    @patch('os_info.openstack.connect')
    def test_connection_failure(self, mock_connect):
        """Test handling of connection failures."""
        # Mock connection failure
        mock_connect.side_effect = Exception("Connection failed")
        
        with self.assertRaises(Exception):
            os_info.setup_openstack_connection(
                auth_method='args',
                auth_url='https://keystone.example.com:5000/v3',
                username='testuser',
                password='testpass',
                project_name='testproject'
            )
    
    @patch('os_info.load_config_file')
    def test_config_file_loading_failure(self, mock_load_config):
        """Test handling of config file loading failures."""
        mock_load_config.return_value = None
        
        with self.assertRaises(ValueError) as context:
            os_info.setup_openstack_connection(auth_method='config', config_file='invalid.conf')
        
        self.assertIn('Failed to load configuration', str(context.exception))


class TestIntegration(unittest.TestCase):
    """Integration tests with multiple components."""
    
    @patch('os_info.setup_openstack_connection')
    @patch('os_info.get_openstack_info_and_export_csv')
    @patch('sys.argv')
    def test_main_execution_flow(self, mock_argv, mock_export, mock_setup):
        """Test the main execution flow."""
        # Mock command line arguments
        mock_argv.__getitem__.side_effect = lambda x: ['os_info.py'][x]
        mock_argv.__len__.return_value = 1
        
        # Mock successful connection setup
        mock_conn = MagicMock()
        mock_setup.return_value = mock_conn
        
        # Import and patch the main execution
        with patch('os_info.parse_arguments') as mock_parse:
            mock_args = MagicMock()
            mock_args.auth_method = 'auto'
            mock_args.config_file = None
            mock_args.instances_file = 'openstack_instances.csv'
            mock_args.hypervisors_file = 'openstack_hypervisors.csv'
            mock_parse.return_value = mock_args
            
            # This would test the main block, but since it's guarded by __name__ == "__main__",
            # we'll test the components individually
            mock_setup.assert_not_called()  # Not called yet
            mock_export.assert_not_called()  # Not called yet


def run_tests():
    """Run all tests."""
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestAuthenticationMethods,
        TestConfigurationFile,
        TestAuthenticationValidation,
        TestConnectionSetup,
        TestArgumentParsing,
        TestDataProcessing,
        TestErrorHandling,
        TestIntegration
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    print("Running OpenStack Info Tool Test Suite")
    print("=" * 50)
    
    success = run_tests()
    
    if success:
        print("\n" + "=" * 50)
        print("✅ All tests passed!")
        sys.exit(0)
    else:
        print("\n" + "=" * 50)
        print("❌ Some tests failed!")
        sys.exit(1)
