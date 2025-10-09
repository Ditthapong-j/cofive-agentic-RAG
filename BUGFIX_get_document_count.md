# Bug Fix: get_document_count() Error

## 🐛 Problem

เกิด error เมื่อ query โดยไม่ใส่ filter:

```
Error processing query: create_rag_tools.<locals>.get_document_count() takes 0 positional arguments but 1 was given
```

## 🔍 Root Cause

ปัญหาอยู่ที่ไฟล์ `src/tools.py`:

### เดิม (มีปัญหา):
```python
def get_document_count() -> str:
    """Get the number of documents in the knowledge base."""
    try:
        count = vector_store_manager.get_document_count()
        return f"The knowledge base contains {count} documents."
    except Exception as e:
        return f"Error getting document count: {str(e)}"
```

**ปัญหา**: 
- ฟังก์ชัน `get_document_count()` ไม่รับ parameter ใดๆ
- แต่ LangChain Tool framework อาจส่ง argument มาให้ (เช่น query string)
- เมื่อ LangChain พยายามเรียกใช้ด้วย argument จึงเกิด error

## ✅ Solution

### ใหม่ (แก้ไขแล้ว):
```python
def get_document_count(query: str = "") -> str:
    """Get the number of documents in the knowledge base."""
    try:
        count = vector_store_manager.get_document_count()
        return f"The knowledge base contains {count} documents."
    except Exception as e:
        return f"Error getting document count: {str(e)}"
```

**การแก้ไข**:
- เพิ่ม parameter `query: str = ""` 
- ทำให้ฟังก์ชันรับ argument ได้แต่ไม่จำเป็นต้องใช้
- Compatible กับ LangChain Tool framework

## 📝 Why This Works

LangChain Tool framework มีพฤติกรรมดังนี้:
1. เมื่อ Agent เรียกใช้ tool อาจส่ง query/input เป็น argument
2. แม้ว่า tool บางตัวไม่ต้องการ input (เช่น `get_document_count`)
3. Framework อาจยังส่ง argument มาอยู่ดี
4. ดังนั้น tool ทุกตัวควรรับ parameter ได้แม้จะไม่ได้ใช้

## 🔧 Files Changed

### src/tools.py
- แก้ไข `get_document_count()` function signature
- เพิ่ม optional parameter `query: str = ""`

## ✅ Testing

### Test Case 1: Query without filters
```bash
curl -X POST "http://localhost:8003/query" \
     -H "Content-Type: application/json" \
     -d '{
       "query": "What documents do we have?",
       "model": "gpt-4o-mini"
     }'
```

**Before**: ❌ Error
**After**: ✅ Works correctly

### Test Case 2: Query with filters
```bash
curl -X POST "http://localhost:8003/query" \
     -H "Content-Type: application/json" \
     -d '{
       "query": "What are the findings?",
       "tags": ["research"]
     }'
```

**Before**: ✅ Works (no change)
**After**: ✅ Still works

### Test Case 3: Document count tool
```python
# When agent calls get_document_count tool
agent.tools.get_document_count()  # ✅ Works
agent.tools.get_document_count("") # ✅ Works
agent.tools.get_document_count("some query") # ✅ Works (parameter ignored)
```

## 🎯 Impact

- ✅ แก้ไข error เมื่อ query โดยไม่มี filter
- ✅ ไม่กระทบกับ functionality อื่นๆ
- ✅ Backward compatible
- ✅ ทำให้ระบบ robust มากขึ้น

## 💡 Best Practice Learned

**สำหรับ LangChain Tools:**
- Tool functions ควรรับ parameter เสมอ (แม้จะไม่ได้ใช้)
- ใช้ default value `= ""` สำหรับ optional parameters
- ทำให้ tool compatible กับ framework behavior

**Pattern:**
```python
def tool_function(query: str = "") -> str:
    # Tool logic here
    # query parameter may or may not be used
    pass
```

## 🚀 Status

✅ **Fixed and Tested**
- Error resolved
- System working normally
- No side effects

---

**Fix applied**: October 9, 2025
**File**: `src/tools.py`
**Function**: `get_document_count()`
