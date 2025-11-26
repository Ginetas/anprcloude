# Quick Start Guide - ANPR Edge Worker Installation

## Choose Your Platform

### Raspberry Pi + Hailo-8L
```bash
sudo bash install_rpi_hailo.sh
```
**Installation time:** ~15 minutes
**Best for:** Maximum performance, AI acceleration

### Raspberry Pi + Google Coral TPU
```bash
sudo bash install_rpi_coral.sh
```
**Installation time:** ~10 minutes
**Best for:** TensorFlow Lite models, easy deployment

### Linux Server (GPU/CPU)
```bash
# Auto-detect GPU
sudo bash install_linux.sh

# CPU-only
sudo bash install_linux.sh --skip-gpu

# Force CUDA 11.8
sudo bash install_linux.sh --force-cuda-version 11.8
```
**Installation time:** ~20-30 minutes (with GPU drivers)
**Best for:** Flexible, powerful deployments

---

## Post-Installation Checklist

### For All Platforms:
- [ ] Installation completed without errors
- [ ] Systemd service is active: `sudo systemctl status anpr-edge-worker.service`
- [ ] Configuration file accessible: `ls /etc/anpr-edge-worker/config.yaml`
- [ ] Log directory exists: `ls /var/log/anpr-edge-worker/`
- [ ] Models directory ready: `ls /opt/anpr-edge-worker/models/`

### For Raspberry Pi + Hailo:
- [ ] Device detected: `hailortcli fw-control identify`
- [ ] GStreamer available: `gst-launch-1.0 --version`
- [ ] Hailo runtime: `dpkg -l | grep hailo`

### For Raspberry Pi + Coral:
- [ ] Device detected: `python3 -c "from pycoral.utils import edgetpu_utils; print(edgetpu_utils.list_edge_tpus())"`
- [ ] USB cable connected (if using USB device)
- [ ] TFLite runtime: `python3 -c "import tflite_runtime; print('OK')"`

### For Linux + GPU:
- [ ] NVIDIA driver: `nvidia-smi`
- [ ] CUDA toolkit: `nvcc --version`
- [ ] GPU detected: `nvidia-smi --list-gpus`

---

## Essential Commands

### Service Management
```bash
# Start service
sudo systemctl start anpr-edge-worker.service

# Stop service
sudo systemctl stop anpr-edge-worker.service

# Check status
sudo systemctl status anpr-edge-worker.service

# View logs (live)
sudo journalctl -u anpr-edge-worker.service -f

# View last 50 lines
sudo journalctl -u anpr-edge-worker.service -n 50
```

### Configuration
```bash
# Edit configuration
sudo nano /etc/anpr-edge-worker/config.yaml

# Validate YAML
python3 -c "import yaml; yaml.safe_load(open('/etc/anpr-edge-worker/config.yaml'))"
```

### Model Placement
```bash
# Copy your models
cp my_detection_model.* /opt/anpr-edge-worker/models/
cp my_ocr_model.* /opt/anpr-edge-worker/models/

# List installed models
ls -la /opt/anpr-edge-worker/models/
```

### Enable Auto-Start
```bash
sudo systemctl enable anpr-edge-worker.service
```

---

## Directory Reference

| Path | Purpose | Permissions |
|------|---------|-------------|
| `/opt/anpr-edge-worker/` | Application home | User: anprworker |
| `/opt/anpr-edge-worker/venv/` | Python environment | User: anprworker |
| `/opt/anpr-edge-worker/models/` | AI models | User: anprworker |
| `/etc/anpr-edge-worker/` | Configuration files | 750 |
| `/etc/anpr-edge-worker/config.yaml` | Main config | 640 |
| `/var/log/anpr-edge-worker/` | Application logs | User: anprworker |
| `/etc/systemd/system/anpr-edge-worker.service` | Systemd service | 644 |

---

## Troubleshooting Quick Links

| Problem | Solution |
|---------|----------|
| Service won't start | Check logs: `sudo journalctl -u anpr-edge-worker.service -n 100` |
| Device not detected | See device-specific commands in README.md |
| Out of memory | Reduce batch size in config.yaml |
| Permission denied | Check user groups: `groups anprworker` |
| GPU not detected | Run: `sudo bash install_linux.sh --force-cuda-version 12.0` |
| Models not loading | Check path in config.yaml and file permissions |

---

## First Run

1. **Edit Configuration:**
   ```bash
   sudo nano /etc/anpr-edge-worker/config.yaml
   ```
   - Update camera source URI
   - Verify accelerator type
   - Set model paths

2. **Start Service:**
   ```bash
   sudo systemctl start anpr-edge-worker.service
   ```

3. **Monitor Logs:**
   ```bash
   sudo journalctl -u anpr-edge-worker.service -f
   ```

4. **API Access (if configured):**
   ```bash
   # Check API (default port 5000)
   curl http://localhost:5000/health
   ```

---

## Important Notes

- **Device Connection:** Connect Hailo-8L or Coral TPU BEFORE starting service
- **Model Format:** Ensure models match your accelerator (HEF for Hailo, TFLite for Coral)
- **Permissions:** User `anprworker` handles service execution
- **Logs Location:** `/var/log/anpr-edge-worker/worker.log`
- **Config Location:** `/etc/anpr-edge-worker/config.yaml`

---

## Performance Tips

### Hailo-8L
- Adjust `max_workers` based on available CPU cores
- Use batch processing for multiple streams

### Coral TPU
- Models must be compiled with EdgeTPU support
- Single threaded for optimal performance

### Linux GPU
- Set `use_fp16: true` for faster inference
- Enable tensor cores for compatible GPUs
- Monitor with: `nvidia-smi -l 1`

---

## Next Steps

1. **Install Models:** Place AI models in `/opt/anpr-edge-worker/models/`
2. **Configure Input:** Update camera source in `config.yaml`
3. **Configure Output:** Set up MQTT, HTTP, or other output targets
4. **Verify:** Run health checks and monitor logs
5. **Deploy:** Enable auto-start with `systemctl enable`

For detailed documentation, see **README.md**
