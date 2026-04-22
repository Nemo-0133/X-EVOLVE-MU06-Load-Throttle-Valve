import psutil
import time

class MU06_LoadSuppressor:
    def __init__(self, temp_threshold=80.0, cpu_threshold=85.0):
        self.temp_threshold = temp_threshold
        self.cpu_threshold = cpu_threshold
        print(f"[MU-06] 負載壓制模組上線 (紅線設定: CPU {self.cpu_threshold}%, 溫度防線啟動)")

    def check_physical_status(self):
        """檢測硬體狀態，若超標則回傳暫停指令"""
        cpu_usage = psutil.cpu_percent(interval=1)
        
        # Windows 環境下 psutil 溫度感測可能受限，此處作為框架預留與跨平台兼容
        temp_warning = False
        if hasattr(psutil, "sensors_temperatures"):
            temps = psutil.sensors_temperatures()
            if temps and 'coretemp' in temps:
                for entry in temps['coretemp']:
                    if entry.current >= self.temp_threshold:
                        temp_warning = True

        if cpu_usage >= self.cpu_threshold or temp_warning:
            print(f"[MU-06] 警告：觸發物理紅線 (CPU: {cpu_usage}%)。系統過載！")
            return {"status": "DANGER", "action": "SUSPEND"}
        
        return {"status": "SAFE", "action": "CONTINUE"}
