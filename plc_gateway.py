import time
import struct
import datetime
import os
import logging
from pymodbus.client import ModbusTcpClient
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ==========================================
# USER SETTINGS - ENVIRONMENT VARIABLES
# ==========================================
PLC_IP = os.getenv("PLC_IP", "192.168.0.10")  # Your PLC IP
PORT = int(os.getenv("PLC_PORT", "502"))
UPLOAD_RATE = int(os.getenv("UPLOAD_RATE", "2"))  # Upload every 2 seconds

# ALIGNMENT SETTINGS (DO NOT CHANGE)
# We start at 599 to capture the High Word for address 600
REGISTER_ADDRESS = 599 
REGISTER_COUNT = 44      # Read enough to cover up to 639
UNIT_ID = 1
# ==========================================

# Initialize Cloud Connection
if not firebase_admin._apps:
    try:
        # Try to use service account key file
        if os.path.exists("serviceAccountKey.json"):
            cred = credentials.Certificate("serviceAccountKey.json")
            firebase_admin.initialize_app(cred)
            logger.info("Firebase initialized with service account key")
        else:
            # Use default credentials (for cloud deployment)
            firebase_admin.initialize_app()
            logger.info("Firebase initialized with default credentials")
    except Exception as e:
        logger.error(f"Firebase initialization failed: {e}")
        raise

db = firestore.client()
# We store data in 'factory_data' collection, document 'oven_1'
doc_ref = db.collection('factory_data').document('oven_1')

client = ModbusTcpClient(host=PLC_IP, port=PORT, timeout=5)

def test_plc_connection():
    """Test PLC connectivity before starting main loop"""
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

def decode_float(reg_high, reg_low):
    """ Combines 2 registers into a Float (Big Endian) """
    try:
        raw_bytes = struct.pack('>HH', reg_high, reg_low)
        val = struct.unpack('>f', raw_bytes)[0]
        return val
    except:
        return 0.0

def main_loop():
    logger.info("=== PLC GATEWAY STARTED ===")
    logger.info(f"Target PLC: {PLC_IP}:{PORT}")
    logger.info(f"Upload Rate: {UPLOAD_RATE} seconds")
    logger.info(f"Firebase Collection: factory_data/oven_1")
    logger.info("===============================")
    
    # Add health check for cloud platforms
    if os.getenv('PORT'):
        logger.info(f"Running in cloud mode on port {os.getenv('PORT')}")
    
    # Test PLC connection before starting
    if not test_plc_connection():
        logger.error("Cannot reach PLC. Check network configuration and ensure port forwarding is set up.")
        logger.error("If running locally, verify PLC IP. If running in cloud, ensure public IP and port forwarding.")
        # Continue anyway - connection might be established later

    while True:
        try:
            # 1. Connect
            if not client.connected:
                client.connect()

            # 2. Read Data
            try:
                # Try standard v3 syntax
                rr = client.read_holding_registers(REGISTER_ADDRESS, count=REGISTER_COUNT, slave=UNIT_ID)
            except TypeError:
                # Try older syntax
                try:
                    rr = client.read_holding_registers(REGISTER_ADDRESS, count=REGISTER_COUNT, unit=UNIT_ID)
                except:
                    rr = client.read_holding_registers(REGISTER_ADDRESS, count=REGISTER_COUNT)

            # 3. Process Data
            if not rr.isError() and hasattr(rr, 'registers'):
                regs = rr.registers
                payload = {}
                
                # Loop logic: Iterate pairs
                # regs[0] is 599. regs[1] is 600. Pair (0,1) = Address 600.
                for i in range(0, len(regs), 2):
                    if i + 1 < len(regs):
                        val_high = regs[i]
                        val_low  = regs[i+1]
                        
                        # Calculate the logical address (e.g., 600, 602)
                        # 599 + i + 1
                        current_addr = REGISTER_ADDRESS + i + 1
                        
                        # Safety stop at 639
                        if current_addr > 639:
                            break

                        float_val = decode_float(val_high, val_low)
                        
                        # Add to payload. We convert to string key for JSON compatibility
                        # Rounding to 4 decimal places
                        payload[str(current_addr)] = round(float_val, 4)

                # 4. Add Metadata
                payload['last_updated'] = datetime.datetime.now().isoformat()
                payload['status'] = "ONLINE"

                # 5. Upload to Cloud
                doc_ref.set(payload)
                
                # Log successful upload
                logger.info(f"Uploaded {len(payload)-2} registers successfully")

            else:
                logger.error("Read Error: PLC did not respond correctly")
                doc_ref.update({'status': 'ERROR'})

        except Exception as e:
            logger.error(f"Connection Error: {e}")
            try:
                doc_ref.update({'status': 'OFFLINE'})
            except Exception as fb_error:
                logger.error(f"Failed to update Firebase status: {fb_error}")
        
        time.sleep(UPLOAD_RATE)

# Simple HTTP server for cloud platforms
def start_http_server():
    """Start a simple HTTP server for health checks"""
    import threading
    from http.server import HTTPServer, BaseHTTPRequestHandler
    
    class HealthHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"status": "running", "service": "PLC Gateway"}')
        
        def log_message(self, format, *args):
            pass  # Suppress HTTP logs
    
    port = int(os.getenv('PORT', '10000'))  # Render uses port 10000
    server = HTTPServer(('0.0.0.0', port), HealthHandler)
    logger.info(f"Health check server running on port {port}")
    server.serve_forever()

if __name__ == "__main__":
    # Start HTTP server in a separate thread for cloud platforms
    if os.getenv('PORT'):
        import threading
        server_thread = threading.Thread(target=start_http_server, daemon=True)
        server_thread.start()
    
    main_loop()
