# Arachnida 實作前資安先備知識

這份文件整理在實作 `spider` 與 `scorpion` 之前，建議先具備的資安相關知識。

---

## 1. 必備核心知識

### HTTP / HTTPS 基礎

- **`GET` 請求與狀態碼**
  - `GET` 是爬蟲最常用的請求方法，用來向伺服器取回網頁或圖片資源。
  - 在程式中可透過 `response.status_code` 讀取狀態碼，作為流程分支依據。
  - 在瀏覽器可用 F12 查看狀態碼：
    - 開啟 F12 -> `Network` -> 重新整理頁面。
    - 點任一請求後，可在清單的 `Status` 欄看到（例如 200、301、404）。
    - 也可在該請求的 `Headers` 內看到對應狀態資訊。
  - Python `requests` 最小範例：
    ```python
    import requests

    url = "https://example.com"
    response = requests.get(url, timeout=10)
    print(response.status_code)
    ```
  - 常見處理方式：
    - 先判斷 `response.status_code`，再決定是否解析/下載。
    - 或使用 `response.raise_for_status()`，把 4xx/5xx 視為例外後統一進入錯誤處理。
  - 你需要能根據狀態碼決定行為，而不是只送出請求：
    - `200`：成功，繼續解析頁面或寫入圖片檔案。
    - `301/302`：轉址，應跟隨新 URL，避免漏抓內容。
    - `403`：拒絕存取，通常和權限或反爬策略有關，記錄後略過。
    - `404`：資源不存在，視為壞連結，記錄後繼續下一個目標。
    - `500`：伺服器錯誤，通常是對方站點暫時問題，應容錯不中斷。

- **常見 Header（`User-Agent`、`Content-Type`、`Location`）**
  - `User-Agent`：告訴伺服器請求來自什麼客戶端；某些站點會依它決定是否回應正常內容。
  - `Content-Type`：標示回傳內容型態（例如 `text/html`、`image/png`），可用來判斷要不要當圖片處理。
  - `Location`：轉址時伺服器提供的新目標 URL，處理 301/302 時會用到。
  - 在本專案中，懂 Header 可以避免把非圖片內容誤存成圖片檔。
  - 在瀏覽器可用 F12 查看：
    - `User-Agent`：`Network` -> 選一筆請求 -> `Headers` -> `Request Headers`
    - `Content-Type`：`Network` -> 選一筆請求 -> `Headers` -> `Response Headers`（有時 Request 也會有）
    - `Location`：只在 301/302 轉址回應中出現，位置在 `Response Headers`

- **Redirect 行為（301/302）**
  - 許多網站會把舊網址轉到新網址（例如 `http` 轉 `https`、舊頁轉新頁）。
  - 若爬蟲不處理轉址，常見後果是「連得到頁面但抓不到圖」。
  - 實作時要確保請求庫會跟隨轉址，並以最終 URL 繼續流程。
  - 本專案實作範例（`requests` 對 `GET` 預設會自動跟隨轉址）：
    ```python
    import requests

    url = "http://example.com"
    resp = requests.get(url, timeout=10)  # GET 預設 allow_redirects=True

    print("status:", resp.status_code)      # 最終回應狀態
    print("final_url:", resp.url)           # 轉址後落地 URL
    print("redirected:", len(resp.history) > 0)  # 是否有經過轉址
    ```
  - 在你目前 `spider.py` 中，`fetch_html()` 與 `download_image()` 的 `session.get(...)` 就是此行為的實際應用。

- **HTTPS 與 TLS 憑證驗證**
  - HTTPS 透過 TLS 提供加密傳輸，避免資料在途中被竊聽或竄改。
  - 憑證驗證可確認你連到的是正確站點，不是被中間人攻擊的假站。
  - 實務上不應隨意關閉憑證驗證（例如 `verify=False`），除非是受控測試環境。
  - 在資安情境下，這是「可靠取得資料」的基本前提。
  - `TLS`（Transport Layer Security）的三個核心目的：
    - 加密（Confidentiality）：避免資料內容被旁路偷看。
    - 完整性（Integrity）：避免資料在傳輸中被竄改。
    - 驗證（Authentication）：透過憑證確認對方站點身分。
  - 本專案為何要理解 TLS：
    - `spider` 會抓 `https://` 網站，若不理解 TLS/憑證驗證，常無法判斷連線錯誤原因。
    - 在資安場景中，是否正確驗證憑證會直接影響資料可信度。
  - 是否「必須」：
    - 題目沒有要求你自行實作 TLS 協定（不需要自己寫加密流程）。
    - 但必須能正確處理 HTTPS 請求，並保持預設憑證驗證（`requests` 預設 `verify=True`）。
    - 結論：不必手寫 TLS，但要正確使用支援 TLS 的 HTTP 客戶端。

為什麼重要：`spider` 需要穩定抓取網站內容，請求與回應行為是核心。

### Web Scraping 的合法與倫理邊界

- 知道 `robots.txt` 的用途
- 確認目標網站條款（Terms of Service）
- 避免高頻率請求造成網站負載（避免變相 DoS）

`robots.txt` 補充解釋（本專案常見口試題）：

- `robots.txt` 是網站根目錄的規範檔案（例：`https://example.com/robots.txt`），用來告訴爬蟲哪些路徑可爬、哪些不建議爬。
- 常見欄位：
  - `User-agent`：規則套用對象（特定爬蟲或 `*`）。
  - `Disallow`：不希望爬取的路徑。
  - `Allow`：允許爬取的路徑（可搭配 `Disallow` 使用）。
  - `Crawl-delay`：建議抓取間隔（非所有爬蟲都支援）。
- 本專案是否必做：
  - Subject 沒有強制要求你實作 robots parser。
  - 但在真實環境中，應尊重 `robots.txt` 與網站條款，避免法律與倫理風險。
- 建議口試回答方式：
  - 「本次以 mandatory 規格為主，未實作 robots 解析；但我知道其用途，正式爬蟲會遵守 `robots.txt` 與站點政策。」

為什麼重要：技術可行不代表合法或合理，專案中應保持安全與倫理習慣。

### URL 與網域處理

- 絕對 URL vs 相對 URL
  - 絕對 URL：包含完整 `scheme + host`，例如 `https://example.com/img/a.jpg`。
  - 相對 URL：例如 `/img/a.jpg`、`../img/a.jpg`、`a.jpg`，必須用「當前頁面 URL」轉成絕對 URL 後才能請求。
  - 專案情境（`spider URL -r N -l N -p PATH`）：
    - 當前頁面：`https://site.com/blog/post/index.html`
    - `src="/img/a.jpg"` -> `https://site.com/img/a.jpg`
    - `src="img/a.jpg"` -> `https://site.com/blog/post/img/a.jpg`
    - `src="../img/a.jpg"` -> `https://site.com/blog/img/a.jpg`
  - 重點：不要手動字串相加，應使用 URL parser/join 函式。
- 同網域 / 跨網域判斷
  - 目的：限制遞迴範圍，避免爬蟲無限擴散到外站。
  - 常見策略（請在 README 寫清楚你採哪一種）：
    - 嚴格同 host：只允許 `example.com`，不含子網域。
    - 同主網域：允許 `a.example.com`、`cdn.example.com`（進階）。
    - 白名單：只允許特定網域集合。
  - 專案建議：mandatory 先做「同 host」即可，規則清楚最重要。
  - 常見錯誤：
    - 用字串包含判斷（`"example.com" in url`）會被 `evil-example.com` 誤判。
    - 忘記 `http/https` 與 port 差異。
- URL 正規化（去除片段、處理 query、拼接路徑）
  - 目的：去重與穩定遞迴，避免同資源被重複抓取。
  - 去除片段（fragment）：
    - `https://a.com/p.jpg#top` 與 `#info` 通常是同一資源，應先移除 `#...`。
  - query 策略：
    - 保留 query：較不漏資料，但可能重複更多。
    - 清除追蹤參數（如 `utm_*`、`fbclid`）：降低重複。
    - 全刪 query：最簡單，但可能把不同圖片誤當同一張。
  - 路徑拼接：處理 `.`、`..`、多斜線與尾斜線差異，交給標準函式，不要自己拼接。
  - `arachnide` 最小實作範例（Python）：
    ```python
    from urllib.parse import urljoin, urlparse, urlunparse, parse_qsl, urlencode

    def normalize_url(base_url: str, raw_link: str) -> str:
        # 1) 相對 -> 絕對
        abs_url = urljoin(base_url, raw_link)
        p = urlparse(abs_url)

        # 2) 只接受 http/https
        if p.scheme not in ("http", "https"):
            return ""

        # 3) 去除 fragment
        fragment = ""

        # 4) 清掉常見追蹤參數（可依需求調整）
        clean_query = []
        for k, v in parse_qsl(p.query, keep_blank_values=True):
            if k.startswith("utm_") or k in ("fbclid",):
                continue
            clean_query.append((k, v))
        query = urlencode(clean_query, doseq=True)

        return urlunparse((p.scheme, p.netloc, p.path, p.params, query, fragment))
    ```
  - 搭配建議：對「正規化後 URL」做 `visited set` 去重，再決定是否遞迴。

為什麼重要：遞迴爬取時若判斷錯誤，容易抓不到圖或無限擴散。

### 檔案與路徑安全

- 避免 Path Traversal（如 `../`）
  - 風險：下載連結或檔名若含 `../`，可能把檔案寫到目標目錄外（例如覆蓋系統檔）。
  - 專案情境：`spider ... -p PATH` 由使用者指定輸出資料夾，這是高風險輸入點。
  - 防護重點：
    - 先把「輸出根目錄」做 `resolve()`（或等效絕對化）。
    - 最終輸出檔也做 `resolve()`，並檢查它是否仍位於根目錄之下。
    - 不合法就拒絕寫入，而不是嘗試「自動修復」。
- 檔名清洗（移除危險字元）
  - 風險：URL 末段可能含控制字元、路徑分隔符或保留字元，造成寫檔錯誤或安全問題。
  - 實務建議：
    - 僅保留白名單字元（英數、`-`、`_`、`.`）。
    - 空檔名時使用預設名稱（例如 `downloaded_file`）。
    - 限制最大長度，避免檔案系統錯誤。
- 使用安全路徑拼接方式（避免手動字串拼接）
  - 反例：`save_path = base + "/" + filename`（平台差異、重複斜線、跳脫路徑難防）。
  - 正確：使用 `Path(base) / filename` 或 `os.path.join`，再做 canonical path 檢查。
  - `spider` 最小實作範例（Python）：
    ```python
    from pathlib import Path
    import re

    def safe_filename(raw_name: str) -> str:
        name = re.sub(r"[^A-Za-z0-9._-]", "_", raw_name).strip("._")
        return name[:120] or "downloaded_file"

    def safe_output_path(base_dir: str, raw_name: str) -> Path:
        root = Path(base_dir).resolve()
        target = (root / safe_filename(raw_name)).resolve()
        if root not in target.parents and target != root:
            raise ValueError("Path traversal detected")
        return target
    ```

為什麼重要：`-p PATH` 與下載檔案寫入磁碟是高風險點。

### EXIF / Metadata 安全意識

- 知道 EXIF 可能包含 GPS、時間、裝置資訊
  - 常見欄位：`GPSLatitude/GPSLongitude`、`DateTimeOriginal`、`Make/Model`。
  - 風險：一張看似普通照片，可能直接暴露拍攝地點、時間與設備資訊。
- 理解 metadata 可能揭露使用者隱私與行為軌跡
  - 單張看起來資訊有限，但多張照片可拼成「活動路徑」與「生活規律」。
  - `scorpion` 的價值：把這些隱含資訊可視化，讓使用者理解洩漏面。
- 理解不同格式（JPG/PNG/GIF/BMP）metadata 支援程度不同
  - JPEG：通常 EXIF 最完整，最常見於手機相機照片。
  - PNG：常見文字區塊（tEXt/iTXt），不一定有 EXIF。
  - GIF/BMP：可讀 metadata 通常較少，需有「欄位可能缺失」的預期。
  - 專案實作重點：不要假設每個欄位都存在，缺欄位應顯示 `N/A` 並繼續處理。
- `scorpion` 最小實作示意（例外安全）：
  ```python
  from PIL import Image, ExifTags

  def read_exif_safe(image_path: str) -> dict:
      try:
          img = Image.open(image_path)
          exif = img.getexif()
          if not exif:
              return {}
          tag_map = {ExifTags.TAGS.get(k, str(k)): v for k, v in exif.items()}
          return tag_map
      except Exception:
          # 單檔失敗不應拖垮整批流程
          return {}
  ```

為什麼重要：`scorpion` 的核心就是解析與顯示這些敏感資訊。

---

## 2. 與本專案直接相關的攻擊面

### SSRF（Server-Side Request Forgery）意識

雖然 `arachnide` 是本地工具，風險比伺服器端低，但這組習慣在你未來做 API 時非常重要。  
若把「使用者提供 URL」直接拿去請求，可能被用來探測內網（例如 `127.0.0.1`、`10.x.x.x`、`192.168.x.x`）。

- 專案實務建議（可直接沿用到 `spider`）：
  - 只允許 `http/https`（呼應前面 URL 正規化）。
  - 拒絕 `localhost`、`127.0.0.1`、私有網段與 link-local 位址。
  - 每個請求都設 `timeout`，避免長時間卡死。
  - 可視需求限制 redirect 次數，避免被導向不預期目標。
- 最小實作示意（Python）：
  ```python
  from urllib.parse import urlparse
  import ipaddress
  import socket

  def is_public_target(url: str) -> bool:
      p = urlparse(url)
      if p.scheme not in ("http", "https") or not p.hostname:
          return False
      try:
          ip = ipaddress.ip_address(socket.gethostbyname(p.hostname))
      except Exception:
          return False
      if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved:
          return False
      return True
  ```

### 惡意內容與檔案偽裝

- 副檔名不等於真實格式（例如 `.jpg` 但內容不是圖片）
  - `a.jpg` 可能其實是 HTML、script 或損壞檔案；不能只看 URL 或檔名判斷。
- 下載後應嘗試驗證內容可否被影像函式庫正確解析
  - 建議雙重檢查：
    - 下載前看 `Content-Type`（只收 `image/*`）。
    - 下載後用影像函式庫嘗試解析（例如 Pillow `verify()`）。
  - 若驗證失敗，應刪除該檔或標記失敗，避免後續流程誤用。
- `spider` 最小實作示意（Python）：
  ```python
  from PIL import Image

  def is_valid_image(path: str) -> bool:
      try:
          with Image.open(path) as img:
              img.verify()
          return True
      except Exception:
          return False
  ```

### 資源耗盡風險

- 遞迴深度太高
  - 深度每 +1，頁面數可能呈倍數成長，容易拖慢甚至失控。
- 單頁圖片過多
  - 某些頁面可能上百張圖，若不設上限可能造成大量 I/O。
- 檔案過大造成磁碟或記憶體壓力
  - 巨大檔案會耗盡磁碟，或在讀入時造成記憶體壓力。

建議：設定最大深度、單頁下載上限、最大檔案大小、請求 timeout 與重試次數上限。

- `spider` 參數層建議（對應 subject）：
  - `-r`：嚴格限制遞迴層數（例如最多 5）。
  - `-l`：限制同頁最多下載圖片數。
  - 下載流式寫入時檢查累積 bytes，超過上限立即中止。
  - 失敗重試次數固定上限（例如 2~3 次），避免無限重試。
- 流式大小限制示意（Python）：
  ```python
  def save_with_size_limit(resp, out_file, max_bytes: int) -> None:
      total = 0
      with open(out_file, "wb") as f:
          for chunk in resp.iter_content(chunk_size=8192):
              if not chunk:
                  continue
              total += len(chunk)
              if total > max_bytes:
                  raise ValueError("File too large")
              f.write(chunk)
  ```

---

## 3. 最小安全實作準則（上手即用）

- 僅允許 `http://` 與 `https://`
- 每次請求加 `timeout`（例如 5~15 秒）
- 遇到錯誤時不中斷整體流程（記錄錯誤後繼續）
- 遞迴爬蟲要有 `visited` 集合，避免重複抓取
- 下載前檢查 Content-Type，下載後再做一次副檔名/內容驗證
- 所有輸出檔案都要落在指定資料夾內（不可跳脫）
- 對 metadata 輸出做好例外處理（避免單檔壞掉導致整體崩潰）

---

## 4. 三天速成學習清單（專案導向）

### Day 1：Web 與請求基礎

- 學習目標：
  - HTTP/HTTPS、狀態碼、redirect、header
  - URL 拼接與正規化
- 實作練習：
  - 用 Python 發送 `GET`，印出狀態碼與最終 URL
  - 測試 301/302 轉址網站
- 驗收標準：
  - 能解釋何時會 403/404
  - 能正確把相對路徑轉成絕對 URL

### Day 2：爬蟲安全與下載策略

- 學習目標：
  - HTML 解析抓 `<img src>`
  - 遞迴策略（深度限制、visited）
  - 安全儲存與檔名處理
- 實作練習：
  - 完成基本 `spider`（含 `-r -l -p`）
  - 加入 timeout、錯誤處理、過濾非圖片連結
- 驗收標準：
  - 遞迴不會無限循環
  - 下載路徑不會被 `../` 逃逸

### Day 3：Metadata 與隱私風險

- 學習目標：
  - 讀取 EXIF 與基本檔案屬性
  - 了解 metadata 隱私風險
- 實作練習：
  - 完成 `scorpion FILE1 [FILE2 ...]`
  - 針對不存在檔案、非圖片檔案、無 EXIF 檔案做容錯
- 驗收標準：
  - 能清楚列出每張圖可取得的 metadata
  - 錯誤輸入不會讓程式整體中斷

---

## 5. 進階加分方向（對應 Bonus）

- 新增 metadata 修改/刪除功能時，務必先備份原檔
- 設計 GUI 時保留「唯讀模式」避免誤改
- 操作記錄（log）可追蹤誰在何時修改了哪些 metadata

---

## 6. 快速自我檢查（提交前）

- `spider` 是否符合 `-r -l -p` 規格與預設值？
- 是否至少支援 `.jpg/.jpeg/.png/.gif/.bmp`？
- `scorpion` 是否能顯示基本屬性與 EXIF？
- 異常輸入（壞檔/不存在檔）是否有穩定錯誤處理？
- 是否避免使用 `wget`、`scrapy` 這類被禁止工具？

若以上都能穩定通過，你就有足夠的資安基礎與工程準備進入正式實作。
