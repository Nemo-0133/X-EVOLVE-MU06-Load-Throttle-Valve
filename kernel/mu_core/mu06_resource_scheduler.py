import psutil
import time
import logging

class MU06ResourceScheduler:
    def __init__(self, cpu_limit=85.0, ram_limit=85.0):
        """
        初始化硬體資源排程器
        :param cpu_limit: CPU 負載熔斷閾值 (預設 85%)
        :param ram_limit: 記憶體負載熔斷閾值 (預設 85%)
        """
        self.cpu_limit = cpu_limit
        self.ram_limit = ram_limit
        
        # 設置基礎日誌紀錄
        logging.basicConfig(level=logging.INFO, format='[MU-06] %(asctime)s - %(message)s')

    def check_system_load(self):
        """
        檢測當前系統負載狀態。
        :return: (is_overloaded, current_cpu, current_ram)
        """
        # 取樣間隔 0.5 秒以獲取準確的 CPU 使用率
        current_cpu = psutil.cpu_percent(interval=0.5)
        current_ram = psutil.virtual_memory().percent

        is_overloaded = current_cpu >= self.cpu_limit or current_ram >= self.ram_limit
        
        return is_overloaded, current_cpu, current_ram

    def yield_resources(self, check_interval=5):
        """
        資源讓出機制 (阻塞當前高耗能進程，直到算力恢復)
        """
        is_overloaded, current_cpu, current_ram = self.check_system_load()
        
        if is_overloaded:
            logging.warning(f"偵測到算力過載 (CPU: {current_cpu}%, RAM: {current_ram}%)。")
            logging.info("觸發資源讓出，暫停本地高耗能運算，進入待機輪詢...")
            
            # 持續輪詢直到資源降至安全標準內
            while is_overloaded:
                time.sleep(check_interval)
                is_overloaded, current_cpu, current_ram = self.check_system_load()
                
            logging.info(f"算力已恢復 (CPU: {current_cpu}%, RAM: {current_ram}%)。解除阻塞，恢復排程。")
            return True
        return False

    def get_hardware_profile(self):
        """
        取得本機硬體基礎規格，供系統動態調整策略
        """
        profile = {
            "logical_cores": psutil.cpu_count(logical=True),
            "physical_cores": psutil.cpu_count(logical=False),
            "total_ram_gb": round(psutil.virtual_memory().total / (1024 ** 3), 2)
        }
        return profile

# 獨立測試區塊 (僅在直接執行此腳本時觸發)
if __name__ == "__main__":
    scheduler = MU06ResourceScheduler()
    profile = scheduler.get_hardware_profile()
    print(f"[系統初始化] 偵測到硬體規格: {profile['physical_cores']} 實體核心 / {profile['logical_cores']} 邏輯核心, {profile['total_ram_gb']} GB RAM")
    
    # 執行一次負載檢測
    scheduler.yield_resources()
