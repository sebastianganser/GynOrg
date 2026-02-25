#!/usr/bin/env node
import { SimpleMCPServer, UserFacingError } from "./simple-mcp-server.js";
import { promises as fs } from "fs";
import path from "path";
import { fileURLToPath } from "url";
import { randomUUID } from "crypto";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const DATA_DIR = path.join(__dirname, "data");
const TASK_FILE = path.join(DATA_DIR, "taskmaster_tasks.json");

const server = new SimpleMCPServer({
  name: "GynOrg Taskmaster MCP",
  version: "0.1.0",
});

async function ensureDataFile() {
  try {
    await fs.access(TASK_FILE);
  } catch {
    await fs.mkdir(DATA_DIR, { recursive: true });
    const seed = { nextId: 1, tasks: [] };
    await fs.writeFile(TASK_FILE, JSON.stringify(seed, null, 2), "utf8");
  }
}

async function loadData() {
  await ensureDataFile();
  const raw = await fs.readFile(TASK_FILE, "utf8");
  const parsed = JSON.parse(raw);
  return {
    nextId: Number.isInteger(parsed.nextId) ? parsed.nextId : 1,
    tasks: Array.isArray(parsed.tasks) ? parsed.tasks : [],
  };
}

async function saveData(data) {
  await fs.mkdir(DATA_DIR, { recursive: true });
  await fs.writeFile(
    TASK_FILE,
    JSON.stringify({ nextId: data.nextId, tasks: data.tasks }, null, 2),
    "utf8",
  );
}

function normalizeStatus(value) {
  const normalized = String(value || "")
    .trim()
    .toLowerCase();
  if (!normalized) {
    return undefined;
  }
  if (["pending", "todo"].includes(normalized)) {
    return "pending";
  }
  if (["in-progress", "doing", "progress"].includes(normalized)) {
    return "in-progress";
  }
  if (["done", "complete", "completed"].includes(normalized)) {
    return "done";
  }
  return normalized;
}

function serializeTask(task, { includeSubtasks = false } = {}) {
  const base = {
    id: task.id,
    title: task.title,
    status: task.status,
    priority: task.priority,
    description: task.description,
    dependencies: task.dependencies ?? [],
    tag: task.tag ?? null,
    updatedAt: task.updatedAt ?? null,
  };

  if (includeSubtasks) {
    base.subtasks = (task.subtasks ?? []).map((sub) => ({
      id: sub.id,
      title: sub.title,
      status: sub.status,
      description: sub.description,
      parentId: task.id,
    }));
  }

  return base;
}

function findTask(data, id) {
  if (!id) return undefined;
  if (id.includes(".")) {
    const [taskId, subId] = id.split(".");
    const task = data.tasks.find((item) => item.id === taskId);
    if (!task) return undefined;
    const subtask = (task.subtasks ?? []).find((sub) => sub.id === id);
    return subtask ? { task, subtask } : undefined;
  }
  const task = data.tasks.find((item) => item.id === id);
  return task ? { task } : undefined;
}

function parseDependencyInput(input) {
  if (!input) return [];
  if (Array.isArray(input)) {
    return input.map((value) => String(value).trim()).filter(Boolean);
  }
  return String(input)
    .split(",")
    .map((value) => value.trim())
    .filter(Boolean);
}

function asBoolean(value, fallback = false) {
  if (typeof value === "boolean") {
    return value;
  }
  if (typeof value === "number") {
    return value !== 0;
  }
  if (typeof value === "string") {
    const normalized = value.trim().toLowerCase();
    if (["true", "1", "yes", "ja"].includes(normalized)) return true;
    if (["false", "0", "no", "nein"].includes(normalized)) return false;
  }
  return fallback;
}

function asNumber(value, fallback) {
  if (value === null || value === undefined) return fallback;
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : fallback;
}

function formatJson(value) {
  return JSON.stringify(value, null, 2);
}

async function withData(mutator) {
  const data = await loadData();
  const result = await mutator(data);
  if (result?.modified) {
    await saveData(data);
  }
  return result?.payload ?? null;
}

server.addTool({
  name: "get_tasks",
  description: "Gibt alle gespeicherten Tasks zurück.",
  execute: async ({ status, withSubtasks = false, tag }) => {
    const includeSubtasks = asBoolean(withSubtasks, false);
    const payload = await withData(async (data) => {
      const normalizedStatus = normalizeStatus(status);
      const filtered = data.tasks.filter((task) => {
        if (normalizedStatus && task.status !== normalizedStatus) return false;
        if (tag && task.tag !== tag) return false;
        return true;
      });

      return {
        payload: {
          success: true,
          tasks: filtered.map((task) =>
            serializeTask(task, { includeSubtasks }),
          ),
        },
      };
    });

    return formatJson(payload);
  },
});

server.addTool({
  name: "get_task",
  description: "Gibt einen einzelnen Task oder Subtask zurück.",
  execute: async ({ id }) => {
    const payload = await withData(async (data) => {
      const result = findTask(data, id);
      if (!result) {
        throw new UserFacingError(`Task '${id}' wurde nicht gefunden.`);
      }

      if (result.subtask) {
        return {
          payload: {
            success: true,
            task: serializeTask(result.task, { includeSubtasks: true }),
            subtask: {
              id: result.subtask.id,
              title: result.subtask.title,
              status: result.subtask.status,
              description: result.subtask.description,
              parentId: result.task.id,
            },
          },
        };
      }

      return {
        payload: {
          success: true,
          task: serializeTask(result.task, { includeSubtasks: true }),
        },
      };
    });

    return formatJson(payload);
  },
});

server.addTool({
  name: "next_task",
  description: "Liefert den nächsten offenen Task basierend auf Status und Dependencies.",
  execute: async ({ tag }) => {
    const payload = await withData(async (data) => {
      const candidates = data.tasks.filter((task) => {
        if (task.status === "done") return false;
        if (tag && task.tag !== tag) return false;
        const deps = task.dependencies ?? [];
        return deps.every((dependencyId) => {
          const dependency = data.tasks.find((item) => item.id === dependencyId);
          return dependency?.status === "done";
        });
      });

      const next =
        candidates.find((task) => task.status === "pending") ??
        candidates.find((task) => task.status === "in-progress");

      if (!next) {
        return {
          payload: {
            success: true,
            task: null,
            message: "Keine offenen Tasks verfügbar.",
          },
        };
      }

      return {
        payload: {
          success: true,
          task: serializeTask(next, { includeSubtasks: true }),
        },
      };
    });

    return formatJson(payload);
  },
});

server.addTool({
  name: "add_task",
  description: "Fügt einen neuen Task hinzu.",
  execute: async ({ prompt, dependencies, priority = "medium", tag }) => {
    const payload = await withData(async (data) => {
      const id = String(data.nextId++);
      const task = {
        id,
        title: prompt.slice(0, 80),
        description: prompt,
        status: "pending",
        priority,
        dependencies: parseDependencyInput(dependencies),
        tag: tag ?? null,
        subtasks: [],
        updatedAt: new Date().toISOString(),
      };
      data.tasks.push(task);

      return {
        modified: true,
        payload: {
          success: true,
          task: serializeTask(task, { includeSubtasks: true }),
          message: "Task wurde angelegt.",
        },
      };
    });

    return formatJson(payload);
  },
});

server.addTool({
  name: "update_task",
  description: "Aktualisiert einen bestehenden Task.",
  execute: async ({ id, prompt, append = false }) => {
    const shouldAppend = asBoolean(append, false);
    const payload = await withData(async (data) => {
      const result = findTask(data, id);
      if (!result?.task) {
        throw new UserFacingError(`Task '${id}' wurde nicht gefunden.`);
      }

      if (result.subtask) {
        result.subtask.description = shouldAppend
          ? `${result.subtask.description ?? ""}\n\n${prompt}`
          : prompt;
        result.subtask.updatedAt = new Date().toISOString();
      } else {
        result.task.description = shouldAppend
          ? `${result.task.description ?? ""}\n\n${prompt}`
          : prompt;
        result.task.title = prompt.slice(0, 80);
        result.task.updatedAt = new Date().toISOString();
      }

      return {
        modified: true,
        payload: {
          success: true,
          task: serializeTask(result.task, { includeSubtasks: true }),
        },
      };
    });

    return formatJson(payload);
  },
});

server.addTool({
  name: "set_task_status",
  description: "Setzt den Status eines Tasks.",
  execute: async ({ id, status }) => {
    const payload = await withData(async (data) => {
      const normalizedStatus = normalizeStatus(status);
      if (!normalizedStatus) {
        throw new UserFacingError(
          "Status muss 'pending', 'in-progress' oder 'done' sein.",
        );
      }

      const result = findTask(data, id);
      if (!result?.task) {
        throw new UserFacingError(`Task '${id}' wurde nicht gefunden.`);
      }

      if (result.subtask) {
        result.subtask.status = normalizedStatus;
        result.subtask.updatedAt = new Date().toISOString();
      } else {
        result.task.status = normalizedStatus;
        result.task.updatedAt = new Date().toISOString();
      }

      return {
        modified: true,
        payload: {
          success: true,
          task: serializeTask(result.task, { includeSubtasks: true }),
        },
      };
    });

    return formatJson(payload);
  },
});

server.addTool({
  name: "expand_task",
  description: "Erzeugt zusätzliche Subtasks zu einem Task.",
  execute: async ({ id, num, prompt }) => {
    const payload = await withData(async (data) => {
      const result = findTask(data, id);
      if (!result?.task) {
        throw new UserFacingError(`Task '${id}' wurde nicht gefunden.`);
      }
      if (result.subtask) {
        throw new UserFacingError("Subtasks können nicht weiter expandiert werden.");
      }

      const requested = asNumber(num, 2);
      const count = requested > 0 ? requested : 2;
      const subtasks = result.task.subtasks ?? [];
      const basePrefix = `${result.task.id}.`;
      for (let i = 0; i < count; i += 1) {
        const newId = `${basePrefix}${subtasks.length + i + 1}`;
        const title =
          prompt && prompt.trim().length > 0
            ? `${prompt.trim()} (${i + 1})`
            : `Detailaufgabe ${i + 1}`;

        subtasks.push({
          id: newId,
          title,
          status: "pending",
          description:
            "Automatisch generierter Untertask basierend auf expand_task.",
          origin: "auto",
          createdFrom: prompt ?? "auto",
          createdAt: new Date().toISOString(),
        });
      }
      result.task.subtasks = subtasks;
      result.task.updatedAt = new Date().toISOString();

      return {
        modified: true,
        payload: {
          success: true,
          task: serializeTask(result.task, { includeSubtasks: true }),
        },
      };
    });

    return formatJson(payload);
  },
});

server.addTool({
  name: "research",
  description: "Stellt eine mock Recherchierfunktion bereit.",
  execute: async ({
    query,
    taskIds = "",
    customContext = "",
    detailLevel = "medium",
  }) => {
    const curatedTaskIds = parseDependencyInput(taskIds);
    const bulletContext =
      customContext?.trim().length > 0
        ? customContext.trim()
        : "Kein zusätzlicher Kontext angegeben.";

    const payload = {
      success: true,
      research_result: [
        `Analyse (${detailLevel}): ${query}`,
        "• Überprüfe bestehende Implementierungen im Repository.",
        "• Vergleiche mit vorhandenen Tests in tests/ und docs/.",
        "• Leite TODOs für Taskmaster- und Context7-Integration ab.",
      ].join("\n"),
      context: {
        relatedTasks: curatedTaskIds,
        customContext: bulletContext,
      },
      sources: [
        "local://notes/research-checklist.md",
        "local://docs/taskmaster-overview.md",
      ],
    };

    return formatJson(payload);
  },
});

server.addTool({
  name: "analyze_project_complexity",
  description: "Gibt eine einfache Komplexitätsanalyse zurück.",
  execute: async ({ threshold }) => {
    const payload = await withData(async (data) => {
      const stats = data.tasks.reduce(
        (acc, task) => {
          acc.total += 1;
          acc.byStatus[task.status] = (acc.byStatus[task.status] ?? 0) + 1;
          acc.pendingDependencies += (task.dependencies ?? []).length;
          const subtasks = task.subtasks ?? [];
          acc.subtasks += subtasks.length;
          return acc;
        },
        {
          total: 0,
          subtasks: 0,
          pendingDependencies: 0,
          byStatus: {},
        },
      );

      const normalizedThreshold = asNumber(threshold, 5);
      const riskLevel =
        stats.pendingDependencies > normalizedThreshold ||
        stats.byStatus["in-progress"] > normalizedThreshold
          ? "hoch"
          : "moderat";

      return {
        payload: {
          success: true,
          complexity: {
            overview: stats,
            threshold: normalizedThreshold,
            riskLevel,
          },
        },
      };
    });

    return formatJson(payload);
  },
});

server.addTool({
  name: "parse_prd",
  description: "Parst eine lokale PRD-Datei und erzeugt Aufgaben-Vorschläge.",
  execute: async ({ input, numTasks, append = false, tag }) => {
    const appendFlag = asBoolean(append, false);
    const limit = Math.max(1, asNumber(numTasks, 3));
    const absolutePath = path.isAbsolute(input)
      ? input
      : path.resolve(process.cwd(), input);

    let fileContent = "";
    try {
      fileContent = await fs.readFile(absolutePath, "utf8");
    } catch (error) {
      throw new UserFacingError(
        `PRD-Datei konnte nicht gelesen werden: ${(error && error.message) || error}`,
      );
    }

    const lines = fileContent.split(/\r?\n/).filter(Boolean);
    const suggestions = lines.slice(0, limit).map((line, idx) => ({
      id: randomUUID(),
      title: line.slice(0, 100),
      status: "pending",
      priority: "medium",
      tag: tag ?? "prd",
      origin: absolutePath,
      order: idx + 1,
    }));

    const payload = await withData(async (data) => {
      if (!appendFlag) {
        data.tasks = data.tasks.filter((task) => task.tag !== "prd");
      }

      suggestions.forEach((suggestion) => {
        const id = String(data.nextId++);
        data.tasks.push({
          id,
          title: suggestion.title,
          description: `Autogeneriert aus PRD ${path.basename(absolutePath)}`,
          status: suggestion.status,
          priority: suggestion.priority,
          dependencies: [],
          tag: suggestion.tag,
          subtasks: [],
          updatedAt: new Date().toISOString(),
        });
      });

      return {
        modified: true,
        payload: {
          success: true,
          message: `Es wurden ${suggestions.length} Aufgaben-Vorschläge erstellt.`,
          importedFrom: absolutePath,
          createdTasks: suggestions.length,
        },
      };
    });

    return formatJson(payload);
  },
});

server.addResource({
  uri: "taskmaster://tasks",
  name: "Taskmaster Übersicht",
  description: "Aktuelle Taskliste des lokalen Taskmaster-Servers.",
  mimeType: "application/json",
  resolve: async () => {
    const data = await loadData();
    return formatJson({
      generatedAt: new Date().toISOString(),
      taskCount: data.tasks.length,
      tasks: data.tasks.map((task) =>
        serializeTask(task, { includeSubtasks: true }),
      ),
    });
  },
});

server.addResourceTemplate({
  uriTemplate: "taskmaster://task/{taskId}",
  name: "Task Detail",
  description: "Detailinformationen zu einem spezifischen Task.",
  mimeType: "application/json",
  arguments: [
    {
      name: "taskId",
      description: "Task-ID, z.B. 3 oder 3.1",
      required: true,
    },
  ],
  resolve: async ({ taskId }) => {
    const data = await loadData();
    const result = findTask(data, taskId);
    if (!result) {
      throw new UserFacingError(`Task '${taskId}' existiert nicht.`);
    }
    if (result.subtask) {
      return formatJson({
        type: "subtask",
        task: serializeTask(result.task, { includeSubtasks: true }),
        subtask: result.subtask,
      });
    }
    return formatJson({
      type: "task",
      task: serializeTask(result.task, { includeSubtasks: true }),
    });
  },
});

await server.start();
