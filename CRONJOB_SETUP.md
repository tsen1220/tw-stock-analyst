# Cronjob 設置指南

## stock-sync 命令說明

`stock-sync` 是專門為定期自動更新設計的命令，適合用 Linux/macOS cronjob 執行。

### 特點

- ✅ **增量更新**：預設只抓最近 2 天資料（可調整）
- ✅ **自動去重**：檢查資料庫中是否已存在，避免重複插入
- ✅ **日誌記錄**：自動寫入 `logs/stock_sync.log`
- ✅ **靜默模式**：預設不顯示終端輸出，適合 cron
- ✅ **錯誤處理**：適當的 exit code（0=成功，1=失敗）

---

## 使用方式

### 基本用法

```bash
# 同步所有股票（config.yaml 中的清單）
uv run stock-sync

# 同步特定股票
uv run stock-sync --stocks 2330 2454 2317

# 同步最近 5 天的資料
uv run stock-sync --days 5

# 跳過財報資料（只同步技術指標）
uv run stock-sync --skip-fundamentals

# 顯示詳細輸出（debugging 用）
uv run stock-sync -v

# 自訂日誌路徑
uv run stock-sync --log-file /var/log/stock_sync.log
```

### 完整參數

```
--stocks STOCKS [STOCKS ...]  指定股票代碼（預設：使用 config.yaml）
--days DAYS                   同步最近幾天（預設：2）
--skip-fundamentals           跳過財報資料
--log-file LOG_FILE           日誌檔案路徑（預設：logs/stock_sync.log）
-v, --verbose                 顯示詳細輸出到終端
```

---

## Cronjob 設定

### 1. 確認執行路徑

首先確認 `uv` 的完整路徑：

```bash
which uv
# 輸出範例：/opt/homebrew/bin/uv
```

### 2. 建立 cron 腳本（推薦）

建立一個包裝腳本 `/Users/kentseng/Projects/stock-analyst/sync_cron.sh`：

```bash
#!/bin/bash

# 設定專案路徑
PROJECT_DIR="/Users/kentseng/Projects/stock-analyst"
cd "$PROJECT_DIR" || exit 1

# 設定 PATH（確保找得到 uv）
export PATH="/opt/homebrew/bin:/usr/local/bin:$PATH"

# 執行同步
/opt/homebrew/bin/uv run stock-sync --days 2 --skip-fundamentals

# 記錄執行狀態
if [ $? -eq 0 ]; then
    echo "$(date): Sync completed successfully" >> "$PROJECT_DIR/logs/cron_status.log"
else
    echo "$(date): Sync failed!" >> "$PROJECT_DIR/logs/cron_status.log"
fi
```

賦予執行權限：

```bash
chmod +x /Users/kentseng/Projects/stock-analyst/sync_cron.sh
```

### 3. 設定 Crontab

編輯 crontab：

```bash
crontab -e
```

加入以下內容：

```cron
# 每天早上 9:00 同步台股資料
0 9 * * * /Users/kentseng/Projects/stock-analyst/sync_cron.sh

# 每天收盤後 14:30 再同步一次
30 14 * * * /Users/kentseng/Projects/stock-analyst/sync_cron.sh

# 每小時同步一次（適合盤中追蹤）
0 * * * * /Users/kentseng/Projects/stock-analyst/sync_cron.sh

# 週一到週五，每天早上 9:00 同步
0 9 * * 1-5 /Users/kentseng/Projects/stock-analyst/sync_cron.sh
```

### 4. 檢查 Cron 是否執行

查看 crontab 設定：

```bash
crontab -l
```

檢查日誌：

```bash
# 同步日誌
tail -f /Users/kentseng/Projects/stock-analyst/logs/stock_sync.log

# Cron 狀態日誌
tail -f /Users/kentseng/Projects/stock-analyst/logs/cron_status.log
```

---

## 進階：使用 systemd timer（Linux）

在 Linux 系統上，推薦使用 systemd timer 取代 cron。

### 1. 建立 Service 檔案

`/etc/systemd/system/stock-sync.service`：

```ini
[Unit]
Description=Taiwan Stock Data Sync
After=network.target

[Service]
Type=oneshot
User=kentseng
WorkingDirectory=/home/kentseng/Projects/stock-analyst
ExecStart=/usr/bin/uv run stock-sync --days 2
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

### 2. 建立 Timer 檔案

`/etc/systemd/system/stock-sync.timer`：

```ini
[Unit]
Description=Taiwan Stock Data Sync Timer
Requires=stock-sync.service

[Timer]
# 每天 09:00 執行
OnCalendar=*-*-* 09:00:00
# 首次啟動後 5 分鐘執行一次
OnBootSec=5min
Persistent=true

[Install]
WantedBy=timers.target
```

### 3. 啟用 Timer

```bash
sudo systemctl daemon-reload
sudo systemctl enable stock-sync.timer
sudo systemctl start stock-sync.timer

# 查看狀態
sudo systemctl status stock-sync.timer

# 查看執行記錄
journalctl -u stock-sync.service -f
```

---

## 日誌管理

### 日誌輪轉（避免檔案過大）

建立 logrotate 配置 `/etc/logrotate.d/stock-sync`（Linux）：

```
/home/kentseng/Projects/stock-analyst/logs/stock_sync.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
}
```

macOS 可以用簡單的腳本清理：

```bash
# 只保留最近 30 天的日誌
find /Users/kentseng/Projects/stock-analyst/logs -name "*.log" -mtime +30 -delete
```

---

## 注意事項

### 1. 首次執行時間較長

第一次執行 `stock-sync` 時，需要下載 embedding 模型（約 2-5 分鐘），之後就會很快。

```bash
# 建議手動執行一次，確保模型已下載
uv run stock-sync -v
```

### 2. 確保 Qdrant 運行

cronjob 執行前，確保 Qdrant Docker 容器正在運行：

```bash
docker ps | grep qdrant
```

如果沒運行，啟動它：

```bash
docker compose up -d
```

### 3. 網路連線

確保執行環境可以訪問：
- FinMind API (`https://api.finmindtrade.com`)
- Qdrant (`localhost:6333`)

### 4. FinMind API 限制

免費額度有請求限制，建議：
- 註冊取得 API token（填入 `config.yaml`）
- 或減少同步頻率

---

## 監控與告警

### 簡單的告警腳本

```bash
#!/bin/bash
# alert_if_failed.sh

LOG_FILE="/Users/kentseng/Projects/stock-analyst/logs/stock_sync.log"
LAST_LINE=$(tail -1 "$LOG_FILE")

if echo "$LAST_LINE" | grep -q "Sync failed"; then
    # 發送 email 或其他通知
    echo "Stock sync failed!" | mail -s "Alert: Stock Sync Failed" your@email.com
fi
```

---

## 故障排除

### Cron 沒有執行？

1. 檢查 cron 日誌：
   ```bash
   # macOS
   log show --predicate 'process == "cron"' --last 1h

   # Linux
   grep CRON /var/log/syslog
   ```

2. 確認腳本有執行權限：
   ```bash
   ls -l /Users/kentseng/Projects/stock-analyst/sync_cron.sh
   ```

3. 手動測試腳本：
   ```bash
   /Users/kentseng/Projects/stock-analyst/sync_cron.sh
   ```

### 資料沒有更新？

檢查日誌：

```bash
tail -50 /Users/kentseng/Projects/stock-analyst/logs/stock_sync.log
```

查看 Qdrant 資料量：

```bash
uv run python -c "
from tw_stock_analyst.vectordb.qdrant_client import StockVectorDB
db = StockVectorDB()
info = db.get_collection_info()
print(f\"Total vectors: {info.get('vectors_count', 0)}\")
"
```

---

## 範例 Cron 時間表

```
分 時 日 月 週    說明
0  9  *  *  *    每天 9:00
30 14 *  *  1-5  週一到週五 14:30
0  9  *  *  1    每週一 9:00
0  */6 * *  *    每 6 小時
*/30 9-13 * * 1-5 週一到週五，9:00-13:00，每 30 分鐘
```

---

## 完整範例

最簡單的 cronjob 設定（每天收盤後更新）：

```bash
# 編輯 crontab
crontab -e

# 加入以下行（週一到週五 14:30 執行）
30 14 * * 1-5 cd /Users/kentseng/Projects/stock-analyst && /opt/homebrew/bin/uv run stock-sync
```

完成！🎉
