# OSINT 圖片爬蟲與 EXIF 分析器

這是一個可直接放上 GitHub 的 OSINT 小型作品集專案，重點展示我對網站圖片爬取與影像中繼資料分析的理解與實作能力。

專案核心分成兩個工具：

- `spider`：從目標網站擷取圖片，支援遞迴抓取、深度限制與輸出路徑設定
- `scorpion`：分析圖片基本資訊、EXIF 與其他 metadata，協助辨識潛在線索與隱私外洩風險

## 為什麼這算 OSINT

OSINT 不只是蒐集公開資料，也包含對公開資料做整理、交叉比對與分析。這個專案對應的能力包含：

- 從公開網頁自動化擷取影像資源
- 對圖片進行 metadata / EXIF 解析
- 從拍攝時間、裝置資訊、格式資訊等欄位辨識可用線索
- 理解資料蒐集過程中的合法、倫理與隱私邊界

## 功能

### `spider`

- 支援 `http://` 與 `https://`
- 可選擇是否遞迴抓取 `-r`
- 可設定最大深度 `-l`
- 可設定下載路徑 `-p`
- 限制於起始 URL 的相同 hostname，避免遞迴範圍失控
- 僅處理題目要求的圖片格式：`.jpg`、`.jpeg`、`.png`、`.gif`、`.bmp`

### `scorpion`

- 分析多個圖片檔案
- 顯示檔案基本資訊：名稱、路徑、大小、時間戳記
- 顯示圖片資訊：格式、模式、尺寸
- 顯示 EXIF 資料
- 顯示其他 metadata，例如 PNG textual info
- 對不存在檔案、非支援格式與解析失敗情況提供錯誤處理

## 快速開始

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
chmod +x spider scorpion run_checks.sh
```

### 啟動 `spider`

```bash
./spider "https://example.com"
./spider -r "https://example.com"
./spider -r -l 2 -p ./data_test "https://example.com"
```

### 啟動 `scorpion`

```bash
./scorpion ./data/sample.jpg
./scorpion ./data/sample.jpg ./data/sample.png
```

### 一鍵自測

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

## 安全與倫理聲明

這個專案只應用於合法、授權、教育與研究用途。進行網站爬取與 metadata 分析時，應注意：

- 尊重網站使用條款與 `robots.txt`
- 避免高頻率請求造成服務負載
- 注意 metadata 可能涉及隱私、位置與裝置資訊
- 不要將工具用於未經授權的資料蒐集

## 可以展示的能力

如果你要把這個專案放到 GitHub 或履歷，可以強調：

- 我能實作基礎 OSINT 自動化流程
- 我理解網頁 crawler 的運作方式與限制
- 我能解析影像 EXIF / metadata 並說明其隱私意義
- 我具備基礎的安全輸入處理、錯誤處理與測試意識
