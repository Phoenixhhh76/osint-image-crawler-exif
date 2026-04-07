# Arachnida 實作差距檢查表（依目前程式碼）

對照檔案：
- `spider.py`
- `scorpion.py`
- 參考規格：`CyberD1_arachnide_en.subject.pdf`

---

## 1) Mandatory 條文對照結果

### Exercice 1 - Spider

- **需求：`./spider [-rlp] URL`**
  - 現況：`python3 spider.py [-r] [-l N] [-p PATH] URL`
  - 判定：**符合（腳本形式可接受）**

- **需求：`-r` 可遞迴下載圖片**
  - 現況：有 BFS 遞迴流程，`-r` 開關正常
  - 判定：**符合**

- **需求：`-r -l [N]` 設定遞迴深度，預設 5**
  - 現況：`DEFAULT_DEPTH = 5`，`-l` 已實作
  - 判定：**符合**

- **需求：`-p [PATH]` 設定輸出路徑，預設 `./data/`**
  - 現況：`DEFAULT_OUTPUT = Path("./data")`，`-p` 已實作
  - 判定：**符合**

- **需求：預設下載 `.jpg/.jpeg/.png/.gif/.bmp`**
  - 現況：`ALLOWED_EXTENSIONS` 已含以上副檔名
  - 判定：**符合**

### Exercice 2 - Scorpion

- **需求：`./scorpion FILE1 [FILE2 ...]`**
  - 現況：`python3 scorpion.py FILE1 [FILE2 ...]`
  - 判定：**符合（腳本形式可接受）**

- **需求：至少支援與 spider 相同副檔名**
  - 現況：`SUPPORTED_EXTENSIONS` 與 spider 一致
  - 判定：**符合**

- **需求：顯示基本屬性（如建立日期）與 EXIF**
  - 現況：有檔案屬性、影像屬性、EXIF、其他 metadata
  - 判定：**符合**

- **需求：輸出格式可自定**
  - 現況：終端文字輸出，結構清楚
  - 判定：**符合**

---

## 2) 目前風險與可加強點（非硬性必做，但建議）

### 已完成調整（最新）

- **Scorpion 時間欄位已做 Linux/macOS 相容化**
  - 現況：`created_at` 搭配 `created_at_source`，並額外輸出 `status_changed_at`。
  - 效果：避免把 Linux 的 `st_ctime` 誤解為建立時間。

- **新增一鍵自測腳本 `run_checks.sh`**
  - 現況：可檢查 Python、依賴套件、語法編譯、`spider` 基本測試、`scorpion` 基本測試。
  - 用法：`./run_checks.sh` 或 `./run_checks.sh "https://example.com"`。

### 高優先（建議先補）

- **Spider 目前只下載 URL 副檔名明確的圖片**
  - 現況：`iter_image_links()` 會先判斷連結副檔名，若 `<img src>` 沒副檔名（但回應其實是圖片）會被略過。
  - 風險：某些網站常用無副檔名圖片路徑，可能少抓。
  - 建議：先嘗試下載，再以 `Content-Type` 決定是否儲存。

- **Spider 沒有限制同網域**
  - 現況：遞迴會跟著所有 HTTP/HTTPS 連結走。
  - 風險：容易爬到外站，範圍失控。
  - 建議：新增「僅同網域」策略（至少可作為可切換選項）。

### 中優先（穩定性提升）

- **未處理 robots.txt / 爬取頻率**
  - 規格未強制，但在 defense 被問倫理與實務時常見。
  - 建議：至少在 README 說明未實作 robots；可加簡單延遲（如 `sleep`）。

- **Linux 評測環境的時間欄位語意**
  - Linux 上 `st_ctime` 通常是 inode status change time，不等於建立時間。
  - 建議：輸出 `created_at_source` 與 `status_changed_at`，口試時主動說明。

### 低優先（展示度提升）

- **錯誤碼策略可更一致**
  - 目前 scorpion 只要有任一檔案失敗就回傳 1（這合理）。
  - 可在 README 明確寫回傳碼語意，增加專業度。

---

## 3) Defense 前快速驗收指令

### Linux 評測前置（建議）

```bash
python3 --version
python3 -m pip install --user requests beautifulsoup4 pillow
python3 -m py_compile spider.py scorpion.py
```

### macOS 本機快速自測（建議）

```bash
python3 -m pip install requests beautifulsoup4 pillow
chmod +x run_checks.sh
./run_checks.sh
```

### Spider

```bash
python3 spider.py "https://example.com"
python3 spider.py -r "https://example.com"
python3 spider.py -r -l 1 "https://example.com"
python3 spider.py -r -l 2 -p ./data_test "https://example.com"
```

### Scorpion

```bash
python3 scorpion.py ./data/sample.jpg
python3 scorpion.py ./data/sample.jpg ./data/sample.png ./data/sample.gif
python3 scorpion.py ./nope.jpg ./data/sample.jpg
```

---

## 4) 結論

以目前程式碼來看，**Mandatory 核心要求已達成**。  
若要提高穩定性與口試說服力，優先補：

1. spider 對「無副檔名但為圖片」的處理  
2. 遞迴同網域限制（避免範圍外爬取）

補完這兩點後，整體完整度會明顯更高。

---

## 5) 當前專案狀態（2026-04-07）

- Mandatory：**可交付**
- Linux 評測注意點：**已處理（scorpion 時間欄位）**
- 自測工具：**已提供（`run_checks.sh`）**
- 建議評測前動作：在乾淨環境重新安裝依賴並跑一次 `run_checks.sh`
