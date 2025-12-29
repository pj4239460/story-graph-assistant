# Known Issues / 已知问题

## ChromaDB Stability Issues on Windows

### Problem
ChromaDB 1.4.0 causes application crashes on Windows when attempting to index data into the vector database. The crash occurs at the native library level without Python exceptions.

### Symptoms
- Application terminates immediately when loading a project
- Last log message: "Upserting to ChromaDB..."
- No Python traceback or error message

### Impact
- ❌ Vector-based semantic search is disabled
- ✅ Keyword-based search works as fallback
- ✅ All other features function normally

### Workaround
Vector indexing has been temporarily disabled in:
- `src/ui/sidebar.py` - Auto-indexing commented out

The application automatically falls back to keyword-based search, which provides:
- Name/alias matching
- Tag-based filtering  
- Trait and description matching
- Intelligent relevance scoring

### Possible Solutions
1. **Wait for ChromaDB fix** - Monitor ChromaDB releases for Windows stability improvements
2. **Switch to FAISS** - Implement FAISS as alternative vector database
3. **Use ChromaDB 0.3.x** - Requires Visual C++ Build Tools installation
4. **Linux/macOS** - ChromaDB works reliably on Unix-based systems

### Related Files
- `src/infra/vector_db.py` - Vector database wrapper with graceful degradation
- `src/services/search_service.py` - Automatic fallback to keyword search
- `src/services/vector_index_service.py` - Indexing service (currently unused)
- `requirements.txt` - ChromaDB marked as optional

---

## ChromaDB 在 Windows 上的稳定性问题

### 问题描述
ChromaDB 1.4.0 在 Windows 上尝试向向量数据库索引数据时会导致应用崩溃。崩溃发生在原生库层面，没有 Python 异常。

### 症状
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
