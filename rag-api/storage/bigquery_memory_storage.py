"""
BigQuery-based Memory Storage

Production-ready storage implementation using Google Cloud BigQuery.
"""

from typing import List, Optional
from datetime import datetime
import os
import json

try:
    from google.cloud import bigquery
    from google.cloud.exceptions import NotFound
    BIGQUERY_AVAILABLE = True
except ImportError:
    BIGQUERY_AVAILABLE = False
    bigquery = None

from ..models import MemoryItem, MemoryType
from ..memory_storage import MemoryStorage


class BigQueryMemoryStorage(MemoryStorage):
    """
    BigQuery-based memory storage.
    
    Requires:
    - google-cloud-bigquery package
    - GOOGLE_APPLICATION_CREDENTIALS environment variable (or default credentials)
    - BigQuery dataset and table
    """
    
    def __init__(
        self,
        project_id: Optional[str] = None,
        dataset_id: str = "jarvis",
        table_id: str = "memories"
    ):
        """
        Initialize BigQuery storage.
        
        Args:
            project_id: GCP project ID (defaults to env var or default credentials)
            dataset_id: BigQuery dataset ID
            table_id: BigQuery table ID
        """
        if not BIGQUERY_AVAILABLE:
            raise ImportError(
                "google-cloud-bigquery is required. Install with: pip install google-cloud-bigquery"
            )
        
        self.project_id = project_id or os.getenv("GOOGLE_CLOUD_PROJECT")
        self.dataset_id = dataset_id
        self.table_id = table_id
        
        # Initialize BigQuery client
        if self.project_id:
            self.client = bigquery.Client(project=self.project_id)
        else:
            self.client = bigquery.Client()  # Uses default credentials
        
        self.dataset_ref = self.client.dataset(dataset_id)
        self.table_ref = self.dataset_ref.table(table_id)
        
        # Create dataset and table if they don't exist
        self._ensure_dataset_and_table()
    
    def _ensure_dataset_and_table(self):
        """Create dataset and table if they don't exist."""
        try:
            self.client.get_dataset(self.dataset_ref)
        except NotFound:
            # Create dataset
            dataset = bigquery.Dataset(self.dataset_ref)
            dataset.location = "US"
            self.client.create_dataset(dataset, exists_ok=True)
        
        try:
            self.client.get_table(self.table_ref)
        except NotFound:
            # Create table with schema
            schema = [
                bigquery.SchemaField("id", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("user_id", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("content", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("memory_type", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("project_id", "STRING", mode="NULLABLE"),
                bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED"),
                bigquery.SchemaField("updated_at", "TIMESTAMP", mode="REQUIRED"),
                bigquery.SchemaField("metadata", "JSON", mode="NULLABLE"),
            ]
            table = bigquery.Table(self.table_ref, schema=schema)
            self.client.create_table(table)
    
    def create(self, memory: MemoryItem) -> MemoryItem:
        """Create a new memory in BigQuery."""
        row = {
            "id": memory.id,
            "user_id": memory.user_id,
            "content": memory.content,
            "memory_type": memory.memory_type.value,
            "project_id": memory.project_id,
            "created_at": memory.created_at.isoformat(),
            "updated_at": memory.updated_at.isoformat(),
            "metadata": json.dumps(memory.metadata or {})
        }
        
        errors = self.client.insert_rows_json(self.table_ref, [row])
        if errors:
            raise Exception(f"Failed to insert memory: {errors}")
        
        return memory
    
    def get(self, memory_id: str, user_id: str) -> Optional[MemoryItem]:
        """Get a memory by ID."""
        query = f"""
        SELECT *
        FROM `{self.project_id}.{self.dataset_id}.{self.table_id}`
        WHERE id = @memory_id AND user_id = @user_id
        LIMIT 1
        """
        
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("memory_id", "STRING", memory_id),
                bigquery.ScalarQueryParameter("user_id", "STRING", user_id),
            ]
        )
        
        query_job = self.client.query(query, job_config=job_config)
        results = list(query_job)
        
        if not results:
            return None
        
        return self._row_to_memory(results[0])
    
    def list(
        self,
        user_id: str,
        project_id: Optional[str] = None,
        memory_type: Optional[MemoryType] = None,
        limit: int = 100
    ) -> List[MemoryItem]:
        """List memories for a user."""
        query = f"""
        SELECT *
        FROM `{self.project_id}.{self.dataset_id}.{self.table_id}`
        WHERE user_id = @user_id
        """
        
        params = [bigquery.ScalarQueryParameter("user_id", "STRING", user_id)]
        
        if project_id:
            query += " AND project_id = @project_id"
            params.append(bigquery.ScalarQueryParameter("project_id", "STRING", project_id))
        
        if memory_type:
            query += " AND memory_type = @memory_type"
            params.append(bigquery.ScalarQueryParameter("memory_type", "STRING", memory_type.value))
        
        query += f" ORDER BY created_at DESC LIMIT {limit}"
        
        job_config = bigquery.QueryJobConfig(query_parameters=params)
        query_job = self.client.query(query, job_config=job_config)
        results = list(query_job)
        
        return [self._row_to_memory(row) for row in results]
    
    def update(self, memory: MemoryItem) -> MemoryItem:
        """Update a memory."""
        query = f"""
        UPDATE `{self.project_id}.{self.dataset_id}.{self.table_id}`
        SET content = @content,
            memory_type = @memory_type,
            project_id = @project_id,
            updated_at = @updated_at,
            metadata = @metadata
        WHERE id = @id AND user_id = @user_id
        """
        
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("id", "STRING", memory.id),
                bigquery.ScalarQueryParameter("user_id", "STRING", memory.user_id),
                bigquery.ScalarQueryParameter("content", "STRING", memory.content),
                bigquery.ScalarQueryParameter("memory_type", "STRING", memory.memory_type.value),
                bigquery.ScalarQueryParameter("project_id", "STRING", memory.project_id),
                bigquery.ScalarQueryParameter("updated_at", "TIMESTAMP", memory.updated_at),
                bigquery.ScalarQueryParameter("metadata", "JSON", json.dumps(memory.metadata or {})),
            ]
        )
        
        query_job = self.client.query(query, job_config=job_config)
        query_job.result()  # Wait for completion
        
        return memory
    
    def delete(self, memory_id: str, user_id: str) -> bool:
        """Delete a memory."""
        query = f"""
        DELETE FROM `{self.project_id}.{self.dataset_id}.{self.table_id}`
        WHERE id = @id AND user_id = @user_id
        """
        
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("id", "STRING", memory_id),
                bigquery.ScalarQueryParameter("user_id", "STRING", user_id),
            ]
        )
        
        query_job = self.client.query(query, job_config=job_config)
        query_job.result()  # Wait for completion
        
        return query_job.num_dml_affected_rows > 0
    
    def search(
        self,
        user_id: str,
        query: str,
        project_id: Optional[str] = None,
        limit: int = 10
    ) -> List[MemoryItem]:
        """
        Search memories using BigQuery text search.
        
        Note: For semantic search, you may want to use vector search
        or integrate with a vector database.
        """
        # Simple text search using BigQuery
        sql_query = f"""
        SELECT *
        FROM `{self.project_id}.{self.dataset_id}.{self.table_id}`
        WHERE user_id = @user_id
        AND LOWER(content) LIKE LOWER(@query)
        """
        
        params = [
            bigquery.ScalarQueryParameter("user_id", "STRING", user_id),
            bigquery.ScalarQueryParameter("query", "STRING", f"%{query}%"),
        ]
        
        if project_id:
            sql_query += " AND project_id = @project_id"
            params.append(bigquery.ScalarQueryParameter("project_id", "STRING", project_id))
        
        sql_query += f" ORDER BY created_at DESC LIMIT {limit}"
        
        job_config = bigquery.QueryJobConfig(query_parameters=params)
        query_job = self.client.query(sql_query, job_config=job_config)
        results = list(query_job)
        
        return [self._row_to_memory(row) for row in results]
    
    def _row_to_memory(self, row) -> MemoryItem:
        """Convert BigQuery row to MemoryItem."""
        return MemoryItem(
            id=row.id,
            user_id=row.user_id,
            content=row.content,
            memory_type=MemoryType(row.memory_type),
            project_id=row.project_id,
            created_at=row.created_at if hasattr(row.created_at, 'isoformat') else datetime.fromisoformat(str(row.created_at)),
            updated_at=row.updated_at if hasattr(row.updated_at, 'isoformat') else datetime.fromisoformat(str(row.updated_at)),
            metadata=json.loads(row.metadata) if row.metadata else {}
        )

