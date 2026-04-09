# OSINT 圖片爬蟲與 EXIF 分析器

此專案為一個以 Python 開發的輕量級 OSINT 圖片蒐集與中繼資料分析工具，適合應用於公開網站資訊盤點、圖片資產蒐集，以及影像 metadata 初步分析等情境。核心能力聚焦於：

- 從公開網站擷取圖片資源
- 解析圖片中繼資料與 EXIF 資訊

專案整體設計重點在於展示可交付的爬蟲開發能力、資料擷取與解析流程、例外處理品質，以及資訊安全與隱私風險意識，可作為網站資料蒐集、OSINT 前期調查或客製化爬蟲需求的技術展示基礎。

## 什麼是 OSINT，與本專案的關聯

OSINT（Open Source Intelligence，開源情報）指的是從合法、公開可取得的來源蒐集資訊，並進一步整理、分析與判讀，以形成具備調查、研判或決策價值的內容。在商業或專案應用上，OSINT 常見於公開資料蒐集、品牌監測、數位足跡盤點、素材追蹤與基礎風險識別等場景。

本專案對應的正是其中與公開圖片資料蒐集及 metadata 判讀相關的工作流程，具體包括：

- 從公開可存取的網頁擷取圖片檔案
- 解析可能具備調查價值的圖片中繼資料
- 辨識具隱私敏感性的欄位，例如時間戳、裝置資訊與內嵌描述
- 在爬取範圍、遞迴深度與錯誤處理上實施基本控制

## 工具

### `spider`

`spider` 用於自指定網站下載圖片檔案。

功能：

- 支援 `http://` 與 `https://`
- 提供遞迴爬取選項 `-r`
- 支援最大深度設定 `-l`
- 支援輸出目錄設定 `-p`
- 限制於與起始 URL 相同的 hostname
- 支援 `.jpg`、`.jpeg`、`.png`、`.gif`、`.bmp`

### `scorpion`

`scorpion` 用於讀取一個或多個圖片檔案，並輸出可取得的中繼資料內容。

功能：

- 顯示基本檔案資訊
- 顯示圖片格式、模式與尺寸
- 在可用情況下擷取 EXIF
- 顯示其他 metadata，例如 PNG 文字欄位
- 妥善處理檔案不存在、不支援副檔名與解析失敗等情況

## 技術棧

- Python 3
- `requests`：負責 HTTP 請求
- `BeautifulSoup`：負責 HTML 解析
- `Pillow`：負責圖片中繼資料與 EXIF 擷取

## 快速開始

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
chmod +x spider scorpion run_checks.sh
```

### 執行 `spider`

```bash
./spider "https://example.com"
./spider -r "https://example.com"
./spider -r -l 2 -p ./data_test "https://example.com"
```

### 執行 `scorpion`

```bash
./scorpion ./data/sample.jpg
./scorpion ./data/sample.jpg ./data/sample.png
```

### 執行檢查

```bash
bash ./run_checks.sh
bash ./run_checks.sh "https://www.python.org"
bash ./run_checks.sh --all
```

## 專案結構

```text
osint-image-crawler-exif/
├── .gitignore
├── README.md
├── README_zh-TW.md
├── requirements.txt
├── run_checks.sh
├── spider
├── spider.py
├── scorpion
├── scorpion.py
└── docs/
    ├── implementation_review_zh-TW.md
    ├── osint_prerequisites_zh-TW.md
    └── project_requirements_zh-TW.md
```

## 文件

- `README_zh-TW.md`：繁體中文專案簡介
- `docs/project_requirements_zh-TW.md`：題目需求翻譯與整理
- `docs/osint_prerequisites_zh-TW.md`：HTTP、URL、EXIF 與安全基礎說明
- `docs/implementation_review_zh-TW.md`：實作檢核與風險盤點

## 安全與倫理

本專案僅適用於合法、經授權、教育或研究情境。

使用或延伸此類工具時，應遵守以下原則：

- 尊重網站服務條款與 `robots.txt`
- 避免發送過量或具干擾性的請求
- 將圖片 metadata 視為可能涉及個資或敏感資訊的資料來源
- 不將 OSINT 工具用於未經授權的蒐集、監控或追蹤行為

## 專案可展示的實務能力

此專案可用於呈現以下實務面向的技術能力：

- 可依指定網站進行圖片資源蒐集，並控制爬取範圍、深度與輸出位置
- 可針對圖片檔案執行 metadata 與 EXIF 解析，支援基礎資料盤點與欄位檢視
- 可處理常見爬蟲需求中的錯誤情境，例如無效連結、格式限制與解析失敗
- 可將技術實作延伸至公開資料蒐集、數位資產盤點、OSINT 前期調查等應用方向
- 具備在功能開發之外，同步考量請求節制、授權範圍與敏感資訊處理的能力

## 適用情境

- 公開網站圖片資產蒐集
- 圖片 metadata 與 EXIF 初步盤點
- OSINT 前期資料整理與線索蒐集
- 客製化爬蟲需求的原型驗證

## 後續可改進方向

- 支援無副檔名的圖片 URL，透過 `Content-Type` 進行判斷
- 將 metadata 匯出為 JSON，便於後續分析與整合
- 強化 URL 正規化與去重邏輯
- 增加 GUI，或提供 metadata 編輯與移除功能
- 圖片重複偵測 : 做圖片指紋、近似重複圖比對、分群與溯源
