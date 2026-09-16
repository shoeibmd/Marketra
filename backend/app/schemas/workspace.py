import uuid
from typing import Any

from pydantic import BaseModel, Field


class WorkspacePanelSchema(BaseModel):
    panel_id: str
    panel_type: str
    title: str
    symbol: str | None = "AAPL"
    x: int = 0
    y: int = 0
    w: int = 4
    h: int = 2


class WorkspaceCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = None
    is_default: bool = False
    layout_config: list[dict[str, Any]] = Field(default_factory=list)


class WorkspaceUpdateRequest(BaseModel):
    name: str | None = None
    description: str | None = None
    is_default: bool | None = None
    layout_config: list[dict[str, Any]] | None = None


class WorkspaceResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    name: str
    description: str | None = None
    is_default: bool
    layout_config: list[dict[str, Any]]
    created_at: str
    updated_at: str
