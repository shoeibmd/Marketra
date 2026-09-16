import uuid
from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth.auth_service import get_current_user
from app.db.session import get_postgres_db
from app.models.domain import Workspace
from app.schemas.workspace import (
    WorkspaceCreateRequest,
    WorkspaceResponse,
    WorkspaceUpdateRequest,
)

router = APIRouter(prefix="/workspaces", tags=["Workspaces"])


@router.get("", response_model=list[WorkspaceResponse])
async def list_user_workspaces(
    db: AsyncSession = Depends(get_postgres_db),
    current_user: dict[str, Any] = Depends(get_current_user),
) -> list[WorkspaceResponse]:
    """List all workspaces owned by the user."""
    user_id = uuid.UUID(current_user["id"])
    stmt = select(Workspace).where(Workspace.user_id == user_id)
    workspaces = (await db.scalars(stmt)).all()

    if not workspaces:
        def_ws = Workspace(
            id=uuid.uuid4(),
            user_id=user_id,
            name="Macro Overview Workspace",
            description="Default system workspace",
            is_default=True,
            layout_config=[
                {
                    "panelId": "panel_chart_1",
                    "panelType": "chart",
                    "title": "AAPL Technical Chart",
                    "symbol": "AAPL",
                    "x": 0,
                    "y": 0,
                    "w": 8,
                    "h": 3,
                },
                {
                    "panelId": "panel_overview_1",
                    "panelType": "overview",
                    "title": "Global Market Overview",
                    "symbol": "SPY",
                    "x": 8,
                    "y": 0,
                    "w": 4,
                    "h": 3,
                },
            ],
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        db.add(def_ws)
        await db.commit()
        await db.refresh(def_ws)
        workspaces = [def_ws]

    return [
        WorkspaceResponse(
            id=w.id,
            user_id=w.user_id,
            name=w.name,
            description=w.description,
            is_default=w.is_default,
            layout_config=w.layout_config.get("layout", []) if isinstance(w.layout_config, dict) else w.layout_config,
            created_at=w.created_at.isoformat(),
            updated_at=w.updated_at.isoformat(),
        )
        for w in workspaces
    ]


@router.get("/{workspace_id}", response_model=WorkspaceResponse)
async def get_workspace(
    workspace_id: uuid.UUID,
    db: AsyncSession = Depends(get_postgres_db),
    current_user: dict[str, Any] = Depends(get_current_user),
) -> WorkspaceResponse:
    """Fetch single workspace layout details."""
    user_id = uuid.UUID(current_user["id"])
    ws = await db.get(Workspace, workspace_id)
    if not ws or ws.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workspace {workspace_id} not found",
        )

    return WorkspaceResponse(
        id=ws.id,
        user_id=ws.user_id,
        name=ws.name,
        description=ws.description,
        is_default=ws.is_default,
        layout_config=ws.layout_config.get("layout", []) if isinstance(ws.layout_config, dict) else ws.layout_config,
        created_at=ws.created_at.isoformat(),
        updated_at=ws.updated_at.isoformat(),
    )


@router.post("", response_model=WorkspaceResponse)
async def create_workspace(
    req: WorkspaceCreateRequest,
    db: AsyncSession = Depends(get_postgres_db),
    current_user: dict[str, Any] = Depends(get_current_user),
) -> WorkspaceResponse:
    """Create a new workspace layout."""
    user_id = uuid.UUID(current_user["id"])
    ws = Workspace(
        id=uuid.uuid4(),
        user_id=user_id,
        name=req.name,
        description=req.description,
        is_default=req.is_default,
        layout_config={"layout": req.layout_config},
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    db.add(ws)
    await db.commit()
    await db.refresh(ws)

    return WorkspaceResponse(
        id=ws.id,
        user_id=ws.user_id,
        name=ws.name,
        description=ws.description,
        is_default=ws.is_default,
        layout_config=req.layout_config,
        created_at=ws.created_at.isoformat(),
        updated_at=ws.updated_at.isoformat(),
    )


@router.put("/{workspace_id}", response_model=WorkspaceResponse)
async def update_workspace(
    workspace_id: uuid.UUID,
    req: WorkspaceUpdateRequest,
    db: AsyncSession = Depends(get_postgres_db),
    current_user: dict[str, Any] = Depends(get_current_user),
) -> WorkspaceResponse:
    """Update workspace layout config or metadata."""
    user_id = uuid.UUID(current_user["id"])
    ws = await db.get(Workspace, workspace_id)
    if not ws or ws.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workspace {workspace_id} not found",
        )

    if req.name is not None:
        ws.name = req.name
    if req.description is not None:
        ws.description = req.description
    if req.is_default is not None:
        ws.is_default = req.is_default
    if req.layout_config is not None:
        ws.layout_config = {"layout": req.layout_config}

    ws.updated_at = datetime.now(UTC)
    await db.commit()
    await db.refresh(ws)

    return WorkspaceResponse(
        id=ws.id,
        user_id=ws.user_id,
        name=ws.name,
        description=ws.description,
        is_default=ws.is_default,
        layout_config=ws.layout_config.get("layout", []) if isinstance(ws.layout_config, dict) else ws.layout_config,
        created_at=ws.created_at.isoformat(),
        updated_at=ws.updated_at.isoformat(),
    )


@router.delete("/{workspace_id}")
async def delete_workspace(
    workspace_id: uuid.UUID,
    db: AsyncSession = Depends(get_postgres_db),
    current_user: dict[str, Any] = Depends(get_current_user),
) -> dict[str, Any]:
    """Delete a workspace."""
    user_id = uuid.UUID(current_user["id"])
    ws = await db.get(Workspace, workspace_id)
    if not ws or ws.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workspace {workspace_id} not found",
        )

    await db.delete(ws)
    await db.commit()
    return {"status": "deleted", "workspace_id": str(workspace_id)}
