# OptimAI Network Node Setup Guide

Complete guide for setting up and running OptimAI Network edge nodes for AI data processing.

## Overview

OptimAI Network is a decentralized AI infrastructure network that enables edge devices to contribute to AI model training, inference, and data processing. Node operators earn rewards based on compute contribution.

## System Requirements

### Minimum Requirements
- **CPU**: 4 cores (x86_64 or ARM64)
- **RAM**: 8 GB
- **Storage**: 50 GB SSD
- **Network**: 10 Mbps stable connection
- **OS**: Ubuntu 20.04/22.04, Debian 11/12, or compatible Linux

### Recommended
- **CPU**: 8+ cores (Intel i7/i9 or AMD Ryzen 7/9)
- **RAM**: 16-32 GB DDR4
- **Storage**: 200 GB NVMe SSD
- **GPU**: NVIDIA GTX 1060+ or RTX series (optional but recommended)
- **Network**: 100 Mbps+ with low latency

### GPU Acceleration (Optional)
- **NVIDIA**: CUDA 11.8+ compatible GPU
- **AMD**: ROCm support (limited)
- **VRAM**: 4 GB minimum, 8 GB+ recommended

## Installation

### Step 1: System Preparation

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y curl wget git python3 python3-pip docker.io docker-compose

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker
```

### Step 2: Install NVIDIA Drivers (if using GPU)

```bash
# Add NVIDIA package repositories
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list

# Install nvidia-docker2
sudo apt update
sudo apt install -y nvidia-docker2

# Restart Docker
sudo systemctl restart docker

# Test GPU access
docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi
```

### Step 3: Install OptimAI CLI

```bash
# Download OptimAI CLI
curl -sSL https://install.optimai.network/optimai-cli.sh | bash

# Or manual installation
wget https://github.com/optimai-network/optimai-cli/releases/latest/download/optimai-linux-amd64
chmod +x optimai-linux-amd64
sudo mv optimai-linux-amd64 /usr/local/bin/optimai

# Verify installation
optimai --version
```

### Step 4: Authenticate and Register

```bash
# Login with your OptimAI account
optimai login

# Or use API key
optimai login --api-key YOUR_API_KEY

# Register node
optimai node register --name "your-node-name"
```

### Step 5: Configure Node

```bash
mkdir -p ~/.optimai

cat > ~/.optimai/config.yaml << 'EOF'
node:
  name: "carly-optimai-node"
  region: "asia-southeast"
  
compute:
  cpu:
    enabled: true
    cores: 4
    priority: "normal"
  gpu:
    enabled: true
    device: "nvidia"
    memory_limit: "6GB"
  memory:
    limit: "12GB"
  storage:
    cache_size: "100GB"
    
network:
  listen_port: 8080
  public_ip: "auto"
  max_bandwidth: "100Mbps"
  
workloads:
  inference: true
  training: true
  data_processing: true
  
rewards:
  address: "YOUR_ETHEREUM_ADDRESS"
  auto_claim: true
  
monitoring:
  enabled: true
  metrics_port: 9090
  log_level: "info"
EOF
```

### Step 6: Start Node

**Option A: Docker Compose (Recommended)**

```bash
cd ~/.optimai

cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  optimai-node:
    image: optimai/network-node:latest
    container_name: optimai-node
    restart: unless-stopped
    runtime: nvidia  # Remove if no GPU
    ports:
      - "8080:8080"
      - "9090:9090"
    volumes:
      - ./config.yaml:/app/config.yaml
      - ./cache:/app/cache
      - ./models:/app/models
    environment:
      - OPTIMAI_CONFIG=/app/config.yaml
      - NVIDIA_VISIBLE_DEVICES=all
    deploy:
      resources:
        limits:
          cpus: '4'
          memory: 12G
        reservations:
          cpus: '2'
          memory: 4G
EOF

# Start node
docker-compose up -d

# View logs
docker-compose logs -f
```

**Option B: Systemd Service**

```bash
sudo tee /etc/systemd/system/optimai-node.service > /dev/null << 'EOF'
[Unit]
Description=OptimAI Network Node
After=network.target docker.service
Requires=docker.service

[Service]
Type=simple
User=$USER
WorkingDirectory=$HOME/.optimai
ExecStart=/usr/bin/docker-compose up
ExecStop=/usr/bin/docker-compose down
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable optimai-node
sudo systemctl start optimai-node
```

## Monitoring

### Check Node Status

```bash
# Node health
optimai node status

# Compute resources
optimai node resources

# Active workloads
optimai workloads list

# Rewards
optimai rewards status
```

### View Logs

```bash
# Docker logs
docker logs -f optimai-node

# Systemd logs
sudo journalctl -u optimai-node -f

# Metrics
curl http://localhost:9090/metrics
```

### Dashboard

Access node dashboard at: `https://dashboard.optimai.network`

## Troubleshooting

### Issue: Node authentication fails

**Symptoms**: `optimai login` fails

**Solutions**:
1. Check API key:
   ```bash
   optimai login --api-key YOUR_KEY
   ```

2. Verify network:
   ```bash
   curl https://api.optimai.network/health
   ```

3. Reset credentials:
   ```bash
   rm ~/.optimai/credentials
   optimai login
   ```

### Issue: GPU not detected

**Symptoms**: Node running but GPU not used

**Solutions**:
1. Check NVIDIA drivers:
   ```bash
   nvidia-smi
   ```

2. Verify nvidia-docker:
   ```bash
   docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi
   ```

3. Update config:
   ```yaml
   gpu:
     enabled: true
     device: "nvidia"
   ```

4. Restart node:
   ```bash
   docker-compose restart
   ```

### Issue: Low task allocation

**Symptoms**: Node online but few tasks

**Solutions**:
1. Check compute availability:
   ```bash
   optimai node resources
   ```

2. Enable more workload types:
   ```yaml
   workloads:
     inference: true
     training: true
     data_processing: true
   ```

3. Improve network latency
4. Upgrade hardware specs

### Issue: Out of memory

**Symptoms**: Node crashes with OOM errors

**Solutions**:
1. Reduce memory limit:
   ```yaml
   memory:
     limit: "8GB"
   ```

2. Limit concurrent tasks:
   ```yaml
   compute:
     max_concurrent: 2
   ```

3. Add swap:
   ```bash
   sudo fallocate -l 8G /swapfile
   sudo chmod 600 /swapfile
   sudo mkswap /swapfile
   sudo swapon /swapfile
   ```

### Issue: Model download fails

**Symptoms**: Cannot download AI models

**Solutions**:
1. Check storage:
   ```bash
   df -h
   ```

2. Clear model cache:
   ```bash
   rm -rf ~/.optimai/cache/models/*
   ```

3. Check network:
   ```bash
   ping huggingface.co
   ```

### Issue: No rewards

**Symptoms**: Node running but no rewards

**Solutions**:
1. Verify reward address:
   ```bash
   optimai config get rewards.address
   ```

2. Check task completion rate:
   ```bash
   optimai workloads history
   ```

3. Verify minimum uptime (usually 24h)
4. Check dashboard for penalties

## FAQ

**Q: What AI models are supported?**
A: OptimAI supports various LLMs, vision models, and custom models. Check dashboard for current list.

**Q: Can I run without GPU?**
A: Yes, but GPU significantly increases earning potential.

**Q: How are rewards calculated?**
A: Based on compute contributed (FLOPS), task completion rate, and network demand.

**Q: Is my data private?**
A: Yes, all processing is done locally. Only anonymized metrics are sent to the network.

**Q: Can I limit resource usage?**
A: Yes, configure limits in `config.yaml` for CPU, GPU, memory, and bandwidth.

## Performance Optimization

### CPU Optimization

```yaml
compute:
  cpu:
    cores: 6
    affinity: "0-5"  # Pin to specific cores
    governor: "performance"
```

### GPU Optimization

```yaml
gpu:
  enabled: true
  device: "nvidia"
  memory_limit: "10GB"
  power_limit: 250  # Watts
  clock_offset: 100
```

### Network Optimization

```yaml
network:
  max_bandwidth: "500Mbps"
  prefer_ipv6: false
  keep_alive: true
```

## Resources

- [Official Documentation](https://docs.optimai.network)
- [OptimAI Dashboard](https://dashboard.optimai.network)
- [Discord Community](https://discord.gg/optimai)
- [GitHub](https://github.com/optimai-network)
- [Hugging Face](https://huggingface.co/optimai)

## License

MIT
