# Multi-stage build for OpenStack Info Tool
# Compatible with Docker, Podman, and OpenShift SCC

# Build stage
FROM registry.access.redhat.com/ubi9/ubi-minimal:latest AS builder

# Install Python and build dependencies
USER root
RUN microdnf update -y && \
    microdnf install -y python3 python3-pip python3-devel gcc && \
    microdnf clean all

# Create application directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip3 install --no-cache-dir --user -r requirements.txt

# Runtime stage
FROM registry.access.redhat.com/ubi9/ubi-minimal:latest

# Metadata labels
LABEL name="OpenStack Info Tool" \
      vendor="OpenStack Community" \
      version="1.0" \
      release="1" \
      summary="OpenStack infrastructure information export tool" \
      description="A tool to extract and export OpenStack instance and hypervisor information to CSV files" \
      io.k8s.description="OpenStack infrastructure information export tool" \
      io.k8s.display-name="OpenStack Info Tool" \
      io.openshift.tags="openstack,infrastructure,monitoring,csv" \
      maintainer="OpenStack Community"

# Install runtime dependencies only
USER root
RUN microdnf update -y && \
    microdnf install -y python3 && \
    microdnf clean all && \
    rm -rf /var/cache/yum

# Create application user and group (OpenShift compatible)
# Use specific UID/GID that works with OpenShift's restricted SCC
RUN groupadd -r -g 1001 osinfo && \
    useradd -r -u 1001 -g osinfo -d /app -s /sbin/nologin \
    -c "OpenStack Info Tool user" osinfo

# Create application directory with proper permissions
WORKDIR /app

# Copy Python dependencies from builder stage
COPY --from=builder /root/.local /home/osinfo/.local

# Copy application files
COPY --chown=1001:1001 os_info.py .
COPY --chown=1001:1001 requirements.txt .
COPY --chown=1001:1001 examples/ ./examples/

# Create directories for output with proper permissions
RUN mkdir -p /app/reports /app/config && \
    chown -R 1001:1001 /app && \
    chmod -R 755 /app && \
    chmod 775 /app/reports /app/config

# Set up Python path for user-installed packages
ENV PATH="/home/osinfo/.local/bin:${PATH}" \
    PYTHONPATH="/home/osinfo/.local/lib/python3.9/site-packages:${PYTHONPATH}" \
    PYTHONUNBUFFERED=1 \
    HOME=/app

# Switch to non-root user (OpenShift SCC requirement)
USER 1001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python3 -c "import sys; sys.exit(0)" || exit 1

# Expose volume for reports and configuration
VOLUME ["/app/reports", "/app/config"]

# Default entrypoint that supports OpenShift arbitrary user IDs
ENTRYPOINT ["/bin/sh", "-c", "\
    # Handle OpenShift arbitrary user ID assignment \
    if ! whoami &> /dev/null; then \
        if [ -w /etc/passwd ]; then \
            echo \"osinfo:x:$(id -u):0:OpenStack Info Tool user:${HOME}:/sbin/nologin\" >> /etc/passwd; \
        fi; \
    fi; \
    # Execute the main command \
    exec python3 os_info.py \"$@\"", "--"]

# Default command shows help
CMD ["--help"]
