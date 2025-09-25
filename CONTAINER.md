# Container Usage Guide

This document explains how to use the OpenStack Info Tool as a container with Docker, Podman, and OpenShift.

## 🐳 Building the Container Image

### Using Docker
```bash
docker build -t openstack-info:latest .
```

### Using Podman
```bash
podman build -t openstack-info:latest .
```

## 🚀 Running the Container

### Basic Usage with Docker
```bash
# Show help
docker run --rm openstack-info:latest

# Run with environment variables
docker run --rm \
  -e OS_AUTH_URL=https://keystone.example.com:5000/v3 \
  -e OS_USERNAME=myuser \
  -e OS_PASSWORD=mypass \
  -e OS_PROJECT_NAME=myproject \
  -v $(pwd)/reports:/app/reports \
  openstack-info:latest --instances-only
```

### Using Podman
```bash
# Show help
podman run --rm openstack-info:latest

# Run with environment variables
podman run --rm \
  -e OS_AUTH_URL=https://keystone.example.com:5000/v3 \
  -e OS_USERNAME=myuser \
  -e OS_PASSWORD=mypass \
  -e OS_PROJECT_NAME=myproject \
  -v $(pwd)/reports:/app/reports:Z \
  openstack-info:latest --instances-only
```

### Using Docker Compose
```bash
# Create .env file with your credentials
echo "OS_AUTH_URL=https://keystone.example.com:5000/v3" > .env
echo "OS_USERNAME=myuser" >> .env
echo "OS_PASSWORD=mypass" >> .env
echo "OS_PROJECT_NAME=myproject" >> .env

# Run with docker-compose
docker-compose run --rm openstack-info --instances-only

# Or run in background
docker-compose up -d
```

## ☸️ OpenShift Deployment

### Prerequisites
- OpenShift cluster access
- Image pushed to accessible registry
- Proper RBAC permissions

### Deploy with OpenShift
```bash
# Create project
oc new-project openstack-monitoring

# Update credentials in the secret (edit the YAML file first)
# Edit openshift/job.yaml and replace:
# - OS_AUTH_URL value
# - OS_USERNAME and OS_PASSWORD in secret
# - OS_PROJECT_NAME, OS_REGION_NAME values

# Deploy the one-shot job
oc apply -f openshift/job.yaml

# Run the job
oc create job openstack-report-$(date +%Y%m%d) --from=job/openstack-info-report

# Check the deployment
oc get jobs
oc get pods
oc get pvc

# View logs
oc logs job/openstack-report-$(date +%Y%m%d)
```

### Security Context Constraints (SCC)
The container is designed to work with OpenShift's default `restricted` SCC:
- Runs as non-root user (UID 1001)
- Handles arbitrary user ID assignment
- No privileged operations required
- Read-only root filesystem compatible

## 🔐 Authentication Methods

### Environment Variables
Set OpenStack credentials as environment variables:
```bash
export OS_AUTH_URL=https://keystone.example.com:5000/v3
export OS_USERNAME=myuser
export OS_PASSWORD=mypass
export OS_PROJECT_NAME=myproject
export OS_USER_DOMAIN_NAME=default
export OS_PROJECT_DOMAIN_NAME=default
```

### Configuration File
Mount a configuration file:
```bash
# Create config file
mkdir -p config
cp examples/openstack.conf.example config/openstack.conf
# Edit config/openstack.conf with your credentials

# Run with config file
docker run --rm \
  -v $(pwd)/config:/app/config:ro \
  -v $(pwd)/reports:/app/reports \
  openstack-info:latest --auth-method config --config-file /app/config/openstack.conf
```

### Interactive Mode (Docker/Podman only)
```bash
docker run --rm -it \
  -v $(pwd)/reports:/app/reports \
  openstack-info:latest --auth-method interactive
```

## 📁 Volumes and Storage

### Local Development
```bash
# Create local directories
mkdir -p reports config

# Mount volumes
docker run --rm \
  -v $(pwd)/reports:/app/reports \
  -v $(pwd)/config:/app/config:ro \
  openstack-info:latest
```

### OpenShift Persistent Storage
The OpenShift deployment includes:
- **PersistentVolumeClaim** for reports storage
- **ConfigMap** for configuration
- **Secret** for sensitive credentials

## 🔧 Advanced Usage

### Custom Entrypoint
```bash
# Override entrypoint for debugging
docker run --rm -it \
  --entrypoint /bin/sh \
  openstack-info:latest
```

### Resource Limits
```bash
# Set memory and CPU limits
docker run --rm \
  --memory=512m \
  --cpus=0.5 \
  openstack-info:latest
```

### Scheduled Execution
```bash
# Run daily with cron (host-based)
echo "0 6 * * * docker run --rm -v /host/reports:/app/reports openstack-info:latest" | crontab -

# Or use OpenShift CronJob (see openshift/deployment.yaml)
```

## 🛡️ Security Best Practices

### Container Security
- ✅ Runs as non-root user (UID 1001)
- ✅ No privileged operations
- ✅ Minimal attack surface (UBI minimal base)
- ✅ Regular security updates via UBI

### Credential Management
- 🔐 Use Kubernetes Secrets for passwords
- 🔐 Mount config files read-only
- 🔐 Avoid hardcoding credentials in images
- 🔐 Use service accounts where possible

### Network Security
- 🌐 Container only needs outbound HTTPS (443) to OpenStack API
- 🌐 No inbound ports required
- 🌐 Consider network policies in OpenShift

## 🐛 Troubleshooting

### Common Issues

#### Permission Denied
```bash
# SELinux issue (Podman/RHEL)
podman run --rm -v $(pwd)/reports:/app/reports:Z openstack-info:latest

# OpenShift: Check SCC and fsGroup
oc describe pod <pod-name>
```

#### Authentication Errors
```bash
# Debug authentication
docker run --rm -it openstack-info:latest --auth-method interactive

# Check environment variables
docker run --rm openstack-info:latest /bin/sh -c 'env | grep OS_'
```

#### Missing Dependencies
```bash
# Rebuild image
docker build --no-cache -t openstack-info:latest .

# Check health
docker run --rm openstack-info:latest /bin/sh -c 'python3 -c "import openstack; print(\"OK\")"'
```

### Logs and Debugging
```bash
# Docker logs
docker logs <container-id>

# OpenShift logs
oc logs -l app=openstack-info
oc describe pod <pod-name>

# Interactive debugging
docker run --rm -it --entrypoint /bin/sh openstack-info:latest
```

## 📊 Output Management

### Report Files
Reports are saved to `/app/reports/` inside the container:
- Mount this directory to persist reports
- Use timestamped filenames for historical data
- Consider log rotation for long-running deployments

### Example Output Structure
```
reports/
├── instances_20231201.csv
├── hypervisors_20231201.csv
├── instances_20231202.csv
└── hypervisors_20231202.csv
```

## 🔄 Integration Examples

### CI/CD Pipeline
```yaml
# GitLab CI example
openstack-report:
  image: openstack-info:latest
  script:
    - python3 os_info.py --instances-file reports/instances.csv
  artifacts:
    paths:
      - reports/
    expire_in: 1 week
```

### Monitoring Integration
```bash
# Export metrics for monitoring
docker run --rm \
  -v $(pwd)/reports:/app/reports \
  openstack-info:latest --hypervisors-only | \
  python3 -c "
import csv, sys
reader = csv.DictReader(open('/app/reports/hypervisors.csv'))
for row in reader:
    print(f'hypervisor_cpu_overcommit{{host=\"{row[\"Hostname\"]}\"}} {row[\"CPU Overcommit Ratio\"]}')
"
```
