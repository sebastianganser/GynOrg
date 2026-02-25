#!/usr/bin/env node
/**
 * Minimal MCP server implementation for local development.
 * Supports initialize, tools/list, tools/call, resources/list and resources/read.
 */
export class UserFacingError extends Error {
  constructor(message) {
    super(message);
    this.name = "UserFacingError";
  }
}

export class SimpleMCPServer {
  constructor({ name, version }) {
    this.info = { name, version };
    this.tools = [];
    this.resources = [];
    this.resourceTemplates = [];
    this.clientCapabilities = {};
    this.initialized = false;
    this.buffer = "";
    this.expectedContentLength = null;
  }

  addTool({ name, description, handler, schema }) {
    this.tools.push({
      name,
      description,
      handler,
      schema: schema ?? { type: "object", properties: {} },
    });
  }

  addResource({ uri, name, description, mimeType = "text/plain", resolve }) {
    this.resources.push({
      uri,
      name,
      description,
      mimeType,
      resolve,
    });
  }

  addResourceTemplate(template) {
    this.resourceTemplates.push(template);
  }

  async start() {
    process.stdin.setEncoding("utf8");
    process.stdin.on("data", (chunk) => this.#handleChunk(chunk));
    process.stdin.on("error", (error) => {
      console.error("STDIN error:", error);
      process.exit(1);
    });
    process.stdin.resume();
    return new Promise(() => {});
  }

  #handleChunk(chunk) {
    this.buffer += chunk;
    // Process headers and payload sequentially
    while (true) {
      if (this.expectedContentLength === null) {
        const headerEnd = this.buffer.indexOf("\r\n\r\n");
        if (headerEnd === -1) {
          return;
        }

        const header = this.buffer.slice(0, headerEnd);
        this.buffer = this.buffer.slice(headerEnd + 4);
        const lengthMatch = header.match(/content-length:\s*(\d+)/i);
        if (!lengthMatch) {
          console.error("Invalid MCP header, missing Content-Length");
          continue;
        }
        this.expectedContentLength = parseInt(lengthMatch[1], 10);
      }

      if (this.buffer.length < this.expectedContentLength) {
        return;
      }

      const message = this.buffer.slice(0, this.expectedContentLength);
      this.buffer = this.buffer.slice(this.expectedContentLength);
      this.expectedContentLength = null;

      try {
        const parsed = JSON.parse(message);
        this.#handleMessage(parsed);
      } catch (error) {
        console.error("Failed to parse MCP message:", error);
      }
    }
  }

  async #handleMessage(message) {
    if (message.method) {
      await this.#handleRequest(message);
      return;
    }

    // Notifications without method are ignored
  }

  async #handleRequest(request) {
    const { method, id, params } = request;
    try {
      switch (method) {
        case "initialize":
          this.clientCapabilities = params?.capabilities ?? {};
          this.initialized = true;
          this.#respond(id, {
            serverInfo: this.info,
            capabilities: this.#buildCapabilities(),
          });
          break;
        case "notifications/initialized":
          break;
        case "ping":
          this.#respond(id, {});
          break;
        case "tools/list":
          this.#respond(id, {
            tools: this.tools.map((tool) => ({
              name: tool.name,
              description: tool.description,
              inputSchema: tool.schema,
            })),
          });
          break;
        case "tools/call": {
          const toolName = params?.name;
          const tool = this.tools.find((entry) => entry.name === toolName);
          if (!tool) {
            throw new UserFacingError(`Tool '${toolName}' ist nicht verfügbar.`);
          }
          const rawResult = await tool.handler(params?.arguments ?? {});
          const textResult =
            typeof rawResult === "string"
              ? rawResult
              : JSON.stringify(rawResult, null, 2);
          this.#respond(id, {
            content: [
              {
                type: "text",
                text: textResult,
              },
            ],
          });
          break;
        }
        case "resources/list":
          this.#respond(id, {
            resources: this.resources.map((resource) => ({
              uri: resource.uri,
              name: resource.name,
              description: resource.description,
              mimeType: resource.mimeType,
            })),
          });
          break;
        case "resources/read": {
          const uri = params?.uri;
          const resource = this.resources.find((entry) => entry.uri === uri);
          if (!resource) {
            throw new UserFacingError(`Resource '${uri}' wurde nicht gefunden.`);
          }
          const content = await resource.resolve(params ?? {});
          this.#respond(id, {
            contents: [
              {
                type: "text",
                text:
                  typeof content === "string"
                    ? content
                    : JSON.stringify(content, null, 2),
                mimeType: resource.mimeType,
              },
            ],
          });
          break;
        }
        case "resources/templates/list":
          this.#respond(id, {
            resourceTemplates: this.resourceTemplates.map((template) => ({
              uriTemplate: template.uriTemplate,
              name: template.name,
              description: template.description,
              mimeType: template.mimeType ?? "text/plain",
              arguments: template.arguments ?? [],
            })),
          });
          break;
        case "resources/templates/read": {
          const uri = params?.uri;
          const template = this.resourceTemplates.find(
            (entry) => entry.uriTemplate === uri,
          );
          if (!template) {
            throw new UserFacingError(
              `Resource Template '${uri}' wurde nicht gefunden.`,
            );
          }
          const args = params?.arguments ?? {};
          const content = await template.resolve(args);
          this.#respond(id, {
            contents: [
              {
                type: "text",
                text:
                  typeof content === "string"
                    ? content
                    : JSON.stringify(content, null, 2),
                mimeType: template.mimeType ?? "text/plain",
              },
            ],
          });
          break;
        }
        default:
          this.#respondError(id, -32601, `Unsupported method: ${method}`);
      }
    } catch (error) {
      if (error instanceof UserFacingError) {
        this.#respondError(id, -32001, error.message);
      } else {
        console.error("Internal MCP error:", error);
        this.#respondError(id, -32603, "Internal error");
      }
    }
  }

  #buildCapabilities() {
    const capabilities = {};
    if (this.tools.length > 0) {
      capabilities.tools = {};
    }
    if (this.resources.length > 0) {
      capabilities.resources = {};
    }
    if (this.resourceTemplates.length > 0) {
      capabilities.resourceTemplates = {};
    }
    return capabilities;
  }

  #respond(id, result) {
    if (id === undefined || id === null) {
      return;
    }
    this.#send({
      jsonrpc: "2.0",
      id,
      result,
    });
  }

  #respondError(id, code, message) {
    if (id === undefined || id === null) {
      return;
    }
    this.#send({
      jsonrpc: "2.0",
      id,
      error: {
        code,
        message,
      },
    });
  }

  #send(payload) {
    const body = JSON.stringify(payload);
    const header = `Content-Length: ${Buffer.byteLength(body, "utf8")}\r\n\r\n`;
    process.stdout.write(header);
    process.stdout.write(body);
  }
}

