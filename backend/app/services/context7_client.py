"""
Context7 Client für die Integration mit dem MCP Server.
"""
import logging
from typing import Dict, List, Optional, Any
from .llm_service import LLMService, LLMProvider, LLMRequest, LLMResponse

logger = logging.getLogger(__name__)


class Context7Client:
    """
    Client für die Kommunikation mit dem Context7 MCP Server.
    Bietet typisierte Methoden für Context7-Funktionen.
    """
    
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service
        self.provider = LLMProvider.CONTEXT7
    
    async def resolve_library_id(self, library_name: str) -> LLMResponse:
        """
        Löst einen Library-Namen zu einer Context7-kompatiblen Library-ID auf.
        
        Args:
            library_name: Name der zu suchenden Library
            
        Returns:
            LLMResponse mit Library-ID und passenden Libraries
        """
        arguments = {"libraryName": library_name}
        
        request = LLMRequest(
            provider=self.provider,
            tool_name="resolve-library-id",
            arguments=arguments
        )
        
        return await self.llm_service.call_tool(request)
    
    async def get_library_docs(self,
                              library_id: str,
                              topic: Optional[str] = None,
                              tokens: int = 10000) -> LLMResponse:
        """
        Holt aktuelle Dokumentation für eine Library.
        
        Args:
            library_id: Context7-kompatible Library-ID (z.B. '/mongodb/docs')
            topic: Spezifisches Thema (z.B. 'hooks', 'routing')
            tokens: Maximale Anzahl Tokens der Dokumentation
            
        Returns:
            LLMResponse mit Dokumentation und Beispielen
        """
        arguments = {
            "context7CompatibleLibraryID": library_id,
            "tokens": tokens
        }
        
        if topic:
            arguments["topic"] = topic
        
        request = LLMRequest(
            provider=self.provider,
            tool_name="get-library-docs",
            arguments=arguments
        )
        
        return await self.llm_service.call_tool(request)
    
    async def get_docs_for_library(self, 
                                  library_name: str,
                                  topic: Optional[str] = None,
                                  tokens: int = 10000) -> LLMResponse:
        """
        Convenience-Methode: Löst Library-Name auf und holt Dokumentation.
        
        Args:
            library_name: Name der Library (z.B. 'react', 'fastapi')
            topic: Spezifisches Thema
            tokens: Maximale Anzahl Tokens
            
        Returns:
            LLMResponse mit Dokumentation oder Fehler
        """
        # Erst Library-ID auflösen
        resolve_response = await self.resolve_library_id(library_name)
        
        if not resolve_response.success:
            return resolve_response
        
        # Library-ID aus der Antwort extrahieren
        library_data = resolve_response.data
        if not library_data or "library_id" not in library_data:
            return LLMResponse(
                success=False,
                error=f"Keine Library-ID für '{library_name}' gefunden"
            )
        
        library_id = library_data["library_id"]
        
        # Dokumentation holen
        return await self.get_library_docs(library_id, topic, tokens)
    
    async def search_libraries(self, search_term: str) -> LLMResponse:
        """
        Sucht nach Libraries basierend auf einem Suchbegriff.
        
        Args:
            search_term: Suchbegriff für Libraries
            
        Returns:
            LLMResponse mit gefundenen Libraries
        """
        # Nutzt resolve_library_id für die Suche
        return await self.resolve_library_id(search_term)
    
    async def get_framework_docs(self,
                                framework: str,
                                version: Optional[str] = None,
                                topic: Optional[str] = None) -> LLMResponse:
        """
        Holt Dokumentation für ein spezifisches Framework.
        
        Args:
            framework: Framework-Name (z.B. 'react', 'fastapi', 'vue')
            version: Spezifische Version (optional)
            topic: Spezifisches Thema (optional)
            
        Returns:
            LLMResponse mit Framework-Dokumentation
        """
        library_name = framework
        if version:
            # Versuche versionsspezifische Library-ID
            library_name = f"{framework}/{version}"
        
        return await self.get_docs_for_library(library_name, topic)
    
    async def get_api_docs(self,
                          api_name: str,
                          endpoint: Optional[str] = None) -> LLMResponse:
        """
        Holt API-Dokumentation.
        
        Args:
            api_name: Name der API
            endpoint: Spezifischer Endpoint (als Topic)
            
        Returns:
            LLMResponse mit API-Dokumentation
        """
        return await self.get_docs_for_library(api_name, endpoint)
    
    async def get_best_practices(self,
                                technology: str,
                                use_case: Optional[str] = None) -> LLMResponse:
        """
        Holt Best Practices für eine Technologie.
        
        Args:
            technology: Technologie-Name
            use_case: Spezifischer Anwendungsfall
            
        Returns:
            LLMResponse mit Best Practices
        """
        topic = "best practices"
        if use_case:
            topic = f"best practices {use_case}"
        
        return await self.get_docs_for_library(technology, topic)
    
    async def get_migration_guide(self,
                                 from_version: str,
                                 to_version: str,
                                 technology: str) -> LLMResponse:
        """
        Holt Migration-Guide zwischen Versionen.
        
        Args:
            from_version: Ausgangsversion
            to_version: Zielversion
            technology: Technologie-Name
            
        Returns:
            LLMResponse mit Migration-Guide
        """
        topic = f"migration from {from_version} to {to_version}"
        return await self.get_docs_for_library(technology, topic)
    
    async def get_security_docs(self, technology: str) -> LLMResponse:
        """
        Holt Sicherheitsdokumentation für eine Technologie.
        
        Args:
            technology: Technologie-Name
            
        Returns:
            LLMResponse mit Sicherheitsdokumentation
        """
        return await self.get_docs_for_library(technology, "security")
    
    async def get_performance_docs(self, technology: str) -> LLMResponse:
        """
        Holt Performance-Dokumentation für eine Technologie.
        
        Args:
            technology: Technologie-Name
            
        Returns:
            LLMResponse mit Performance-Dokumentation
        """
        return await self.get_docs_for_library(technology, "performance")
    
    async def get_testing_docs(self, technology: str) -> LLMResponse:
        """
        Holt Testing-Dokumentation für eine Technologie.
        
        Args:
            technology: Technologie-Name
            
        Returns:
            LLMResponse mit Testing-Dokumentation
        """
        return await self.get_docs_for_library(technology, "testing")
