# Smart-Doc：智慧文件問答系統

## 這是什麼？

想像你有一個超級聰明的助教，可以幫你閱讀大量的技術文件，然後回答你的問題。這就是 **Smart-Doc** 的功能！

這個專案是一個 **RAG 系統**（Retrieval-Augmented Generation，檢索增強生成），讓你可以：

- 上傳技術文件（Word、Excel、Markdown）
- 用自然語言提問（例如：「使用者登入的 API 是什麼？」）
- 獲得智慧的回答，還會告訴你答案來自哪份文件

---

## RAG 是什麼？用簡單的方式解釋

### 傳統搜尋 vs RAG

| 傳統搜尋 | RAG 智慧搜尋 |
|---------|-------------|
| 只能找到包含關鍵字的文件 | 能理解你問題的「意思」 |
| 回傳一堆文件讓你自己找 | 直接給你答案 |
| 「登入」找不到「認證」相關內容 | 知道「登入」和「認證」是相關概念 |

### RAG 的運作原理

```
┌─────────────────────────────────────────────────────────────┐
│                      RAG 運作流程                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   1. 文件處理階段                                            │
│   ┌──────────┐    ┌──────────┐    ┌──────────┐             │
│   │ 上傳文件  │ → │ 切成小段  │ → │ 轉成向量  │             │
│   │ (Word等) │    │ (分塊)   │    │ (嵌入)   │             │
│   └──────────┘    └──────────┘    └──────────┘             │
│                                          ↓                  │
│                                   ┌──────────┐             │
│                                   │ 存入資料庫│             │
│                                   │ (Qdrant) │             │
│                                   └──────────┘             │
│                                                             │
│   2. 問答階段                                               │
│   ┌──────────┐    ┌──────────┐    ┌──────────┐             │
│   │ 使用者提問│ → │ 搜尋相關  │ → │  AI 生成  │             │
│   │ 「API是？」│   │ 文件片段  │    │   答案   │             │
│   └──────────┘    └──────────┘    └──────────┘             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 什麼是「向量」？

向量就像是文字的「數字指紋」。電腦不懂中文，但它懂數字！

- 「貓」可能變成 `[0.2, 0.8, 0.1, ...]`
- 「狗」可能變成 `[0.3, 0.7, 0.2, ...]`
- 「汽車」可能變成 `[0.9, 0.1, 0.4, ...]`

因為貓和狗都是動物，所以它們的向量會「比較接近」；而汽車的向量就會「比較遠」。這樣電腦就能理解語意了！

---

## 專案架構

```
smart-doc/
├── src/                    # 主要程式碼
│   ├── main.py            # 程式入口點
│   ├── config.py          # 設定檔
│   ├── api/               # API 相關
│   │   └── routes/        # 各種 API 端點
│   ├── core/              # 核心功能
│   │   ├── parsers/       # 文件解析器（讀取 Word、Excel 等）
│   │   ├── chunkers/      # 文件切塊器
│   │   ├── extractors/    # 資訊提取器
│   │   └── retrievers/    # 搜尋引擎
│   ├── services/          # 商業邏輯
│   └── infrastructure/    # 外部服務整合
├── tests/                  # 測試程式
├── scripts/               # 工具腳本
├── docker-compose.yml     # Docker 容器設定
└── requirements.txt       # Python 套件清單
```

---

## 使用的技術

### 後端框架
- **FastAPI**：一個現代、快速的 Python 網頁框架，用來建立 API
- **Python 3.11+**：主要程式語言

### AI 與機器學習
- **LlamaIndex**：RAG 框架，幫助整合文件和 AI
- **HuggingFace Transformers**：提供文字轉向量的模型
- **BGE 模型**：專門為中文優化的嵌入模型

### 資料庫
- **Qdrant**：向量資料庫，專門儲存和搜尋向量

### AI 語言模型（擇一使用）
- **Ollama**：在自己電腦上執行的 AI（離線可用）
- **Anthropic Claude**：雲端 AI 服務（需要網路）

### 開發工具
- **Docker**：容器化技術，讓程式更容易部署
- **pytest**：Python 測試框架

---

## 主要功能

### 1. 文件上傳與處理

支援三種文件格式：

| 格式 | 說明 | 適用情境 |
|------|------|---------|
| `.md` | Markdown 文件 | 技術文件、說明書 |
| `.docx` | Word 文件 | 正式文件、報告 |
| `.xlsx` | Excel 試算表 | 資料表、規格定義 |

### 2. 語意搜尋

不只是關鍵字搜尋，而是理解你的意思：

```
問：「怎麼驗證使用者身份？」
→ 會找到關於「登入」、「認證」、「Token」的內容
```

### 3. 智慧問答

直接回答你的問題，並標註資料來源：

```
問：「使用者 API 有哪些？」

答：根據文件，使用者相關的 API 包括：
    - GET /api/users - 取得使用者列表
    - POST /api/users - 建立新使用者
    - GET /api/users/{id} - 取得特定使用者

    📄 來源：API 規格文件.docx，第 3 章
```

### 4. 跨文件關聯

自動找出不同文件之間的關係：

```
查詢「訂單 API」時，系統會自動連結：
├── API 文件中的 /api/orders 端點
├── 資料庫文件中的 orders 資料表
└── 實體定義中的 Order 物件
```

---

## API 端點說明

| 端點 | 方法 | 功能 |
|------|------|------|
| `/health` | GET | 檢查系統是否正常運作 |
| `/api/documents/upload` | POST | 上傳新文件 |
| `/api/documents` | GET | 列出所有已上傳的文件 |
| `/api/documents/{id}` | DELETE | 刪除指定文件 |
| `/api/query/search` | POST | 搜尋相關文件片段 |
| `/api/query/ask` | POST | 提問並獲得 AI 回答 |

---

## 如何開始使用？

### 前置需求

1. **Python 3.11** 或更新版本
2. **Docker** 和 **Docker Compose**
3. **至少 8GB RAM**（執行 AI 模型需要）

### 安裝步驟

```bash
# 1. 複製專案
git clone <專案網址>
cd smart-doc

# 2. 建立虛擬環境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 安裝套件
pip install -r requirements.txt

# 4. 啟動服務（使用 Docker）
docker-compose up -d

# 5. 初始化向量資料庫
python scripts/init_qdrant.py

# 6. 啟動 API 伺服器
uvicorn src.main:app --reload
```

### 測試是否成功

開啟瀏覽器，前往：`http://localhost:8000/health`

如果看到 `{"status": "healthy"}`，代表系統已經成功啟動！

---

## 學習資源

如果你想深入了解這個專案使用的技術，這裡有一些推薦資源：

### Python 基礎
- [Python 官方教學](https://docs.python.org/zh-tw/3/tutorial/)
- [莫煩 Python](https://mofanpy.com/)

### FastAPI
- [FastAPI 官方文件](https://fastapi.tiangolo.com/zh/)

### 機器學習與 AI
- [李宏毅機器學習課程](https://www.youtube.com/c/HungyiLeeNTU)
- [什麼是 Embedding？](https://www.youtube.com/results?search_query=word+embedding+explained)

### RAG 概念
- [RAG 簡介影片](https://www.youtube.com/results?search_query=RAG+retrieval+augmented+generation+explained)

---

## 常見問題

### Q: 為什麼不直接用 ChatGPT？

A: ChatGPT 只知道它訓練時學到的知識，不知道你公司內部的文件內容。RAG 讓 AI 可以「閱讀」你的文件，然後根據文件內容回答問題。

### Q: 資料會上傳到雲端嗎？

A: 如果使用 Ollama（本地 AI），所有資料都在你自己的電腦上，完全離線運作。如果使用 Anthropic Claude，問答時會將相關片段傳送到雲端處理。

### Q: 需要很好的電腦嗎？

A: 基本功能（使用雲端 AI）只需要一般電腦。如果要在本地執行 AI 模型，建議至少 16GB RAM 和支援 CUDA 的 NVIDIA 顯卡。

### Q: 可以處理多大的文件？

A: 單一文件最大 50MB。系統會自動將大文件切成小塊處理。

---

## 專案狀態

目前版本：**0.1.0（Alpha）**

這是一個開發中的專案，核心功能已經完成，但仍有許多功能正在開發中。歡迎學習和實驗！

---

## 貢獻指南

歡迎提交 Issue 或 Pull Request！

在提交之前，請確保：
1. 程式碼通過測試：`pytest`
2. 程式碼風格檢查：`ruff check .`
3. 型別檢查：`mypy src/`

---

## 授權

本專案僅供學習用途。

---

## 詞彙表

| 術語 | 英文 | 解釋 |
|------|------|------|
| RAG | Retrieval-Augmented Generation | 結合搜尋和 AI 生成的技術 |
| 向量 | Vector | 用數字陣列表示文字的方式 |
| 嵌入 | Embedding | 將文字轉換成向量的過程 |
| API | Application Programming Interface | 程式之間溝通的介面 |
| LLM | Large Language Model | 大型語言模型，如 ChatGPT |
| 語意搜尋 | Semantic Search | 根據意思（而非關鍵字）搜尋 |
