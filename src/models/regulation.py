"""
法規資料模型

定義法規相關的 Pydantic 資料模型，用於 Agent 間的資料傳遞與驗證。
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, HttpUrl


# ===========================================
# 列舉類型定義
# ===========================================

class Jurisdiction(str, Enum):
    """司法管轄區域"""
    TAIWAN = "TW"
    EU = "EU"
    USA = "US"
    INTERNATIONAL = "INTL"
    JAPAN = "JP"


class RegulationType(str, Enum):
    """法規類型"""
    LAW = "law"                    # 法律
    REGULATION = "regulation"      # 法規/規則
    STANDARD = "standard"          # 標準
    GUIDELINE = "guideline"        # 指引
    FRAMEWORK = "framework"        # 框架


class SourceType(str, Enum):
    """資料來源類型"""
    API = "api"
    SCRAPE = "scrape"
    DATABASE = "database"
    MANUAL = "manual"


class QueryIntent(str, Enum):
    """查詢意圖類型"""
    SEARCH = "search"              # 搜尋法規
    COMPARE = "compare"            # 比較法規
    UPDATE = "update"              # 更新法規
    TRANSLATE = "translate"        # 翻譯法規


class IssueSeverity(str, Enum):
    """問題嚴重程度"""
    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"


class Language(str, Enum):
    """支援的語言"""
    ZH_TW = "zh-TW"    # 繁體中文
    ZH_CN = "zh-CN"    # 簡體中文
    EN_US = "en-US"    # 英文
    JA_JP = "ja-JP"    # 日文


# ===========================================
# 法規相關模型
# ===========================================

class Requirement(BaseModel):
    """合規要求"""
    requirement_id: str = Field(..., description="要求識別碼")
    description: str = Field(..., description="要求描述")
    category: Optional[str] = Field(None, description="要求類別")
    mandatory: bool = Field(True, description="是否為強制要求")
    references: list[str] = Field(default_factory=list, description="相關引用")


class Article(BaseModel):
    """法規條文"""
    article_number: str = Field(..., description="條文編號")
    title: Optional[str] = Field(None, description="條文標題")
    content: str = Field(..., description="條文內容")
    summary: Optional[str] = Field(None, description="條文摘要")
    requirements: list[Requirement] = Field(default_factory=list, description="衍生的合規要求")
    references: list[str] = Field(default_factory=list, description="引用其他條文")
    penalties: list[str] = Field(default_factory=list, description="相關罰則")


class RegulationMetadata(BaseModel):
    """法規元資料"""
    source_url: Optional[HttpUrl] = Field(None, description="來源 URL")
    source_type: SourceType = Field(..., description="來源類型")
    retrieved_at: datetime = Field(default_factory=datetime.now, description="擷取時間")
    language: Language = Field(..., description="原始語言")
    version: Optional[str] = Field(None, description="版本號")
    hash: Optional[str] = Field(None, description="內容雜湊值")


class Regulation(BaseModel):
    """法規完整資料結構"""
    regulation_id: str = Field(..., description="法規唯一識別碼")
    title: str = Field(..., description="法規名稱")
    title_en: Optional[str] = Field(None, description="英文名稱")
    jurisdiction: Jurisdiction = Field(..., description="司法管轄區")
    regulation_type: RegulationType = Field(..., description="法規類型")
    effective_date: Optional[datetime] = Field(None, description="生效日期")
    last_amended_date: Optional[datetime] = Field(None, description="最後修訂日期")
    issuing_authority: Optional[str] = Field(None, description="發布機關")
    summary: Optional[str] = Field(None, description="法規摘要")
    articles: list[Article] = Field(default_factory=list, description="條文列表")
    metadata: RegulationMetadata = Field(..., description="元資料")

    class Config:
        json_schema_extra = {
            "example": {
                "regulation_id": "TW-PDPA-2023",
                "title": "個人資料保護法",
                "title_en": "Personal Data Protection Act",
                "jurisdiction": "TW",
                "regulation_type": "law",
                "effective_date": "2023-05-31T00:00:00",
                "issuing_authority": "法務部",
            }
        }


# ===========================================
# 查詢計畫相關模型
# ===========================================

class DataSource(BaseModel):
    """資料來源定義"""
    name: str = Field(..., description="來源名稱")
    source_type: SourceType = Field(..., description="來源類型")
    url: Optional[HttpUrl] = Field(None, description="來源 URL")
    priority: int = Field(1, description="優先級 (1 為最高)")
    enabled: bool = Field(True, description="是否啟用")


class QueryTarget(BaseModel):
    """查詢目標"""
    regulation_type: Optional[RegulationType] = Field(None, description="法規類型")
    jurisdiction: Jurisdiction = Field(..., description="司法管轄區")
    keywords: list[str] = Field(default_factory=list, description="關鍵字")
    date_range: Optional[dict] = Field(None, description="日期範圍")


class QueryPlan(BaseModel):
    """查詢計畫"""
    query_id: str = Field(..., description="查詢識別碼")
    intent: QueryIntent = Field(..., description="查詢意圖")
    original_query: str = Field(..., description="原始查詢文字")
    targets: list[QueryTarget] = Field(..., description="查詢目標列表")
    sources: list[DataSource] = Field(..., description="資料來源列表")
    created_at: datetime = Field(default_factory=datetime.now, description="建立時間")

    class Config:
        json_schema_extra = {
            "example": {
                "query_id": "Q-20241128-001",
                "intent": "search",
                "original_query": "找出台灣個人資料保護法的最新版本",
                "targets": [
                    {
                        "regulation_type": "law",
                        "jurisdiction": "TW",
                        "keywords": ["個人資料保護法", "個資法"]
                    }
                ]
            }
        }


# ===========================================
# 驗證報告相關模型
# ===========================================

class ValidationCheck(BaseModel):
    """驗證檢查項目"""
    check_type: str = Field(..., description="檢查類型")
    passed: bool = Field(..., description="是否通過")
    details: str = Field(..., description="檢查詳情")
    score: Optional[int] = Field(None, description="分數 (0-100)")


class ValidationIssue(BaseModel):
    """驗證問題"""
    severity: IssueSeverity = Field(..., description="嚴重程度")
    description: str = Field(..., description="問題描述")
    location: Optional[str] = Field(None, description="問題位置")
    suggestion: Optional[str] = Field(None, description="修正建議")


class ValidationReport(BaseModel):
    """驗證報告"""
    validation_id: str = Field(..., description="驗證識別碼")
    regulation_id: str = Field(..., description="法規識別碼")
    overall_score: int = Field(..., ge=0, le=100, description="總體可信度分數")
    checks: list[ValidationCheck] = Field(..., description="檢查項目列表")
    issues: list[ValidationIssue] = Field(default_factory=list, description="發現的問題")
    recommendations: list[str] = Field(default_factory=list, description="建議動作")
    validated_at: datetime = Field(default_factory=datetime.now, description="驗證時間")

    @property
    def is_trusted(self) -> bool:
        """判斷是否可信 (分數 >= 75)"""
        return self.overall_score >= 75


# ===========================================
# 翻譯結果相關模型
# ===========================================

class TranslationResult(BaseModel):
    """翻譯結果"""
    translation_id: str = Field(..., description="翻譯識別碼")
    source_language: Language = Field(..., description="來源語言")
    target_language: Language = Field(..., description="目標語言")
    original_text: str = Field(..., description="原文")
    translated_text: str = Field(..., description="譯文")
    terminology_notes: list[dict] = Field(default_factory=list, description="術語標註")
    confidence_score: Optional[float] = Field(None, ge=0, le=1, description="翻譯信心分數")
    needs_review: bool = Field(False, description="是否需要人工審核")
    translated_at: datetime = Field(default_factory=datetime.now, description="翻譯時間")


# ===========================================
# Agent 通訊相關模型
# ===========================================

class AgentMessage(BaseModel):
    """Agent 間的訊息格式"""
    sender: str = Field(..., description="發送者 Agent 名稱")
    receiver: str = Field(..., description="接收者 Agent 名稱")
    message_type: str = Field(..., description="訊息類型")
    payload: dict = Field(..., description="訊息內容")
    timestamp: datetime = Field(default_factory=datetime.now, description="時間戳記")


class TaskStatus(str, Enum):
    """任務狀態"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskResult(BaseModel):
    """任務執行結果"""
    task_id: str = Field(..., description="任務識別碼")
    status: TaskStatus = Field(..., description="任務狀態")
    result: Optional[dict] = Field(None, description="執行結果")
    error: Optional[str] = Field(None, description="錯誤訊息")
    started_at: Optional[datetime] = Field(None, description="開始時間")
    completed_at: Optional[datetime] = Field(None, description="完成時間")
