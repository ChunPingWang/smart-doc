# 系統設計文件 RAG 專案規格書

> **版本**: 1.0  
> **建立日期**: 2024-12  
> **文件類型**: 需求規格與技術架構

---

## 目錄

1. [專案概述](#1-專案概述)
2. [功能需求](#2-功能需求)
3. [非功能需求](#3-非功能需求)
4. [技術架構](#4-技術架構)
5. [技術清單](#5-技術清單)
6. [系統架構圖](#6-系統架構圖)
7. [專案目錄結構](#7-專案目錄結構)
8. [API 規格](#8-api-規格)
9. [資料模型](#9-資料模型)
10. [部署配置](#10-部署配置)
11. [開發階段規劃](#11-開發階段規劃)
12. [附錄](#12-附錄)

---

## 1. 專案概述

### 1.1 專案目標

建立一套針對系統分析與設計文件的 RAG (Retrieval-Augmented Generation) 系統，支援 Word、Excel、Markdown 格式的技術文件，提供智慧化的文件檢索與問答能力。

### 1.2 適用文件類型

| 文件類型 | 格式 | 內容範例 |
|----------|------|----------|
| API 規格 | .md, .docx | Endpoint、Request/Response Schema、錯誤碼 |
| 資料庫 Schema | .xlsx, .md | Table 定義、欄位規格、關聯關係 |
| 系統行為 | .docx, .md | 業務規則、流程描述、狀態轉換 |
| 設計文件 | .docx, .md | 架構說明、元件設計、介面定義 |

### 1.3 核心價值

- **跨文件關聯查詢**: 查詢 API 時自動帶出對應的 Table Schema 與 Entity 定義
- **結構化資訊保留**: 表格、程式碼區塊、層級結構完整保留
- **本地部署支援**: 敏感文件可完全在本地環境處理，不傳送至外部服務

---

## 2. 功能需求

### 2.1 文件匯入與解析

| 需求編號 | 需求描述 | 優先級 |
|----------|----------|--------|
| FR-001.1 | 系統應支援 Word (.docx) 文件匯入，保留標題層級、表格、清單結構 | P0 |
| FR-001.2 | 系統應支援 Excel (.xlsx) 文件匯入，識別 Table Schema 定義（欄位名稱、型別、描述、約束） | P0 |
| FR-001.3 | 系統應支援 Markdown (.md) 文件匯入，保留 heading hierarchy 與 code block | P0 |
| FR-001.4 | 系統應自動辨識文件類型（API 規格、資料庫 Schema、系統行為描述、流程圖說明） | P1 |
| FR-001.5 | 系統應支援批次匯入與增量更新 | P1 |
| FR-001.6 | 系統應支援文件版本管理，記錄更新歷史 | P2 |

### 2.2 內容結構化處理

| 需求編號 | 需求描述 | 優先級 |
|----------|----------|--------|
| FR-002.1 | 系統應從 API 規格文件中抽取 endpoint、HTTP method、request/response schema | P0 |
| FR-002.2 | 系統應從 Table Schema 文件中抽取 table name、column 定義、primary key、foreign key 關係 | P0 |
| FR-002.3 | 系統應從系統行為文件中抽取 entity name、business rule、workflow step | P1 |
| FR-002.4 | 系統應建立跨文件的實體關聯索引（API 對應 Entity、Entity 對應 Table） | P0 |
| FR-002.5 | 系統應識別並保留程式碼區塊的語言類型與完整內容 | P1 |

### 2.3 智慧檢索

| 需求編號 | 需求描述 | 優先級 |
|----------|----------|--------|
| FR-003.1 | 系統應支援自然語言查詢系統設計文件 | P0 |
| FR-003.2 | 系統應支援依文件類型過濾查詢結果 | P1 |
| FR-003.3 | 系統應支援依技術實體（API endpoint、Table name）精確查詢 | P0 |
| FR-003.4 | 查詢結果應自動關聯相關文件（查 API 時帶出對應 Table Schema） | P0 |
| FR-003.5 | 系統應支援 hybrid search（語意搜尋 + 關鍵字搜尋） | P1 |
| FR-003.6 | 系統應支援查詢結果的相關性分數顯示 | P2 |

### 2.4 回答生成

| 需求編號 | 需求描述 | 優先級 |
|----------|----------|--------|
| FR-004.1 | 系統應基於檢索結果生成結構化回答 | P0 |
| FR-004.2 | 回答應包含來源文件引用（document name、section） | P0 |
| FR-004.3 | 系統應支援不同回答模式（摘要、詳細、比較） | P1 |
| FR-004.4 | 系統應能識別資訊不足並明確告知使用者 | P1 |
| FR-004.5 | 系統應支援串流回應 (streaming response) | P2 |

### 2.5 管理功能

| 需求編號 | 需求描述 | 優先級 |
|----------|----------|--------|
| FR-005.1 | 系統應提供文件索引狀態查詢 | P1 |
| FR-005.2 | 系統應支援單一文件重新索引 | P1 |
| FR-005.3 | 系統應提供查詢歷史記錄 | P2 |
| FR-005.4 | 系統應支援索引內容匯出備份 | P2 |
| FR-005.5 | 系統應提供系統健康狀態檢查端點 | P1 |

---

## 3. 非功能需求

### 3.1 效能需求

| 需求編號 | 需求描述 | 指標 |
|----------|----------|------|
| NFR-001.1 | 單一文件解析時間 | < 30 秒（100 頁以內文件） |
| NFR-001.2 | 查詢回應時間 | < 5 秒（含 LLM 生成） |
| NFR-001.3 | 並行查詢支援 | >= 10 concurrent requests |
| NFR-001.4 | Embedding 處理速度 | >= 100 chunks/秒 |

### 3.2 容量需求

| 需求編號 | 需求描述 | 指標 |
|----------|----------|------|
| NFR-002.1 | 文件索引數量 | >= 1,000 份文件 |
| NFR-002.2 | 單一文件大小上限 | 50 MB |
| NFR-002.3 | 向量資料庫容量 | >= 1,000,000 chunks |
| NFR-002.4 | 元資料儲存 | >= 10 GB |

### 3.3 可用性需求

| 需求編號 | 需求描述 |
|----------|----------|
| NFR-003.1 | 系統應支援本地部署（air-gapped 環境） |
| NFR-003.2 | 系統應支援 Docker 容器化部署 |
| NFR-003.3 | 系統應提供 REST API 供整合 |
| NFR-003.4 | 系統應支援水平擴展（Stateless API Server） |
| NFR-003.5 | 系統服務可用性目標 >= 99.5% |

### 3.4 安全性需求

| 需求編號 | 需求描述 |
|----------|----------|
| NFR-004.1 | 系統應支援 API 認證機制（API Key / JWT） |
| NFR-004.2 | 敏感文件內容不應傳送至外部服務（支援本地 LLM） |
| NFR-004.3 | 系統應記錄所有查詢操作的 audit log |
| NFR-004.4 | 檔案上傳應進行類型與大小驗證 |
| NFR-004.5 | API 應實作 rate limiting |

### 3.5 維運需求

| 需求編號 | 需求描述 |
|----------|----------|
| NFR-005.1 | 系統應提供結構化日誌輸出 (JSON format) |
| NFR-005.2 | 系統應支援 Prometheus metrics 輸出 |
| NFR-005.3 | 系統應提供健康檢查端點 (/health, /ready) |
| NFR-005.4 | 設定應支援環境變數注入 |

---

## 4. 技術架構

### 4.1 架構概述

系統採用分層架構設計，包含以下層級：

1. **API Layer**: FastAPI 提供 REST API 服務
2. **Service Layer**: 業務邏輯封裝
3. **Core Layer**: RAG Pipeline 核心元件
4. **Infrastructure Layer**: 基礎設施整合

### 4.2 核心流程

#### 4.2.1 文件處理流程

```
Document Upload
      ↓
┌─────────────────┐
│  File Validation │ → 檢查格式、大小
└────────┬────────┘
         ↓
┌─────────────────┐
│     Parser      │ → Word/Excel/Markdown 解析
└────────┬────────┘
         ↓
┌─────────────────┐
│    Chunker      │ → 依文件類型選擇分塊策略
└────────┬────────┘
         ↓
┌─────────────────┐
│   Extractor     │ → 抽取 API/Table/Entity metadata
└────────┬────────┘
         ↓
┌─────────────────┐
│   Embedder      │ → 向量化
└────────┬────────┘
         ↓
┌─────────────────┐
│  Vector Store   │ → 儲存至 Qdrant
└─────────────────┘
```

#### 4.2.2 查詢流程

```
User Query
      ↓
┌─────────────────┐
│ Query Transform │ → 查詢改寫/擴展
└────────┬────────┘
         ↓
┌─────────────────┐
│  Hybrid Search  │ → Dense + Sparse 檢索
└────────┬────────┘
         ↓
┌─────────────────┐
│    Reranker     │ → 結果重排序
└────────┬────────┘
         ↓
┌─────────────────┐
│ Cross-Reference │ → 跨文件關聯擴展
└────────┬────────┘
         ↓
┌─────────────────┐
│   LLM Generate  │ → 生成回答
└────────┬────────┘
         ↓
    Response
```

---

## 5. 技術清單

### 5.1 核心元件

| 類別 | 元件 | 版本 | 用途 | 授權 |
|------|------|------|------|------|
| Framework | LlamaIndex | >= 0.10.x | RAG orchestration | MIT |
| Vector DB | Qdrant | >= 1.9.x | 向量儲存與檢索 | Apache 2.0 |
| Embedding | bge-large-zh-v1.5 | - | 中文向量化 | MIT |
| Embedding | bge-large-en-v1.5 | - | 英文向量化 | MIT |
| Reranker | bge-reranker-v2-m3 | - | 檢索結果重排序 | MIT |
| LLM (本地) | Ollama + Qwen2.5 | 14B/32B | 本地推論 | Apache 2.0 |
| LLM (雲端) | Claude API | claude-sonnet-4-20250514 | 雲端推論 | Commercial |

### 5.2 文件處理

| 類別 | 元件 | 版本 | 用途 | 授權 |
|------|------|------|------|------|
| Doc Parser | Unstructured.io | >= 0.13.x | Word/PDF 結構化解析 | Apache 2.0 |
| Word | python-docx | >= 1.1.x | Word 文件讀取 | MIT |
| Excel | openpyxl | >= 3.1.x | Excel 文件讀取 | MIT |
| Markdown | LlamaIndex MarkdownNodeParser | - | Markdown 結構化解析 | MIT |

### 5.3 基礎設施

| 類別 | 元件 | 版本 | 用途 | 授權 |
|------|------|------|------|------|
| Runtime | Python | >= 3.11 | 執行環境 | PSF |
| Container | Docker | >= 24.x | 容器化部署 | Apache 2.0 |
| Orchestration | Docker Compose | >= 2.x | 多容器管理 | Apache 2.0 |
| API Framework | FastAPI | >= 0.110.x | REST API 服務 | MIT |
| Task Queue | Celery | >= 5.3.x | 非同步文件處理 | BSD |
| Message Broker | Redis | >= 7.x | Task queue backend | BSD |

### 5.4 開發工具

| 類別 | 元件 | 用途 |
|------|------|------|
| Testing | pytest | 單元測試 |
| Testing | pytest-asyncio | 非同步測試 |
| Linting | ruff | 程式碼品質 |
| Type Check | mypy | 型別檢查 |
| Documentation | mkdocs | 文件產生 |

### 5.5 Python Dependencies

```txt
# requirements.txt

# Core RAG Framework
llama-index>=0.10.50
llama-index-vector-stores-qdrant>=0.2.0
llama-index-embeddings-huggingface>=0.2.0
llama-index-postprocessor-flag-embedding-reranker>=0.1.0
llama-index-llms-ollama>=0.1.0
llama-index-llms-anthropic>=0.1.0

# Document Processing
unstructured[docx,xlsx,md]>=0.13.0
python-docx>=1.1.0
openpyxl>=3.1.2

# Vector Database
qdrant-client>=1.9.0

# API Server
fastapi>=0.110.0
uvicorn[standard]>=0.29.0
python-multipart>=0.0.9

# Task Queue
celery>=5.3.0
redis>=5.0.0

# Utilities
pydantic>=2.7.0
pydantic-settings>=2.2.0
python-dotenv>=1.0.0
tenacity>=8.2.0
structlog>=24.1.0

# ML/Embedding
torch>=2.2.0
transformers>=4.40.0
sentence-transformers>=2.7.0

# Observability
prometheus-client>=0.20.0

# Development
pytest>=8.1.0
pytest-asyncio>=0.23.0
pytest-cov>=5.0.0
ruff>=0.4.0
mypy>=1.9.0
httpx>=0.27.0
```

---

## 6. 系統架構圖

### 6.1 整體架構

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              Client Layer                                    │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                         │
│  │   Web UI    │  │   CLI Tool  │  │  REST API   │                         │
│  │  (Optional) │  │             │  │   Client    │                         │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘                         │
└─────────┼────────────────┼────────────────┼─────────────────────────────────┘
          │                │                │
          ▼                ▼                ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              API Layer (FastAPI)                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐             │
│  │  /api/documents │  │  /api/query     │  │  /api/admin     │             │
│  │  - POST upload  │  │  - POST search  │  │  - POST reindex │             │
│  │  - GET list     │  │  - POST ask     │  │  - GET status   │             │
│  │  - DELETE {id}  │  │                 │  │  - GET health   │             │
│  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘             │
└───────────┼────────────────────┼────────────────────┼───────────────────────┘
            │                    │                    │
            ▼                    ▼                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           Service Layer                                      │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐          │
│  │ DocumentService  │  │  QueryService    │  │  IndexService    │          │
│  │ - parse()        │  │  - search()      │  │  - build()       │          │
│  │ - chunk()        │  │  - retrieve()    │  │  - update()      │          │
│  │ - extract_meta() │  │  - generate()    │  │  - delete()      │          │
│  └────────┬─────────┘  └────────┬─────────┘  └────────┬─────────┘          │
└───────────┼────────────────────┼────────────────────┼───────────────────────┘
            │                    │                    │
            ▼                    ▼                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          Core Components                                     │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                        Document Pipeline                              │  │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐     │  │
│  │  │  Parsers   │→ │  Chunkers  │→ │ Extractors │→ │  Indexer   │     │  │
│  │  │ - Word     │  │ - Markdown │  │ - API      │  │            │     │  │
│  │  │ - Excel    │  │ - Semantic │  │ - Table    │  │            │     │  │
│  │  │ - Markdown │  │ - Custom   │  │ - Entity   │  │            │     │  │
│  │  └────────────┘  └────────────┘  └────────────┘  └────────────┘     │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                        Retrieval Pipeline                             │  │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐     │  │
│  │  │  Query     │→ │  Hybrid    │→ │  Reranker  │→ │  Cross-Ref │     │  │
│  │  │ Transform  │  │  Search    │  │            │  │  Enricher  │     │  │
│  │  └────────────┘  └────────────┘  └────────────┘  └────────────┘     │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
            │                    │                    │
            ▼                    ▼                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Infrastructure Layer                                 │
│                                                                              │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐                │
│  │    Qdrant      │  │    Redis       │  │  File Storage  │                │
│  │  Vector Store  │  │  Task Queue    │  │   (Local/S3)   │                │
│  │  + Metadata    │  │  + Cache       │  │                │                │
│  └────────────────┘  └────────────────┘  └────────────────┘                │
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │                         LLM Backend                                 │    │
│  │  ┌──────────────────────┐  ┌──────────────────────┐               │    │
│  │  │   Ollama (Local)     │  │   Claude API (Cloud) │               │    │
│  │  │   - Qwen2.5          │  │   - claude-sonnet-4-20250514         │               │    │
│  │  │   - Llama3.1         │  │                      │               │    │
│  │  └──────────────────────┘  └──────────────────────┘               │    │
│  └────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 6.2 資料流程圖

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          Document Ingestion Flow                             │
└─────────────────────────────────────────────────────────────────────────────┘

  User Upload                                              Vector Store
      │                                                         ▲
      ▼                                                         │
┌───────────┐    ┌───────────┐    ┌───────────┐    ┌───────────┴───────────┐
│   File    │    │  Parser   │    │  Chunker  │    │      Embedder         │
│ Validator │ → │           │ → │           │ → │                         │
│           │    │ Word/Excel│    │ Structure │    │ bge-large-zh/en-v1.5  │
│           │    │ /Markdown │    │ Aware     │    │                       │
└───────────┘    └───────────┘    └─────┬─────┘    └───────────────────────┘
                                        │
                                        ▼
                                 ┌───────────┐
                                 │ Metadata  │
                                 │ Extractor │
                                 │           │
                                 │ - API     │
                                 │ - Table   │
                                 │ - Entity  │
                                 └───────────┘


┌─────────────────────────────────────────────────────────────────────────────┐
│                            Query Processing Flow                             │
└─────────────────────────────────────────────────────────────────────────────┘

  User Query                                               Final Response
      │                                                         ▲
      ▼                                                         │
┌───────────┐    ┌───────────┐    ┌───────────┐    ┌───────────┴───────────┐
│  Query    │    │  Hybrid   │    │ Reranker  │    │    LLM Generator      │
│ Transform │ → │  Search   │ → │           │ → │                         │
│           │    │           │    │ bge-      │    │ Claude / Qwen2.5      │
│           │    │ Dense +   │    │ reranker  │    │                       │
│           │    │ Sparse    │    │ -v2-m3    │    │                       │
└───────────┘    └─────┬─────┘    └───────────┘    └───────────────────────┘
                       │
                       ▼
                ┌───────────┐
                │  Cross-   │
                │ Reference │
                │ Enricher  │
                └───────────┘
```

---

## 7. 專案目錄結構

```
system-doc-rag/
├── docker-compose.yml              # Docker Compose 配置
├── docker-compose.override.yml     # 開發環境覆蓋配置
├── Dockerfile                      # 應用程式 Dockerfile
├── Dockerfile.dev                  # 開發環境 Dockerfile
├── requirements.txt                # Python 依賴
├── requirements-dev.txt            # 開發依賴
├── pyproject.toml                  # 專案配置
├── README.md                       # 專案說明
├── Makefile                        # 常用指令
├── .env.example                    # 環境變數範本
├── .gitignore
│
├── src/
│   ├── __init__.py
│   ├── main.py                     # FastAPI entry point
│   ├── config.py                   # 設定管理 (pydantic-settings)
│   │
│   ├── api/                        # API Layer
│   │   ├── __init__.py
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── documents.py        # 文件上傳/管理 API
│   │   │   ├── query.py            # 查詢 API
│   │   │   └── admin.py            # 管理 API
│   │   ├── schemas/                # Pydantic Request/Response Models
│   │   │   ├── __init__.py
│   │   │   ├── document.py
│   │   │   ├── query.py
│   │   │   └── response.py
│   │   ├── dependencies.py         # FastAPI Dependencies
│   │   └── middleware.py           # 中介軟體 (logging, auth)
│   │
│   ├── services/                   # Service Layer
│   │   ├── __init__.py
│   │   ├── document_service.py     # 文件處理服務
│   │   ├── query_service.py        # 查詢服務
│   │   └── index_service.py        # 索引管理服務
│   │
│   ├── core/                       # Core Components
│   │   ├── __init__.py
│   │   ├── parsers/                # 文件解析器
│   │   │   ├── __init__.py
│   │   │   ├── base.py             # Parser 抽象基類
│   │   │   ├── word_parser.py      # Word 文件解析
│   │   │   ├── excel_parser.py     # Excel 文件解析
│   │   │   └── markdown_parser.py  # Markdown 文件解析
│   │   ├── chunkers/               # 分塊策略
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── semantic_chunker.py
│   │   │   └── structure_chunker.py
│   │   ├── extractors/             # Metadata 抽取
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── api_extractor.py    # API endpoint 抽取
│   │   │   ├── table_extractor.py  # Table schema 抽取
│   │   │   └── entity_extractor.py # Entity name 抽取
│   │   ├── retrievers/             # 檢索器
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── hybrid_retriever.py
│   │   │   └── cross_ref_retriever.py
│   │   └── generators/             # 回答生成
│   │       ├── __init__.py
│   │       ├── base.py
│   │       └── response_generator.py
│   │
│   ├── infrastructure/             # Infrastructure Layer
│   │   ├── __init__.py
│   │   ├── vector_store.py         # Qdrant 封裝
│   │   ├── llm_client.py           # LLM 抽象層 (Ollama/Claude)
│   │   ├── embedding.py            # Embedding 服務
│   │   ├── storage.py              # 檔案儲存 (Local/S3)
│   │   └── cache.py                # Redis 快取
│   │
│   ├── tasks/                      # Celery Async Tasks
│   │   ├── __init__.py
│   │   ├── celery_app.py           # Celery 配置
│   │   └── document_tasks.py       # 非同步文件處理任務
│   │
│   └── utils/                      # 工具函式
│       ├── __init__.py
│       ├── logging.py              # 結構化日誌
│       └── helpers.py              # 通用工具
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py                 # Pytest fixtures
│   ├── unit/                       # 單元測試
│   │   ├── __init__.py
│   │   ├── test_parsers.py
│   │   ├── test_chunkers.py
│   │   ├── test_extractors.py
│   │   └── test_services.py
│   ├── integration/                # 整合測試
│   │   ├── __init__.py
│   │   ├── test_document_flow.py
│   │   ├── test_query_flow.py
│   │   └── test_api.py
│   └── fixtures/                   # 測試資料
│       ├── sample_api_spec.md
│       ├── sample_schema.xlsx
│       └── sample_design.docx
│
├── scripts/
│   ├── setup_models.sh             # 下載 embedding/reranker 模型
│   ├── init_qdrant.py              # 初始化向量庫 collection
│   ├── seed_data.py                # 測試資料匯入
│   └── healthcheck.py              # 健康檢查腳本
│
├── docs/
│   ├── index.md                    # 文件首頁
│   ├── api.md                      # API 文件
│   ├── deployment.md               # 部署指南
│   ├── development.md              # 開發指南
│   └── architecture.md             # 架構說明
│
└── configs/
    ├── logging.yaml                # 日誌配置
    └── qdrant_schema.json          # Qdrant collection schema
```

---

## 8. API 規格

### 8.1 Documents API

#### POST /api/documents/upload

上傳文件並建立索引。

**Request:**
```http
POST /api/documents/upload
Content-Type: multipart/form-data

file: <binary>
doc_type: api_spec | table_schema | system_design | general (optional)
tags: ["tag1", "tag2"] (optional)
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "document_id": "doc_abc123",
    "filename": "api_spec.md",
    "doc_type": "api_spec",
    "chunks_count": 42,
    "metadata": {
      "api_endpoints": ["GET /users", "POST /users"],
      "table_names": [],
      "entity_names": ["User", "Account"]
    },
    "created_at": "2024-12-01T10:00:00Z"
  }
}
```

#### GET /api/documents

列出所有已索引文件。

**Request:**
```http
GET /api/documents?page=1&size=20&doc_type=api_spec
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "items": [
      {
        "document_id": "doc_abc123",
        "filename": "api_spec.md",
        "doc_type": "api_spec",
        "chunks_count": 42,
        "created_at": "2024-12-01T10:00:00Z",
        "updated_at": "2024-12-01T10:00:00Z"
      }
    ],
    "total": 100,
    "page": 1,
    "size": 20
  }
}
```

#### DELETE /api/documents/{document_id}

刪除文件及其索引。

**Response:**
```json
{
  "status": "success",
  "message": "Document deleted successfully"
}
```

### 8.2 Query API

#### POST /api/query/search

語意搜尋文件內容。

**Request:**
```json
{
  "query": "使用者註冊 API 的請求格式",
  "filters": {
    "doc_types": ["api_spec"],
    "tags": ["user-service"]
  },
  "top_k": 5,
  "include_cross_reference": true
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "results": [
      {
        "chunk_id": "chunk_xyz789",
        "document_id": "doc_abc123",
        "content": "## POST /api/users\n\n註冊新使用者...",
        "score": 0.92,
        "metadata": {
          "section": "User Registration",
          "api_endpoint": "POST /api/users",
          "doc_type": "api_spec"
        },
        "cross_references": [
          {
            "chunk_id": "chunk_table_001",
            "document_id": "doc_schema_001",
            "type": "table_schema",
            "table_name": "users",
            "relevance": "high"
          }
        ]
      }
    ],
    "query_time_ms": 150
  }
}
```

#### POST /api/query/ask

問答式查詢，返回 LLM 生成的回答。

**Request:**
```json
{
  "question": "使用者註冊 API 需要哪些欄位？對應的資料庫表格結構是什麼？",
  "response_mode": "detailed",
  "include_sources": true
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "answer": "根據 API 規格文件，使用者註冊 API (POST /api/users) 需要以下欄位：\n\n1. **必填欄位**:\n   - email (string): 使用者電子郵件\n   - password (string): 密碼，至少 8 字元\n   - name (string): 使用者名稱\n\n2. **選填欄位**:\n   - phone (string): 電話號碼\n   - avatar_url (string): 頭像網址\n\n對應的資料庫表格 `users` 結構如下：\n\n| Column | Type | Nullable | Description |\n|--------|------|----------|-------------|\n| id | BIGINT | NO | 主鍵 |\n| email | VARCHAR(255) | NO | 電子郵件 |\n| password_hash | VARCHAR(255) | NO | 密碼雜湊 |\n| name | VARCHAR(100) | NO | 使用者名稱 |\n| phone | VARCHAR(20) | YES | 電話 |\n| avatar_url | TEXT | YES | 頭像網址 |\n| created_at | TIMESTAMP | NO | 建立時間 |",
    "sources": [
      {
        "document_id": "doc_abc123",
        "filename": "user_api_spec.md",
        "section": "POST /api/users"
      },
      {
        "document_id": "doc_schema_001",
        "filename": "database_schema.xlsx",
        "section": "users table"
      }
    ],
    "confidence": 0.95,
    "generation_time_ms": 2500
  }
}
```

### 8.3 Admin API

#### GET /api/admin/health

健康檢查。

**Response:**
```json
{
  "status": "healthy",
  "components": {
    "api": "healthy",
    "vector_store": "healthy",
    "llm": "healthy",
    "redis": "healthy"
  },
  "timestamp": "2024-12-01T10:00:00Z"
}
```

#### POST /api/admin/reindex/{document_id}

重新索引指定文件。

**Response:**
```json
{
  "status": "success",
  "data": {
    "task_id": "task_abc123",
    "document_id": "doc_abc123",
    "status": "processing"
  }
}
```

#### GET /api/admin/stats

系統統計資訊。

**Response:**
```json
{
  "status": "success",
  "data": {
    "total_documents": 150,
    "total_chunks": 12500,
    "documents_by_type": {
      "api_spec": 45,
      "table_schema": 30,
      "system_design": 75
    },
    "storage_used_mb": 256,
    "last_indexed_at": "2024-12-01T10:00:00Z"
  }
}
```

---

## 9. 資料模型

### 9.1 Document Model

```python
class Document(BaseModel):
    document_id: str
    filename: str
    file_path: str
    doc_type: DocType  # api_spec, table_schema, system_design, general
    file_size: int
    chunks_count: int
    metadata: DocumentMetadata
    tags: list[str]
    status: IndexStatus  # pending, processing, indexed, failed
    created_at: datetime
    updated_at: datetime
    indexed_at: datetime | None
```

### 9.2 Chunk Model

```python
class Chunk(BaseModel):
    chunk_id: str
    document_id: str
    content: str
    content_type: str  # text, table, code_block
    section_hierarchy: list[str]  # ["Chapter 1", "1.1 Overview"]
    metadata: ChunkMetadata
    embedding: list[float] | None
    created_at: datetime
```

### 9.3 ChunkMetadata Model

```python
class ChunkMetadata(BaseModel):
    doc_type: DocType
    section: str | None
    page_number: int | None
    
    # API specific
    api_endpoints: list[str] | None
    http_methods: list[str] | None
    
    # Table specific
    table_names: list[str] | None
    column_names: list[str] | None
    
    # Entity specific
    entity_names: list[str] | None
    
    # Code specific
    code_language: str | None
```

### 9.4 Query Model

```python
class QueryRequest(BaseModel):
    query: str
    filters: QueryFilters | None
    top_k: int = 5
    include_cross_reference: bool = True
    response_mode: ResponseMode = "concise"  # concise, detailed, comparison

class QueryFilters(BaseModel):
    doc_types: list[DocType] | None
    tags: list[str] | None
    date_from: datetime | None
    date_to: datetime | None
```

### 9.5 Qdrant Collection Schema

```json
{
  "collection_name": "system_docs",
  "vectors": {
    "size": 1024,
    "distance": "Cosine"
  },
  "sparse_vectors": {
    "text": {
      "index": {
        "on_disk": false
      }
    }
  },
  "payload_schema": {
    "document_id": "keyword",
    "chunk_id": "keyword",
    "doc_type": "keyword",
    "section": "text",
    "api_endpoints": "keyword[]",
    "table_names": "keyword[]",
    "entity_names": "keyword[]",
    "tags": "keyword[]",
    "created_at": "datetime"
  }
}
```

---

## 10. 部署配置

### 10.1 Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  api:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=production
      - QDRANT_HOST=qdrant
      - QDRANT_PORT=6333
      - REDIS_URL=redis://redis:6379/0
      - LLM_PROVIDER=${LLM_PROVIDER:-ollama}
      - OLLAMA_HOST=ollama
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY:-}
    volumes:
      - ./data/uploads:/app/uploads
      - ./data/models:/app/models
    depends_on:
      - qdrant
      - redis
    restart: unless-stopped

  worker:
    build:
      context: .
      dockerfile: Dockerfile
    command: celery -A src.tasks.celery_app worker --loglevel=info
    environment:
      - ENVIRONMENT=production
      - QDRANT_HOST=qdrant
      - REDIS_URL=redis://redis:6379/0
    volumes:
      - ./data/uploads:/app/uploads
      - ./data/models:/app/models
    depends_on:
      - qdrant
      - redis
    restart: unless-stopped

  qdrant:
    image: qdrant/qdrant:v1.9.0
    ports:
      - "6333:6333"
      - "6334:6334"
    volumes:
      - ./data/qdrant:/qdrant/storage
    environment:
      - QDRANT__SERVICE__GRPC_PORT=6334
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - ./data/redis:/data
    command: redis-server --appendonly yes
    restart: unless-stopped

  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ./data/ollama:/root/.ollama
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]
    restart: unless-stopped

volumes:
  qdrant_data:
  redis_data:
  ollama_models:
```

### 10.2 Environment Variables

```bash
# .env.example

# Application
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO
API_HOST=0.0.0.0
API_PORT=8000

# Vector Store
QDRANT_HOST=localhost
QDRANT_PORT=6333
QDRANT_COLLECTION=system_docs

# Redis
REDIS_URL=redis://localhost:6379/0

# LLM Configuration
LLM_PROVIDER=ollama  # ollama | anthropic
OLLAMA_HOST=localhost
OLLAMA_PORT=11434
OLLAMA_MODEL=qwen2.5:14b
ANTHROPIC_API_KEY=your-api-key-here
ANTHROPIC_MODEL=claude-sonnet-4-20250514

# Embedding
EMBEDDING_MODEL=BAAI/bge-large-zh-v1.5
RERANKER_MODEL=BAAI/bge-reranker-v2-m3

# Storage
UPLOAD_DIR=./data/uploads
MAX_FILE_SIZE_MB=50

# Security
API_KEY_ENABLED=false
API_KEY=your-api-key-here
```

### 10.3 Dockerfile

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY scripts/ ./scripts/
COPY configs/ ./configs/

# Create necessary directories
RUN mkdir -p /app/uploads /app/models /app/logs

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python scripts/healthcheck.py || exit 1

# Run the application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 11. 開發階段規劃

### 11.1 Phase 概覽

| Phase | 名稱 | 預估工時 | 產出 |
|-------|------|----------|------|
| Phase 1 | 基礎架構建置 | 3-5 天 | Docker 環境、FastAPI skeleton、Qdrant 設定 |
| Phase 2 | 文件解析模組 | 5-7 天 | Word/Excel/Markdown parser、metadata extractor |
| Phase 3 | 索引建置 | 3-5 天 | Chunking 策略、Embedding pipeline、向量索引 |
| Phase 4 | 檢索功能 | 5-7 天 | Hybrid search、Reranker、Cross-reference |
| Phase 5 | 回答生成 | 3-5 天 | LLM 整合、Response formatting、Citation |
| Phase 6 | API 完善 | 3-5 天 | 完整 REST API、錯誤處理、驗證 |
| Phase 7 | 測試與優化 | 5-7 天 | 單元測試、整合測試、效能調校 |

**總預估：27-41 個工作天（單人開發）**

### 11.2 詳細任務分解

#### Phase 1: 基礎架構建置 (3-5 天)

| Task | 說明 | 預估 |
|------|------|------|
| 1.1 | 建立專案結構、設定 pyproject.toml | 0.5 天 |
| 1.2 | Docker Compose 環境配置 (Qdrant, Redis, Ollama) | 1 天 |
| 1.3 | FastAPI 基礎架構、路由設定 | 1 天 |
| 1.4 | 設定管理 (pydantic-settings)、日誌配置 | 0.5 天 |
| 1.5 | Qdrant collection 初始化腳本 | 0.5 天 |
| 1.6 | 基礎 CI/CD 設定 (lint, test) | 0.5 天 |

#### Phase 2: 文件解析模組 (5-7 天)

| Task | 說明 | 預估 |
|------|------|------|
| 2.1 | Parser 抽象基類設計 | 0.5 天 |
| 2.2 | Markdown Parser 實作 (保留結構) | 1 天 |
| 2.3 | Word Parser 實作 (Unstructured.io) | 1.5 天 |
| 2.4 | Excel Parser 實作 (Table Schema 識別) | 1.5 天 |
| 2.5 | API Endpoint Extractor | 1 天 |
| 2.6 | Table Schema Extractor | 1 天 |
| 2.7 | Entity Name Extractor | 0.5 天 |

#### Phase 3: 索引建置 (3-5 天)

| Task | 說明 | 預估 |
|------|------|------|
| 3.1 | Chunking 策略實作 (Structure-aware) | 1.5 天 |
| 3.2 | Embedding 服務封裝 (bge-large) | 1 天 |
| 3.3 | Qdrant Vector Store 整合 | 1 天 |
| 3.4 | Metadata indexing 與 filtering | 1 天 |

#### Phase 4: 檢索功能 (5-7 天)

| Task | 說明 | 預估 |
|------|------|------|
| 4.1 | Hybrid Search 實作 (Dense + Sparse) | 2 天 |
| 4.2 | Reranker 整合 (bge-reranker-v2-m3) | 1 天 |
| 4.3 | Cross-Reference Retriever 實作 | 2 天 |
| 4.4 | Query Transform / Expansion | 1 天 |

#### Phase 5: 回答生成 (3-5 天)

| Task | 說明 | 預估 |
|------|------|------|
| 5.1 | LLM Client 抽象層 (Ollama/Claude) | 1 天 |
| 5.2 | Response Generator 實作 | 1.5 天 |
| 5.3 | Source Citation 格式化 | 0.5 天 |
| 5.4 | Streaming Response 支援 | 1 天 |

#### Phase 6: API 完善 (3-5 天)

| Task | 說明 | 預估 |
|------|------|------|
| 6.1 | Document Upload API (含驗證) | 1 天 |
| 6.2 | Query API (search, ask) | 1 天 |
| 6.3 | Admin API (health, stats, reindex) | 1 天 |
| 6.4 | 錯誤處理、API 文件 (OpenAPI) | 1 天 |
| 6.5 | Rate Limiting、認證 (Optional) | 1 天 |

#### Phase 7: 測試與優化 (5-7 天)

| Task | 說明 | 預估 |
|------|------|------|
| 7.1 | 單元測試 (Parsers, Extractors, Chunkers) | 2 天 |
| 7.2 | 整合測試 (Document flow, Query flow) | 2 天 |
| 7.3 | 效能測試與調校 | 1.5 天 |
| 7.4 | 文件撰寫 (部署、使用指南) | 1 天 |

### 11.3 里程碑

| 里程碑 | 完成條件 | 目標時間 |
|--------|----------|----------|
| M1 | Docker 環境可啟動、API skeleton 可存取 | Week 1 |
| M2 | 可上傳並解析 Markdown 文件 | Week 2 |
| M3 | 可上傳並解析 Word/Excel 文件 | Week 3 |
| M4 | 基本語意搜尋可運作 | Week 4 |
| M5 | Cross-reference 檢索可運作 | Week 5 |
| M6 | LLM 問答功能可運作 | Week 6 |
| M7 | 完整 API、測試覆蓋率 > 80% | Week 7-8 |

---

## 12. 附錄

### 12.1 參考資源

| 資源 | 連結 |
|------|------|
| LlamaIndex Documentation | https://docs.llamaindex.ai/ |
| Qdrant Documentation | https://qdrant.tech/documentation/ |
| Unstructured.io | https://unstructured.io/docs |
| BGE Embedding Models | https://huggingface.co/BAAI/bge-large-zh-v1.5 |
| BGE Reranker | https://huggingface.co/BAAI/bge-reranker-v2-m3 |
| FastAPI | https://fastapi.tiangolo.com/ |
| Ollama | https://ollama.ai/ |

### 12.2 名詞定義

| 名詞 | 定義 |
|------|------|
| RAG | Retrieval-Augmented Generation，檢索增強生成 |
| Chunk | 文件分割後的最小索引單位 |
| Embedding | 將文字轉換為向量表示 |
| Hybrid Search | 結合語意搜尋與關鍵字搜尋的混合檢索方式 |
| Reranker | 對初步檢索結果進行重新排序的模型 |
| Cross-Reference | 跨文件的關聯查詢，如 API 對應 Table Schema |

### 12.3 版本歷史

| 版本 | 日期 | 變更說明 |
|------|------|----------|
| 1.0 | 2024-12 | 初版 |

---

**文件結束**
