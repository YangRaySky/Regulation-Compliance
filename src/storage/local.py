"""
本機儲存實作

使用 SQLite 與 ChromaDB 實作本機儲存。
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from ..models.regulation import Regulation, TranslationResult, ValidationReport
from .interfaces import CacheInterface, StorageInterface, VectorStoreInterface


class LocalSQLiteStorage(StorageInterface):
    """
    SQLite 本機儲存實作

    使用 SQLAlchemy 操作 SQLite 資料庫。
    """

    def __init__(self, db_path: str = "./data/regulations.db"):
        """
        初始化 SQLite 儲存

        Args:
            db_path: 資料庫檔案路徑
        """
        self.db_path = db_path
        self._ensure_directory()
        self._init_db()

    def _ensure_directory(self):
        """確保目錄存在"""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

    def _init_db(self):
        """初始化資料庫表格"""
        import sqlite3

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 法規資料表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS regulations (
                regulation_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                title_en TEXT,
                jurisdiction TEXT NOT NULL,
                regulation_type TEXT NOT NULL,
                effective_date TEXT,
                last_amended_date TEXT,
                issuing_authority TEXT,
                summary TEXT,
                articles_json TEXT,
                metadata_json TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)

        # 驗證報告表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS validation_reports (
                validation_id TEXT PRIMARY KEY,
                regulation_id TEXT NOT NULL,
                overall_score INTEGER NOT NULL,
                checks_json TEXT,
                issues_json TEXT,
                recommendations_json TEXT,
                validated_at TEXT NOT NULL,
                FOREIGN KEY (regulation_id) REFERENCES regulations(regulation_id)
            )
        """)

        # 翻譯結果表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS translations (
                translation_id TEXT PRIMARY KEY,
                source_language TEXT NOT NULL,
                target_language TEXT NOT NULL,
                original_text TEXT NOT NULL,
                translated_text TEXT NOT NULL,
                terminology_notes_json TEXT,
                confidence_score REAL,
                needs_review INTEGER,
                translated_at TEXT NOT NULL
            )
        """)

        conn.commit()
        conn.close()

    async def save_regulation(self, regulation: Regulation) -> str:
        """儲存法規資料"""
        import sqlite3

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        now = datetime.now().isoformat()

        cursor.execute("""
            INSERT OR REPLACE INTO regulations (
                regulation_id, title, title_en, jurisdiction, regulation_type,
                effective_date, last_amended_date, issuing_authority, summary,
                articles_json, metadata_json, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            regulation.regulation_id,
            regulation.title,
            regulation.title_en,
            regulation.jurisdiction.value,
            regulation.regulation_type.value,
            regulation.effective_date.isoformat() if regulation.effective_date else None,
            regulation.last_amended_date.isoformat() if regulation.last_amended_date else None,
            regulation.issuing_authority,
            regulation.summary,
            json.dumps([a.model_dump() for a in regulation.articles], ensure_ascii=False),
            json.dumps(regulation.metadata.model_dump(), ensure_ascii=False, default=str),
            now,
            now,
        ))

        conn.commit()
        conn.close()

        return regulation.regulation_id

    async def get_regulation(self, regulation_id: str) -> Optional[Regulation]:
        """取得法規資料"""
        import sqlite3

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM regulations WHERE regulation_id = ?",
            (regulation_id,)
        )
        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        # 將資料庫記錄轉換為 Regulation 物件
        return self._row_to_regulation(row)

    def _row_to_regulation(self, row) -> Regulation:
        """將資料庫記錄轉換為 Regulation 物件"""
        from ..models.regulation import Article, Jurisdiction, Regulation, RegulationMetadata, RegulationType

        articles_data = json.loads(row[9]) if row[9] else []
        metadata_data = json.loads(row[10]) if row[10] else {}

        return Regulation(
            regulation_id=row[0],
            title=row[1],
            title_en=row[2],
            jurisdiction=Jurisdiction(row[3]),
            regulation_type=RegulationType(row[4]),
            effective_date=datetime.fromisoformat(row[5]) if row[5] else None,
            last_amended_date=datetime.fromisoformat(row[6]) if row[6] else None,
            issuing_authority=row[7],
            summary=row[8],
            articles=[Article(**a) for a in articles_data],
            metadata=RegulationMetadata(**metadata_data),
        )

    async def list_regulations(
        self,
        jurisdiction: Optional[str] = None,
        regulation_type: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Regulation]:
        """列出法規資料"""
        import sqlite3

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = "SELECT * FROM regulations WHERE 1=1"
        params = []

        if jurisdiction:
            query += " AND jurisdiction = ?"
            params.append(jurisdiction)

        if regulation_type:
            query += " AND regulation_type = ?"
            params.append(regulation_type)

        query += " ORDER BY updated_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        return [self._row_to_regulation(row) for row in rows]

    async def update_regulation(self, regulation: Regulation) -> bool:
        """更新法規資料"""
        try:
            await self.save_regulation(regulation)
            return True
        except Exception:
            return False

    async def delete_regulation(self, regulation_id: str) -> bool:
        """刪除法規資料"""
        import sqlite3

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            "DELETE FROM regulations WHERE regulation_id = ?",
            (regulation_id,)
        )
        affected = cursor.rowcount

        conn.commit()
        conn.close()

        return affected > 0

    async def save_validation_report(self, report: ValidationReport) -> str:
        """儲存驗證報告"""
        import sqlite3

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO validation_reports (
                validation_id, regulation_id, overall_score,
                checks_json, issues_json, recommendations_json, validated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            report.validation_id,
            report.regulation_id,
            report.overall_score,
            json.dumps([c.model_dump() for c in report.checks], ensure_ascii=False),
            json.dumps([i.model_dump() for i in report.issues], ensure_ascii=False),
            json.dumps(report.recommendations, ensure_ascii=False),
            report.validated_at.isoformat(),
        ))

        conn.commit()
        conn.close()

        return report.validation_id

    async def get_validation_reports(
        self,
        regulation_id: str,
        limit: int = 10,
    ) -> list[ValidationReport]:
        """取得法規的驗證報告歷史"""
        import sqlite3

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM validation_reports
            WHERE regulation_id = ?
            ORDER BY validated_at DESC
            LIMIT ?
        """, (regulation_id, limit))

        rows = cursor.fetchall()
        conn.close()

        reports = []
        for row in rows:
            from ..models.regulation import ValidationCheck, ValidationIssue

            reports.append(ValidationReport(
                validation_id=row[0],
                regulation_id=row[1],
                overall_score=row[2],
                checks=[ValidationCheck(**c) for c in json.loads(row[3] or "[]")],
                issues=[ValidationIssue(**i) for i in json.loads(row[4] or "[]")],
                recommendations=json.loads(row[5] or "[]"),
                validated_at=datetime.fromisoformat(row[6]),
            ))

        return reports

    async def save_translation(self, translation: TranslationResult) -> str:
        """儲存翻譯結果"""
        import sqlite3

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO translations (
                translation_id, source_language, target_language,
                original_text, translated_text, terminology_notes_json,
                confidence_score, needs_review, translated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            translation.translation_id,
            translation.source_language.value,
            translation.target_language.value,
            translation.original_text,
            translation.translated_text,
            json.dumps(translation.terminology_notes, ensure_ascii=False),
            translation.confidence_score,
            1 if translation.needs_review else 0,
            translation.translated_at.isoformat(),
        ))

        conn.commit()
        conn.close()

        return translation.translation_id


class LocalChromaVectorStore(VectorStoreInterface):
    """
    ChromaDB 本機向量資料庫實作
    """

    def __init__(
        self,
        persist_directory: str = "./data/chroma",
        collection_name: str = "regulations",
    ):
        """
        初始化 ChromaDB

        Args:
            persist_directory: 持久化目錄
            collection_name: 集合名稱
        """
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        self._client = None
        self._collection = None

    def _get_client(self):
        """取得 ChromaDB 客戶端"""
        if self._client is None:
            try:
                import chromadb
                from chromadb.config import Settings

                Path(self.persist_directory).mkdir(parents=True, exist_ok=True)

                self._client = chromadb.PersistentClient(
                    path=self.persist_directory,
                    settings=Settings(anonymized_telemetry=False),
                )
            except ImportError:
                raise ImportError(
                    "ChromaDB 未安裝。請執行: pip install chromadb"
                )
        return self._client

    def _get_collection(self):
        """取得集合"""
        if self._collection is None:
            client = self._get_client()
            self._collection = client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"},
            )
        return self._collection

    async def add_documents(
        self,
        documents: list[dict],
        embeddings: Optional[list[list[float]]] = None,
    ) -> list[str]:
        """新增文件到向量資料庫"""
        collection = self._get_collection()

        ids = []
        contents = []
        metadatas = []

        for i, doc in enumerate(documents):
            doc_id = doc.get("id", f"doc_{datetime.now().timestamp()}_{i}")
            ids.append(doc_id)
            contents.append(doc.get("content", ""))
            metadatas.append(doc.get("metadata", {}))

        if embeddings:
            collection.add(
                ids=ids,
                documents=contents,
                metadatas=metadatas,
                embeddings=embeddings,
            )
        else:
            collection.add(
                ids=ids,
                documents=contents,
                metadatas=metadatas,
            )

        return ids

    async def similarity_search(
        self,
        query: str,
        k: int = 5,
        filter: Optional[dict] = None,
    ) -> list[dict]:
        """相似度搜尋"""
        collection = self._get_collection()

        results = collection.query(
            query_texts=[query],
            n_results=k,
            where=filter,
            include=["documents", "metadatas", "distances"],
        )

        documents = []
        for i in range(len(results["ids"][0])):
            documents.append({
                "id": results["ids"][0][i],
                "content": results["documents"][0][i] if results["documents"] else "",
                "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                "score": 1 - results["distances"][0][i] if results["distances"] else 0,
            })

        return documents

    async def delete_documents(self, document_ids: list[str]) -> bool:
        """刪除文件"""
        try:
            collection = self._get_collection()
            collection.delete(ids=document_ids)
            return True
        except Exception:
            return False

    async def get_document(self, document_id: str) -> Optional[dict]:
        """取得單一文件"""
        collection = self._get_collection()

        results = collection.get(
            ids=[document_id],
            include=["documents", "metadatas"],
        )

        if not results["ids"]:
            return None

        return {
            "id": results["ids"][0],
            "content": results["documents"][0] if results["documents"] else "",
            "metadata": results["metadatas"][0] if results["metadatas"] else {},
        }

    async def update_document(
        self,
        document_id: str,
        content: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> bool:
        """更新文件"""
        try:
            collection = self._get_collection()

            update_kwargs = {"ids": [document_id]}
            if content:
                update_kwargs["documents"] = [content]
            if metadata:
                update_kwargs["metadatas"] = [metadata]

            collection.update(**update_kwargs)
            return True
        except Exception:
            return False


class LocalMemoryCache(CacheInterface):
    """
    記憶體快取實作

    簡單的字典快取，適合本機開發使用。
    """

    def __init__(self):
        self._cache: dict[str, tuple[Any, Optional[datetime]]] = {}

    async def get(self, key: str) -> Optional[Any]:
        """取得快取值"""
        if key not in self._cache:
            return None

        value, expiry = self._cache[key]

        if expiry and datetime.now() > expiry:
            del self._cache[key]
            return None

        return value

    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
    ) -> bool:
        """設定快取值"""
        expiry = None
        if ttl:
            from datetime import timedelta
            expiry = datetime.now() + timedelta(seconds=ttl)

        self._cache[key] = (value, expiry)
        return True

    async def delete(self, key: str) -> bool:
        """刪除快取"""
        if key in self._cache:
            del self._cache[key]
            return True
        return False

    async def exists(self, key: str) -> bool:
        """檢查快取是否存在"""
        return await self.get(key) is not None
