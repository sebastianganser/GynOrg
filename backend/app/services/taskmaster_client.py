"""
Taskmaster-AI Client für die Integration mit dem MCP Server.
"""
import logging
from typing import Dict, List, Optional, Any
from .llm_service import LLMService, LLMProvider, LLMRequest, LLMResponse

logger = logging.getLogger(__name__)


class TaskmasterClient:
    """
    Client für die Kommunikation mit dem Taskmaster-AI MCP Server.
    Bietet typisierte Methoden für alle Taskmaster-Funktionen.
    """
    
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service
        self.provider = LLMProvider.TASKMASTER
    
    async def get_tasks(self, 
                       status: Optional[str] = None,
                       with_subtasks: bool = False,
                       tag: Optional[str] = None) -> LLMResponse:
        """
        Holt alle Tasks vom Taskmaster.
        
        Args:
            status: Filter nach Status (z.B. 'pending', 'done')
            with_subtasks: Subtasks mit einbeziehen
            tag: Spezifischer Tag-Kontext
        """
        arguments = {}
        if status:
            arguments["status"] = status
        if with_subtasks:
            arguments["withSubtasks"] = with_subtasks
        if tag:
            arguments["tag"] = tag
        
        request = LLMRequest(
            provider=self.provider,
            tool_name="get_tasks",
            arguments=arguments
        )
        
        return await self.llm_service.call_tool(request)
    
    async def get_task(self, task_id: str, tag: Optional[str] = None) -> LLMResponse:
        """
        Holt Details zu einem spezifischen Task.
        
        Args:
            task_id: ID des Tasks (z.B. '15' oder '15.2' für Subtask)
            tag: Spezifischer Tag-Kontext
        """
        arguments = {"id": task_id}
        if tag:
            arguments["tag"] = tag
        
        request = LLMRequest(
            provider=self.provider,
            tool_name="get_task",
            arguments=arguments
        )
        
        return await self.llm_service.call_tool(request)
    
    async def next_task(self, tag: Optional[str] = None) -> LLMResponse:
        """
        Holt den nächsten verfügbaren Task basierend auf Dependencies.
        
        Args:
            tag: Spezifischer Tag-Kontext
        """
        arguments = {}
        if tag:
            arguments["tag"] = tag
        
        request = LLMRequest(
            provider=self.provider,
            tool_name="next_task",
            arguments=arguments
        )
        
        return await self.llm_service.call_tool(request)
    
    async def add_task(self,
                      prompt: str,
                      dependencies: Optional[List[str]] = None,
                      priority: str = "medium",
                      research: bool = False,
                      tag: Optional[str] = None) -> LLMResponse:
        """
        Fügt einen neuen Task hinzu.
        
        Args:
            prompt: Beschreibung des neuen Tasks
            dependencies: Liste von Task-IDs als Dependencies
            priority: Priorität ('high', 'medium', 'low')
            research: Research-Modus aktivieren
            tag: Spezifischer Tag-Kontext
        """
        arguments = {"prompt": prompt, "priority": priority}
        
        if dependencies:
            arguments["dependencies"] = ",".join(dependencies)
        if research:
            arguments["research"] = research
        if tag:
            arguments["tag"] = tag
        
        request = LLMRequest(
            provider=self.provider,
            tool_name="add_task",
            arguments=arguments
        )
        
        return await self.llm_service.call_tool(request)
    
    async def update_task(self,
                         task_id: str,
                         prompt: str,
                         append: bool = False,
                         research: bool = False,
                         tag: Optional[str] = None) -> LLMResponse:
        """
        Aktualisiert einen bestehenden Task.
        
        Args:
            task_id: ID des zu aktualisierenden Tasks
            prompt: Neue Informationen oder Änderungen
            append: Anhängen statt ersetzen
            research: Research-Modus aktivieren
            tag: Spezifischer Tag-Kontext
        """
        arguments = {
            "id": task_id,
            "prompt": prompt
        }
        
        if append:
            arguments["append"] = append
        if research:
            arguments["research"] = research
        if tag:
            arguments["tag"] = tag
        
        request = LLMRequest(
            provider=self.provider,
            tool_name="update_task",
            arguments=arguments
        )
        
        return await self.llm_service.call_tool(request)
    
    async def update_subtask(self,
                            subtask_id: str,
                            prompt: str,
                            research: bool = False,
                            tag: Optional[str] = None) -> LLMResponse:
        """
        Aktualisiert einen Subtask mit timestamped Informationen.
        
        Args:
            subtask_id: ID des Subtasks (z.B. '5.2')
            prompt: Informationen zum Anhängen
            research: Research-Modus aktivieren
            tag: Spezifischer Tag-Kontext
        """
        arguments = {
            "id": subtask_id,
            "prompt": prompt
        }
        
        if research:
            arguments["research"] = research
        if tag:
            arguments["tag"] = tag
        
        request = LLMRequest(
            provider=self.provider,
            tool_name="update_subtask",
            arguments=arguments
        )
        
        return await self.llm_service.call_tool(request)
    
    async def set_task_status(self,
                             task_id: str,
                             status: str,
                             tag: Optional[str] = None) -> LLMResponse:
        """
        Setzt den Status eines Tasks oder Subtasks.
        
        Args:
            task_id: ID des Tasks/Subtasks
            status: Neuer Status ('pending', 'in-progress', 'done', etc.)
            tag: Spezifischer Tag-Kontext
        """
        arguments = {
            "id": task_id,
            "status": status
        }
        
        if tag:
            arguments["tag"] = tag
        
        request = LLMRequest(
            provider=self.provider,
            tool_name="set_task_status",
            arguments=arguments
        )
        
        return await self.llm_service.call_tool(request)
    
    async def expand_task(self,
                         task_id: str,
                         num_subtasks: Optional[int] = None,
                         research: bool = False,
                         prompt: Optional[str] = None,
                         force: bool = False,
                         tag: Optional[str] = None) -> LLMResponse:
        """
        Erweitert einen Task in Subtasks.
        
        Args:
            task_id: ID des zu erweiternden Tasks
            num_subtasks: Anzahl der zu erstellenden Subtasks
            research: Research-Modus aktivieren
            prompt: Zusätzlicher Kontext
            force: Bestehende Subtasks überschreiben
            tag: Spezifischer Tag-Kontext
        """
        arguments = {"id": task_id}
        
        if num_subtasks:
            arguments["num"] = str(num_subtasks)
        if research:
            arguments["research"] = research
        if prompt:
            arguments["prompt"] = prompt
        if force:
            arguments["force"] = force
        if tag:
            arguments["tag"] = tag
        
        request = LLMRequest(
            provider=self.provider,
            tool_name="expand_task",
            arguments=arguments
        )
        
        return await self.llm_service.call_tool(request)
    
    async def research(self,
                      query: str,
                      task_ids: Optional[List[str]] = None,
                      file_paths: Optional[List[str]] = None,
                      custom_context: Optional[str] = None,
                      include_project_tree: bool = False,
                      detail_level: str = "medium",
                      save_to: Optional[str] = None,
                      tag: Optional[str] = None) -> LLMResponse:
        """
        Führt eine AI-gestützte Recherche durch.
        
        Args:
            query: Recherche-Anfrage
            task_ids: Task-IDs für Kontext
            file_paths: Dateipfade für Kontext
            custom_context: Zusätzlicher Kontext
            include_project_tree: Projektstruktur einbeziehen
            detail_level: Detailgrad ('low', 'medium', 'high')
            save_to: Task-ID zum Speichern der Ergebnisse
            tag: Spezifischer Tag-Kontext
        """
        arguments = {"query": query, "detailLevel": detail_level}
        
        if task_ids:
            arguments["taskIds"] = ",".join(task_ids)
        if file_paths:
            arguments["filePaths"] = ",".join(file_paths)
        if custom_context:
            arguments["customContext"] = custom_context
        if include_project_tree:
            arguments["includeProjectTree"] = include_project_tree
        if save_to:
            arguments["saveTo"] = save_to
        if tag:
            arguments["tag"] = tag
        
        request = LLMRequest(
            provider=self.provider,
            tool_name="research",
            arguments=arguments
        )
        
        return await self.llm_service.call_tool(request)
    
    async def analyze_complexity(self,
                                threshold: int = 5,
                                research: bool = False,
                                tag: Optional[str] = None) -> LLMResponse:
        """
        Analysiert die Komplexität der Tasks.
        
        Args:
            threshold: Komplexitäts-Schwellwert (1-10)
            research: Research-Modus aktivieren
            tag: Spezifischer Tag-Kontext
        """
        arguments = {"threshold": threshold}
        
        if research:
            arguments["research"] = research
        if tag:
            arguments["tag"] = tag
        
        request = LLMRequest(
            provider=self.provider,
            tool_name="analyze_project_complexity",
            arguments=arguments
        )
        
        return await self.llm_service.call_tool(request)
    
    async def parse_prd(self,
                       input_file: str,
                       num_tasks: Optional[int] = None,
                       force: bool = False,
                       research: bool = False,
                       append: bool = False,
                       tag: Optional[str] = None) -> LLMResponse:
        """
        Parst ein PRD und generiert Tasks.
        
        Args:
            input_file: Pfad zur PRD-Datei
            num_tasks: Anzahl der zu generierenden Tasks
            force: Bestehende Tasks überschreiben
            research: Research-Modus aktivieren
            append: An bestehende Tasks anhängen
            tag: Spezifischer Tag-Kontext
        """
        arguments = {"input": input_file}
        
        if num_tasks:
            arguments["numTasks"] = str(num_tasks)
        if force:
            arguments["force"] = force
        if research:
            arguments["research"] = research
        if append:
            arguments["append"] = append
        if tag:
            arguments["tag"] = tag
        
        request = LLMRequest(
            provider=self.provider,
            tool_name="parse_prd",
            arguments=arguments
        )
        
        return await self.llm_service.call_tool(request)
