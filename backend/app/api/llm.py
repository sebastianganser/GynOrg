"""
API Endpoints für LLM-Integration (Taskmaster-AI und Context7).
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, List, Optional, Any
import logging

from ..services.llm_service import llm_service, LLMProvider
from ..services.taskmaster_client import TaskmasterClient
from ..services.context7_client import Context7Client
from ..core.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/llm", tags=["LLM"])

# Client-Instanzen
taskmaster_client = TaskmasterClient(llm_service)
context7_client = Context7Client(llm_service)


@router.on_event("startup")
async def initialize_llm_service():
    """Initialisiert den LLM Service beim Start."""
    success = await llm_service.initialize()
    if success:
        logger.info("LLM Service erfolgreich initialisiert")
    else:
        logger.error("LLM Service Initialisierung fehlgeschlagen")


@router.get("/status")
async def get_llm_status(current_user: dict = Depends(get_current_user)):
    """
    Gibt den Status aller LLM-Provider zurück.
    """
    try:
        status = llm_service.get_provider_status()
        health = await llm_service.health_check()
        
        return {
            "status": status,
            "health": health,
            "timestamp": "2025-01-07T15:26:00Z"
        }
    except Exception as e:
        logger.error(f"Fehler beim Abrufen des LLM-Status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Taskmaster-AI Endpoints
@router.get("/taskmaster/tasks")
async def get_tasks(
    status: Optional[str] = None,
    with_subtasks: bool = False,
    tag: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """
    Holt alle Tasks vom Taskmaster-AI.
    """
    try:
        response = await taskmaster_client.get_tasks(status, with_subtasks, tag)
        
        if not response.success:
            raise HTTPException(status_code=400, detail=response.error)
        
        return response.data
    except Exception as e:
        logger.error(f"Fehler beim Abrufen der Tasks: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/taskmaster/tasks/{task_id}")
async def get_task(
    task_id: str,
    tag: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """
    Holt Details zu einem spezifischen Task.
    """
    try:
        response = await taskmaster_client.get_task(task_id, tag)
        
        if not response.success:
            raise HTTPException(status_code=404, detail=response.error)
        
        return response.data
    except Exception as e:
        logger.error(f"Fehler beim Abrufen des Tasks {task_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/taskmaster/next-task")
async def get_next_task(
    tag: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """
    Holt den nächsten verfügbaren Task.
    """
    try:
        response = await taskmaster_client.next_task(tag)
        
        if not response.success:
            raise HTTPException(status_code=400, detail=response.error)
        
        return response.data
    except Exception as e:
        logger.error(f"Fehler beim Abrufen des nächsten Tasks: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/taskmaster/tasks")
async def add_task(
    task_data: Dict[str, Any],
    current_user: dict = Depends(get_current_user)
):
    """
    Fügt einen neuen Task hinzu.
    
    Body:
    {
        "prompt": "Task-Beschreibung",
        "dependencies": ["1", "2"],  // optional
        "priority": "medium",        // optional
        "research": false,           // optional
        "tag": "feature-branch"      // optional
    }
    """
    try:
        prompt = task_data.get("prompt")
        if not prompt:
            raise HTTPException(status_code=400, detail="Prompt ist erforderlich")
        
        dependencies = task_data.get("dependencies")
        priority = task_data.get("priority", "medium")
        research = task_data.get("research", False)
        tag = task_data.get("tag")
        
        response = await taskmaster_client.add_task(
            prompt=prompt,
            dependencies=dependencies,
            priority=priority,
            research=research,
            tag=tag
        )
        
        if not response.success:
            raise HTTPException(status_code=400, detail=response.error)
        
        return response.data
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Fehler beim Hinzufügen des Tasks: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/taskmaster/tasks/{task_id}")
async def update_task(
    task_id: str,
    update_data: Dict[str, Any],
    current_user: dict = Depends(get_current_user)
):
    """
    Aktualisiert einen bestehenden Task.
    
    Body:
    {
        "prompt": "Neue Informationen",
        "append": false,             // optional
        "research": false,           // optional
        "tag": "feature-branch"      // optional
    }
    """
    try:
        prompt = update_data.get("prompt")
        if not prompt:
            raise HTTPException(status_code=400, detail="Prompt ist erforderlich")
        
        append = update_data.get("append", False)
        research = update_data.get("research", False)
        tag = update_data.get("tag")
        
        response = await taskmaster_client.update_task(
            task_id=task_id,
            prompt=prompt,
            append=append,
            research=research,
            tag=tag
        )
        
        if not response.success:
            raise HTTPException(status_code=400, detail=response.error)
        
        return response.data
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Fehler beim Aktualisieren des Tasks {task_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/taskmaster/tasks/{task_id}/status")
async def set_task_status(
    task_id: str,
    status_data: Dict[str, str],
    current_user: dict = Depends(get_current_user)
):
    """
    Setzt den Status eines Tasks.
    
    Body:
    {
        "status": "done",
        "tag": "feature-branch"  // optional
    }
    """
    try:
        status = status_data.get("status")
        if not status:
            raise HTTPException(status_code=400, detail="Status ist erforderlich")
        
        tag = status_data.get("tag")
        
        response = await taskmaster_client.set_task_status(
            task_id=task_id,
            status=status,
            tag=tag
        )
        
        if not response.success:
            raise HTTPException(status_code=400, detail=response.error)
        
        return response.data
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Fehler beim Setzen des Task-Status {task_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/taskmaster/research")
async def research(
    research_data: Dict[str, Any],
    current_user: dict = Depends(get_current_user)
):
    """
    Führt eine AI-gestützte Recherche durch.
    
    Body:
    {
        "query": "Recherche-Anfrage",
        "task_ids": ["1", "2"],          // optional
        "file_paths": ["src/main.py"],   // optional
        "custom_context": "...",         // optional
        "include_project_tree": false,   // optional
        "detail_level": "medium",        // optional
        "save_to": "1.2",               // optional
        "tag": "feature-branch"          // optional
    }
    """
    try:
        query = research_data.get("query")
        if not query:
            raise HTTPException(status_code=400, detail="Query ist erforderlich")
        
        task_ids = research_data.get("task_ids")
        file_paths = research_data.get("file_paths")
        custom_context = research_data.get("custom_context")
        include_project_tree = research_data.get("include_project_tree", False)
        detail_level = research_data.get("detail_level", "medium")
        save_to = research_data.get("save_to")
        tag = research_data.get("tag")
        
        response = await taskmaster_client.research(
            query=query,
            task_ids=task_ids,
            file_paths=file_paths,
            custom_context=custom_context,
            include_project_tree=include_project_tree,
            detail_level=detail_level,
            save_to=save_to,
            tag=tag
        )
        
        if not response.success:
            raise HTTPException(status_code=400, detail=response.error)
        
        return response.data
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Fehler bei der Recherche: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Context7 Endpoints
@router.get("/context7/libraries/search")
async def search_libraries(
    q: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Sucht nach Libraries basierend auf einem Suchbegriff.
    """
    try:
        response = await context7_client.search_libraries(q)
        
        if not response.success:
            raise HTTPException(status_code=400, detail=response.error)
        
        return response.data
    except Exception as e:
        logger.error(f"Fehler bei der Library-Suche: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/context7/libraries/{library_name}/docs")
async def get_library_docs(
    library_name: str,
    topic: Optional[str] = None,
    tokens: int = 10000,
    current_user: dict = Depends(get_current_user)
):
    """
    Holt Dokumentation für eine Library.
    """
    try:
        response = await context7_client.get_docs_for_library(
            library_name=library_name,
            topic=topic,
            tokens=tokens
        )
        
        if not response.success:
            raise HTTPException(status_code=404, detail=response.error)
        
        return response.data
    except Exception as e:
        logger.error(f"Fehler beim Abrufen der Library-Docs für {library_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/context7/frameworks/{framework}/docs")
async def get_framework_docs(
    framework: str,
    version: Optional[str] = None,
    topic: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """
    Holt Framework-Dokumentation.
    """
    try:
        response = await context7_client.get_framework_docs(
            framework=framework,
            version=version,
            topic=topic
        )
        
        if not response.success:
            raise HTTPException(status_code=404, detail=response.error)
        
        return response.data
    except Exception as e:
        logger.error(f"Fehler beim Abrufen der Framework-Docs für {framework}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/context7/best-practices/{technology}")
async def get_best_practices(
    technology: str,
    use_case: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """
    Holt Best Practices für eine Technologie.
    """
    try:
        response = await context7_client.get_best_practices(
            technology=technology,
            use_case=use_case
        )
        
        if not response.success:
            raise HTTPException(status_code=404, detail=response.error)
        
        return response.data
    except Exception as e:
        logger.error(f"Fehler beim Abrufen der Best Practices für {technology}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
