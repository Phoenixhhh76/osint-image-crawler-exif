# Cybersecurity Piscine - Arachnida（專案要求中文翻譯）

## 專案資訊

- **摘要**：網頁爬取與中繼資料（metadata）入門專案  
- **版本**：1.00

## 目錄（翻譯）

1. 介紹（Introduction）
2. 前言（Prologue）
3. 必做部分（Mandatory Part）
4. 練習 1 - Spider
5. 練習 2 - Scorpion
6. Bonus 部分
7. 繳交與同儕評分

---

## I. 介紹（Introduction）

此專案將讓你學會處理來自網路的資料。

- 首先，你要建立一個小程式，自動從網頁擷取資訊。
- 接著，你要建立第二個程式，用來分析這些檔案並操作其中的 metadata。

Metadata（中繼資料）是用來描述其他資料的資訊，也就是「關於資料的資料」。  
它常被用來描述圖片與文件中的資訊，也可能揭露建立或修改這些檔案的人之敏感資訊。

---

## II. 前言（Prologue）

蛛形綱（Arachnids）屬於螯肢亞門（chelicerate arthropods），全球有超過 100,000 個不同物種。  
其中包含蜘蛛，也包含蜱蟲、蠍子與蟎。  
蛛形綱最典型的共同特徵是四對腳，以及可用來抓取食物的尖銳附肢（chelicerae）。

---

## III. 必做部分（Mandatory Part）

你必須建立兩個程式，程式可以是腳本（script）或可執行檔（binary）。

- 若你使用編譯型語言，必須提交完整原始碼，並在評分時完成編譯。
- 你可以使用能建立 HTTP 請求與處理檔案的函式或函式庫。
- **但每個程式的核心邏輯必須由你自行開發。**

因此，使用 `wget` 或 `scrapy` 會被視為作弊，**本專案直接 0 分**。

---

## IV. 練習 1 - Spider

`spider` 程式必須能在提供 URL 後，**遞迴地**從網站擷取所有圖片。

### 指令格式

```bash
./spider [-rlp] URL
```

### 參數要求

- `-r`：遞迴下載參數 URL 中可抓到的圖片。
- `-r -l [N]`：設定遞迴下載最大深度。
  - 若未指定，預設深度為 `5`。
- `-p [PATH]`：設定下載檔案儲存路徑。
  - 若未指定，預設使用 `./data/`。

### 預設需下載的副檔名

- `.jpg` / `.jpeg`
- `.png`
- `.gif`
- `.bmp`

---

## V. 練習 2 - Scorpion

第二個程式 `scorpion` 會接收圖片檔案作為參數，並必須能解析 EXIF 與其他 metadata，顯示在螢幕上。

### 基本要求

- 至少要相容於 `spider` 處理的相同副檔名。
- 需顯示基本屬性（例如建立日期）與 EXIF 資料。
- 輸出格式可自行決定。

### 指令格式

```bash
./scorpion FILE1 [FILE2 ...]
```

---

## VI. Bonus 部分

你可以加入以下功能來加分：

- 為 `scorpion` 新增選項，能對指定檔案的 metadata 進行「修改 / 刪除」。
- 製作美觀的圖形化介面（GUI），用於檢視與管理 metadata。

> Bonus 只會在 Mandatory **完美達成**時才評估。  
> 「完美」表示必做部分已完整完成，且功能無故障。  
> 只要有任何必做要求未全部通過，Bonus 將完全不評分。

---

## VII. 繳交與同儕評分（Submission and peer-evaluation）

請照慣例將作業提交到你的 Git repository。  
評分（defense）時只會檢查 repository 內的內容。  
請務必再次確認資料夾與檔名是否正確。
