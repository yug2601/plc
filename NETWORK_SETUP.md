# Important: Network Configuration for Cloud Deployment

## ⚠️ Critical Setup Required

For your cloud-deployed backend to communicate with your PLC, you need to configure your network properly.

## Option 1: Public IP Access (Recommended)
If your PLC has a public IP or your router has port forwarding:

### Router Configuration
1. **Find your PLC's local IP**: `192.168.0.10` (as in your code)
2. **Configure Port Forwarding** on your router:
   - External Port: `502` (or any port you choose)
   - Internal IP: `192.168.0.10`
   - Internal Port: `502`
   - Protocol: `TCP`

3. **Find your public IP**: Visit [whatismyip.com](https://whatismyip.com)

4. **Update your environment variable**:
   - Change `PLC_IP` from `192.168.0.10` to your public IP
   - If you used a different external port, update `PLC_PORT` too

### Security Considerations
- Consider changing the external port from 502 to something less obvious (e.g., 8502)
- Set up firewall rules to restrict access if possible
- Monitor for unusual connection attempts

## Option 2: VPN Solution
If port forwarding isn't possible or desired:

### Using Tailscale (Easier)
1. **Install Tailscale** on your PLC network device and cloud server
2. **Get PLC's Tailscale IP** (usually starts with 100.x.x.x)
3. **Update environment variable** to use Tailscale IP

### Using Traditional VPN
1. Set up VPN server on your network
2. Configure cloud service to connect via VPN
3. Use local PLC IP (`192.168.0.10`)

## Option 3: Cloud Gateway (Advanced)
Deploy a gateway service on a cloud VM in your region that connects to your local network.

## Testing Connectivity

### Test from Cloud Service
Add this test code to verify connection:

```python
# Add this to your plc_gateway.py for testing
def test_plc_connection():
    """Test PLC connectivity"""
    import socket
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((PLC_IP, PORT))
        sock.close()
        if result == 0:
            logger.info(f"✅ PLC connection test SUCCESSFUL to {PLC_IP}:{PORT}")
            return True
        else:
            logger.error(f"❌ PLC connection test FAILED to {PLC_IP}:{PORT}")
            return False
    except Exception as e:
        logger.error(f"❌ PLC connection test ERROR: {e}")
        return False

# Call this in your main_loop before starting the while loop
if not test_plc_connection():
    logger.error("Cannot reach PLC. Check network configuration.")
```

## Deployment Environment Variables

Update your cloud deployment with the correct IP:

### For Railway/Render
```
PLC_IP=YOUR_PUBLIC_IP_OR_DOMAIN
PLC_PORT=502
UPLOAD_RATE=2
```

### Example with Port Forwarding
If you forward port 8502 to your PLC's port 502:
```
PLC_IP=YOUR_PUBLIC_IP
PLC_PORT=8502
UPLOAD_RATE=2
```

## Final Architecture

```
Internet → Cloud Service (Railway/Render)
    ↓
Your Public IP:8502
    ↓
Router (Port Forward 8502→502)
    ↓
PLC (192.168.0.10:502)
```

After this setup:
- ✅ Your Vercel frontend works from anywhere
- ✅ Your Railway/Render backend works from anywhere  
- ✅ Backend connects to your PLC via internet
- ✅ No need for your PC to be on
- ✅ No need to manually start scripts

**The entire system runs in the cloud!** 🚀