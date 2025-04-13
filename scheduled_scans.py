from antivirus_agent_ai import scan_system
import schedule
import time
import logging
from datetime import datetime

logging.basicConfig(
    filename="scheduled_scans.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def run_scheduled_scan():
    logging.info("Rozpoczęto zaplanowane skanowanie")
    try:
        results = scan_system()
        logging.info(f"Wyniki skanowania: {results}")
        with open(f"scan_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt", "w") as f:
            f.write(results)
        logging.info("Zakończono zaplanowane skanowanie")
    except Exception as e:
        logging.error(f"Błąd podczas skanowania: {str(e)}")

def schedule_scans():
    # Codzienne skanowanie o 2:00
    schedule.every().day.at("02:00").do(run_scheduled_scan)
    
    # Co godzinę skanowanie ważnych lokalizacji
    schedule.every().hour.do(lambda: scan_system())
    
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    schedule_scans()
