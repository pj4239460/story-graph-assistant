# Known Issues / 已知问题

## ~~ChromaDB Stability Issues on Windows~~ ✅ RESOLVED

### Problem
~~ChromaDB 1.4.0 causes application crashes on Windows when attempting to index data into the vector database. The crash occurs at the native library level without Python exceptions.~~

### Resolution (December 2025)
**MIGRATED TO FAISS** - The application now uses FAISS (Facebook AI Similarity Search) instead of ChromaDB:
- ✅ **Stable on Windows** - No DLL errors or crashes
- ✅ **CPU-only** - No PyTorch dependencies, lighter installation
- ✅ **Simple architecture** - Direct file-based storage without client/server complexity
- ✅ **Same API** - Seamless replacement with identical search capabilities

### Technical Details
- **Vector DB**: FAISS with IndexFlatL2 (exact L2 distance search)
- **Embeddings**: sentence-transformers paraphrase-multilingual-MiniLM-L12-v2
- **Storage**: `.vectordb/` directory with `.index` (FAISS binary) and `.meta.json` (metadata) files
- **Dimensions**: 384-dimensional vectors

### Previous Symptoms (ChromaDB 1.4.0)
- Application terminated immediately when loading a project
- Last log message: "Upserting to ChromaDB..."
- No Python traceback or error message

### Related Files
- `src/infra/vector_db.py` - Rewritten for FAISS (376 lines)
- `src/services/search_service.py` - Automatic fallback to keyword search maintained
- `src/services/vector_index_service.py` - Index management with detailed logging
- `requirements.txt` - Updated: faiss-cpu, sentence-transformers (ChromaDB removed)

---

## ~~ChromaDB 在 Windows 上的稳定性问题~~ ✅ 已解决

### 问题描述
~~ChromaDB 1.4.0 在 Windows 上尝试向向量数据库索引数据时会导致应用崩溃。崩溃发生在原生库层面，没有 Python 异常。~~

### 解决方案（2025年12月）
**已迁移到 FAISS** - 应用现在使用 FAISS（Facebook AI 相似度搜索）替代 ChromaDB：
- ✅ **Windows 稳定** - 无 DLL 错误或崩溃
- ✅ **仅 CPU** - 无 PyTorch 依赖，安装更轻量
- ✅ **架构简单** - 直接基于文件存储，无客户端/服务器复杂性
- ✅ **相同 API** - 无缝替换，搜索能力相同

### 技术细节
- **向量数据库**: FAISS IndexFlatL2（精确 L2 距离搜索）
- **嵌入模型**: sentence-transformers paraphrase-multilingual-MiniLM-L12-v2
- **存储位置**: `.vectordb/` 目录，包含 `.index`（FAISS 二进制）和 `.meta.json`（元数据）文件
- **向量维度**: 384 维

### 之前的症状（ChromaDB 1.4.0）
- 加载项目时应用立即终止
- 最后的日志消息："Upserting to ChromaDB..."
- 没有 Python traceback 或错误消息

### 影响范围
- ❌ 基于向量的语义搜索已禁用
- ✅ 关键词搜索作为降级方案正常工作
- ✅ 所有其他功能正常运行

### 临时解决方案
向量索引功能已在以下文件中临时禁用：
- `src/ui/sidebar.py` - 自动索引已注释

应用会自动降级到关键词搜索，提供：
- 名称/别名匹配
- 标签过滤
- 特质和描述匹配
- 智能相关性评分

### 可能的解决方案
1. **等待 ChromaDB 修复** - 关注 ChromaDB 新版本的 Windows 稳定性改进
2. **切换到 FAISS** - 使用 FAISS 作为替代向量数据库
3. **使用 ChromaDB 0.3.x** - 需要安装 Visual C++ Build Tools
4. **Linux/macOS** - ChromaDB 在 Unix 系统上运行稳定

### 相关文件
- `src/infra/vector_db.py` - 向量数据库包装器，具有优雅降级
- `src/services/search_service.py` - 自动降级到关键词搜索
- `src/services/vector_index_service.py` - 索引服务（当前未使用）
- `requirements.txt` - ChromaDB 标记为可选依赖

---

## Other Issues

None currently reported.

## 其他问题

目前无其他已知问题。
