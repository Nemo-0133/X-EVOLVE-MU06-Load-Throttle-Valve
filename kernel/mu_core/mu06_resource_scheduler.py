import psutil
import time
import logging

class MU06ResourceScheduler:
    """
    靜默調度中樞 (內部代號: MU-06)
    負責本地資源壓制、電費曲線抹平，以及每日資源水位監控。
    """
    def __init__(self, cpu_limit=85.0, ram_limit=0.85):
        # 實體資源限制參數 (保留原有的硬體壓制)
        self.cpu_limit = cpu_limit
        self.ram_limit = ram_limit
        
        # 資源水位計參數 (新增：防止 API/算力 枯竭)
        self.daily_token_limit = 100000  # 每日 Token/算力 消耗上限
        self.current_usage = 0           # 當前累計使用量
        self.is_sleep_mode = False       # 強制休眠狀態
        
        logging.basicConfig(level=logging.INFO, format='[SCHEDULER] %(asctime)s - %(message)s')
        logging.info("MU-06 靜默調度中樞更新完成：資源水位與實體硬體監控已就緒。")

    def track_usage(self, increment):
        """記錄資源消耗量並檢查水位"""
        self.current_usage += increment
        logging.info(f"當前水位更新: {self.current_usage} / {self.daily_token_limit}")
        
        if self.current_usage >= self.daily_token_limit:
            self._enter_sleep_mode()

    def _enter_sleep_mode(self):
        """觸發強制休眠，切斷外部非必要排程"""
        self.is_sleep_mode = True
        logging.critical("!!! 警告：達到每日資源水位上限 !!!")
        logging.critical("系統強制進入 [Sleep Mode]，所有非必要外部探測已掛起。")

    def reset_daily_usage(self):
        """週期性重置水位 (通常於每日 00:00 執行)"""
        self.current_usage = 0
        self.is_sleep_mode = False
        logging.info("每日資源水位已重置，系統回復正常運作。")

    def check_system_health(self):
        """執行實體資源壓制檢查 (結合 psutil)"""
        if self.is_sleep_mode:
            return "SLEEP"
        
        # 偵測實體 CPU 與記憶體負載
        cpu_usage = psutil.cpu_percent(interval=0.1)
        ram_usage = psutil.virtual_memory().percent / 100.0
        
        if cpu_usage > self.cpu_limit or ram_usage > self.ram_limit:
            logging.warning(f"實體負載過高 (CPU: {cpu_usage}%, RAM: {ram_usage*100:.1f}%)，觸發效能壓制。")
            return "THROTTLED"
            
        return "HEALTHY"

# --- 本機單獨測試區塊 ---
if __name__ == "__main__":
    scheduler = MU06ResourceScheduler()
    
    # 測試實體狀態
    print(f"\n[硬體檢測] 當前系統健康度: {scheduler.check_system_health()}")
    
    # 模擬資源消耗過程
    test_increments = [20000, 30000, 60000]
    
    for inc in test_increments:
        if not scheduler.is_sleep_mode:
            print(f"\n執行任務中，消耗資源: {inc}")
            scheduler.track_usage(inc)
        else:
            print("\n系統處於休眠狀態，拒絕執行任務。")
