#!/usr/bin/env node
import { SimpleMCPServer, UserFacingError } from "./simple-mcp-server.js";
import { promises as fs } from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const DATA_DIR = path.join(__dirname, "data");
const DOCS_FILE = path.join(DATA_DIR, "context7_docs.json");

const server = new SimpleMCPServer({
  name: "GynOrg Context7 MCP",
  version: "0.1.0",
});

async function ensureDocsFile() {
  try {
    await fs.access(DOCS_FILE);
  } catch {
    throw new Error(
      "context7_docs.json wurde nicht gefunden. Bitte Repository-Struktur prüfen.",
    );
  }
}

async function loadDocs() {
  await ensureDocsFile();
  const raw = await fs.readFile(DOCS_FILE, "utf8");
  const parsed = JSON.parse(raw);
  return Array.isArray(parsed.libraries) ? parsed.libraries : [];
}

function normalize(text) {
  return String(text || "").toLowerCase();
}

function matchScore(input, target) {
  if (!input || !target) return 0;
  const normalizedInput = normalize(input);
  const normalizedTarget = normalize(target);
  if (normalizedInput === normalizedTarget) return 5;
  if (normalizedTarget.includes(normalizedInput)) return 4;
  if (normalizedInput.includes(normalizedTarget)) return 3;
  return 0;
}

function findLibraries(libraries, query) {
  if (!query) return libraries;
  const normalized = normalize(query);
  const ranked = libraries
    .map((library) => {
      const nameScore = matchScore(normalized, library.name);
      const aliasScore = Math.max(
        0,
        ...(library.aliases ?? []).map((alias) => matchScore(normalized, alias)),
      );
      const totalScore = Math.max(nameScore, aliasScore);
      return { library, score: totalScore };
    })
    .filter((entry) => entry.score > 0)
    .sort((a, b) => b.score - a.score);
  return ranked.map((entry) => entry.library);
}

function formatLibrary(library) {
  return {
    id: library.id,
    name: library.name,
    description: library.summary,
    aliases: library.aliases ?? [],
    availableTopics: Object.keys(library.topics ?? {}),
  };
}

server.addTool({
  name: "resolve-library-id",
  description: "Führt eine Suche nach Context7-kompatiblen Libraries aus.",
  execute: async ({ libraryName }) => {
    const libraries = await loadDocs();
    const matches = findLibraries(libraries, libraryName);
    if (matches.length === 0) {
      return JSON.stringify(
        {
          success: true,
          library_id: null,
          matches: [],
          message: `Keine Bibliothek für '${libraryName}' gefunden.`,
        },
        null,
        2,
      );
    }

    return JSON.stringify(
      {
        success: true,
        library_id: matches[0].id,
        matches: matches.slice(0, 5).map(formatLibrary),
      },
      null,
      2,
    );
  },
});

server.addTool({
  name: "get-library-docs",
  description: "Liefert hinterlegte Dokumentation und Beispiele.",
  execute: async ({ context7CompatibleLibraryID, topic }) => {
    const libraries = await loadDocs();
    const library = libraries.find(
      (entry) => entry.id === context7CompatibleLibraryID,
    );
    if (!library) {
      throw new UserFacingError(
        `Bibliothek '${context7CompatibleLibraryID}' ist nicht hinterlegt.`,
      );
    }

    const topics = library.topics ?? {};
    let selectedTopic = "overview";
    if (topic) {
      const normalizedTopic = normalize(topic);
      const match = Object.keys(topics).find(
        (key) => normalize(key) === normalizedTopic,
      );
      if (match) {
        selectedTopic = match;
      } else {
        const partial = Object.keys(topics).find((key) =>
          normalize(key).includes(normalizedTopic),
        );
        selectedTopic = partial ?? selectedTopic;
      }
    }

    const documentation =
      topics[selectedTopic] ??
      library.summary ??
      "Keine Dokumentation verfügbar.";

    return JSON.stringify(
      {
        success: true,
        library: formatLibrary(library),
        topic: selectedTopic,
        documentation,
        examples: library.examples ?? [],
      },
      null,
      2,
    );
  },
});

server.addResource({
  uri: "context7://libraries",
  name: "Verfügbare Context7 Libraries",
  mimeType: "application/json",
  description: "Auflistung aller lokal hinterlegten Context7-Bibliotheken.",
  resolve: async () => {
    const libraries = await loadDocs();
    return JSON.stringify(
      {
        generatedAt: new Date().toISOString(),
        libraries: libraries.map(formatLibrary),
      },
      null,
      2,
    );
  },
});

server.addResourceTemplate({
  uriTemplate: "context7://library/{name}",
  name: "Context7 Library Detail",
  mimeType: "application/json",
  description: "Details und Dokumentation zu einer bestimmten Library.",
  arguments: [
    {
      name: "name",
      description: "Name oder ID einer Library, z.B. react oder /docs/react",
      required: true,
    },
  ],
  resolve: async ({ name }) => {
    const libraries = await loadDocs();
    const normalized = normalize(name);
    const library =
      libraries.find((entry) => normalize(entry.id) === normalized) ??
      libraries.find((entry) => normalize(entry.name) === normalized);

    if (!library) {
      throw new UserFacingError(`Library '${name}' konnte nicht gefunden werden.`);
    }

    return JSON.stringify(
      {
        library: formatLibrary(library),
        documentation: library.topics ?? {},
        examples: library.examples ?? [],
      },
      null,
      2,
    );
  },
});

await server.start();
