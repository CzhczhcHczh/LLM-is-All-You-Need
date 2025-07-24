"""
ChromaDB 管理 API - 展示和管理向量数据库中的内容
"""

from fastapi import APIRouter, Query, HTTPException, Depends
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from loguru import logger
import json

from services import chromadb_service
from database import SessionLocal, get_db

# 创建路由
admin_router = APIRouter(prefix="/admin", tags=["管理接口"])

# 数据模型
class JobEmbedding(BaseModel):
    id: str
    document: str
    metadata: Dict[str, Any]
    distance: Optional[float] = None

class QueryResult(BaseModel):
    total: int
    results: List[JobEmbedding]

@admin_router.get("/chroma/jobs", response_model=QueryResult)
async def list_job_embeddings(
    query: Optional[str] = None,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """
    获取 ChromaDB 中的职位嵌入向量数据
    
    - 可选的搜索查询
    - 分页支持
    """
    try:
        if query:
            # 如果有查询，进行语义搜索
            results = chromadb_service.search_similar_jobs(query, limit)
            
            embeddings = []
            for result in results:
                embeddings.append(JobEmbedding(
                    id=result["id"],
                    document=result["document"],
                    metadata=result["metadata"],
                    distance=result["distance"]
                ))
            
            return QueryResult(
                total=len(embeddings),
                results=embeddings
            )
        else:
            # 没有查询，获取所有数据
            # 注意：ChromaDB 本身不支持分页，这里我们获取所有数据后手动分页
            all_results = chromadb_service.get_all_job_embeddings()
            
            # 手动分页
            paginated_results = all_results[offset:offset+limit]
            
            embeddings = []
            for result in paginated_results:
                embeddings.append(JobEmbedding(
                    id=result["id"],
                    document=result["document"],
                    metadata=result["metadata"]
                ))
            
            return QueryResult(
                total=len(all_results),
                results=embeddings
            )
    except Exception as e:
        logger.error(f"Error fetching ChromaDB data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching data: {str(e)}")

@admin_router.get("/chroma/jobs/{job_id}")
async def get_job_embedding(job_id: str):
    """获取单个职位嵌入向量数据的详细信息"""
    try:
        result = chromadb_service.get_job_embedding(job_id)
        if not result:
            raise HTTPException(status_code=404, detail=f"Job embedding {job_id} not found")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching job embedding {job_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching job embedding: {str(e)}")

@admin_router.delete("/chroma/jobs/{job_id}")
async def delete_job_embedding(job_id: str):
    """删除单个职位嵌入向量数据"""
    try:
        result = chromadb_service.delete_job_embedding(job_id)
        return {"success": True, "message": f"Job embedding {job_id} deleted"}
    except Exception as e:
        logger.error(f"Error deleting job embedding {job_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error deleting job embedding: {str(e)}")

@admin_router.get("/chroma/stats")
async def get_chroma_stats():
    """获取 ChromaDB 数据库统计信息"""
    try:
        stats = chromadb_service.get_stats()
        return stats
    except Exception as e:
        logger.error(f"Error getting ChromaDB stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting stats: {str(e)}")
