#!/usr/bin/env node
/**
 * MCP Server for Crypto Intelligence System V10.0-r1
 * Provides integration between Claude and CIS system
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
  GetPromptRequestSchema,
  ListPromptsRequestSchema
} from '@modelcontextprotocol/sdk/types.js';

import fs from 'fs/promises';
import path from 'path';
import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);
const PROJECT_ROOT = process.cwd();

class CISMCPServer {
  constructor() {
    this.server = new Server({
      name: "crypto-intelligence-system",
      version: "10.0.1"
    }, {
      capabilities: {
        tools: {},
        prompts: {}
      }
    });

    this.setupHandlers();
  }

  setupHandlers() {
    // List available tools
    this.server.setRequestHandler(ListToolsRequestSchema, async () => ({
      tools: [
        {
          name: "execute_task",
          description: "Execute a CIS V10 task from TASKS/ACTIVE directory",
          inputSchema: {
            type: "object",
            properties: {
              task_file: {
                type: "string",
                description: "Name of task file in TASKS/ACTIVE/"
              },
              auto_archive: {
                type: "boolean",
                description: "Whether to auto-archive after completion",
                default: true
              }
            },
            required: ["task_file"]
          }
        },
        {
          name: "check_system_status",
          description: "Check current CIS V10 system status and health",
          inputSchema: {
            type: "object",
            properties: {}
          }
        },
        {
          name: "run_financial_cto_check",
          description: "Run Financial CTO task lifecycle check",
          inputSchema: {
            type: "object",
            properties: {
              continuous: {
                type: "boolean",
                description: "Whether to start continuous monitoring",
                default: false
              }
            }
          }
        },
        {
          name: "get_task_status",
          description: "Get status of all tasks or specific task",
          inputSchema: {
            type: "object",
            properties: {
              task_id: {
                type: "string",
                description: "Specific task ID to check (optional)"
              }
            }
          }
        },
        {
          name: "analyze_market_data",
          description: "Run market data analysis using simple_analysis.py",
          inputSchema: {
            type: "object",
            properties: {
              symbol: {
                type: "string",
                description: "Crypto symbol to analyze (e.g., BTCUSDT)",
                default: "BTCUSDT"
              },
              days: {
                type: "number",
                description: "Number of days to analyze",
                default: 30
              }
            }
          }
        },
        {
          name: "validate_system_integrity",
          description: "Validate CIS V10 system integrity and configuration",
          inputSchema: {
            type: "object",
            properties: {}
          }
        }
      ]
    }));

    // Handle tool calls
    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      const { name, arguments: args } = request.params;

      switch (name) {
        case "execute_task":
          return await this.executeTask(args);
        case "check_system_status":
          return await this.checkSystemStatus();
        case "run_financial_cto_check":
          return await this.runFinancialCTOCheck(args);
        case "get_task_status":
          return await this.getTaskStatus(args);
        case "analyze_market_data":
          return await this.analyzeMarketData(args);
        case "validate_system_integrity":
          return await this.validateSystemIntegrity();
        default:
          throw new Error(`Unknown tool: ${name}`);
      }
    });

    // List available prompts
    this.server.setRequestHandler(ListPromptsRequestSchema, async () => ({
      prompts: [
        {
          name: "financial_cto_guidance",
          description: "Get Financial CTO guidance for CIS V10 decisions",
          arguments: [
            {
              name: "scenario",
              description: "The scenario requiring CTO guidance",
              required: true
            }
          ]
        },
        {
          name: "task_analysis",
          description: "Analyze a CIS V10 task and provide implementation guidance",
          arguments: [
            {
              name: "task_content",
              description: "Content of the task to analyze",
              required: true
            }
          ]
        }
      ]
    }));

    // Handle prompt requests
    this.server.setRequestHandler(GetPromptRequestSchema, async (request) => {
      const { name, arguments: args } = request.params;

      switch (name) {
        case "financial_cto_guidance":
          return await this.getFinancialCTOGuidance(args);
        case "task_analysis":
          return await this.getTaskAnalysis(args);
        default:
          throw new Error(`Unknown prompt: ${name}`);
      }
    });
  }

  async executeTask(args) {
    const { task_file, auto_archive = true } = args;

    try {
      // Check if task exists in ACTIVE
      const activeTaskPath = path.join(PROJECT_ROOT, 'TASKS', 'ACTIVE', task_file);
      const taskExists = await fs.access(activeTaskPath).then(() => true).catch(() => false);

      if (!taskExists) {
        return {
          content: [
            {
              type: "text",
              text: `❌ Task file not found: ${task_file}\n\nAvailable tasks:\n${await this.listActiveTasks()}`
            }
          ]
        };
      }

      // Read task content
      const taskContent = await fs.readFile(activeTaskPath, 'utf-8');

      // Find corresponding script
      const taskName = task_file.replace(/\.(md|txt)$/, '').toLowerCase();
      const scriptPath = path.join(PROJECT_ROOT, 'ENGINE', 'scripts', `${taskName}.py`);

      let executionResult = "";

      // Try to execute corresponding script
      try {
        const { stdout, stderr } = await execAsync(`python "${scriptPath}"`, {
          cwd: PROJECT_ROOT
        });
        executionResult = `✅ Script executed successfully:\n${stdout}`;
        if (stderr) {
          executionResult += `\n⚠️ Warnings:\n${stderr}`;
        }
      } catch (error) {
        executionResult = `❌ Script execution failed:\n${error.message}`;
      }

      // Run Financial CTO check if auto_archive enabled
      if (auto_archive) {
        try {
          await execAsync(`python ENGINE/task_lifecycle_manager.py`, {
            cwd: PROJECT_ROOT
          });
          executionResult += `\n🏦 Financial CTO check completed`;
        } catch (error) {
          executionResult += `\n⚠️ Financial CTO check had issues: ${error.message}`;
        }
      }

      return {
        content: [
          {
            type: "text",
            text: `📋 Task Execution Report: ${task_file}\n\n${executionResult}`
          }
        ]
      };

    } catch (error) {
      return {
        content: [
          {
            type: "text",
            text: `❌ Error executing task: ${error.message}`
          }
        ]
      };
    }
  }

  async checkSystemStatus() {
    try {
      // Check MARKET_MIND structure
      const marketMindPath = path.join(PROJECT_ROOT, 'MARKET_MIND');
      const marketMindExists = await fs.access(marketMindPath).then(() => true).catch(() => false);

      let status = "🏦 CIS V10.0-r1 System Status Report\n";
      status += "=" * 50 + "\n\n";

      if (marketMindExists) {
        status += "✅ MARKET_MIND structure: Present\n";

        // Check layers
        const layers = ['LAYER_A_RESEARCH', 'LAYER_B_DATA', 'LAYER_C_KNOWLEDGE',
                       'LAYER_D_MODEL', 'LAYER_E_VALIDATION', 'LAYER_F_FEEDBACK',
                       'LAYER_G_NEWS', 'LAYER_H_INTERFACE'];

        let layersPresent = 0;
        for (const layer of layers) {
          const layerPath = path.join(marketMindPath, layer);
          const exists = await fs.access(layerPath).then(() => true).catch(() => false);
          if (exists) layersPresent++;
        }

        status += `✅ Architecture layers: ${layersPresent}/8 present\n`;

        // Check config files
        const configPath = path.join(marketMindPath, 'CONFIG');
        const configExists = await fs.access(configPath).then(() => true).catch(() => false);
        if (configExists) {
          const configFiles = await fs.readdir(configPath);
          status += `✅ Configuration files: ${configFiles.length} files\n`;
        }
      } else {
        status += "❌ MARKET_MIND structure: Not found\n";
      }

      // Check task system
      const activeTasksPath = path.join(PROJECT_ROOT, 'TASKS', 'ACTIVE');
      const completedTasksPath = path.join(PROJECT_ROOT, 'TASKS', 'COMPLETED');

      try {
        const activeTasks = await fs.readdir(activeTasksPath);
        const completedTasks = await fs.readdir(completedTasksPath);
        status += `📋 Task system: ${activeTasks.length} active, ${completedTasks.length} completed\n`;
      } catch (error) {
        status += "⚠️ Task system: Directory access error\n";
      }

      // Check Financial CTO
      const ctoPath = path.join(PROJECT_ROOT, 'virtual_cto', 'financial_cto.md');
      const ctoExists = await fs.access(ctoPath).then(() => true).catch(() => false);
      status += `🏦 Financial CTO: ${ctoExists ? 'Integrated' : 'Missing'}\n`;

      return {
        content: [
          {
            type: "text",
            text: status
          }
        ]
      };

    } catch (error) {
      return {
        content: [
          {
            type: "text",
            text: `❌ Error checking system status: ${error.message}`
          }
        ]
      };
    }
  }

  async runFinancialCTOCheck(args) {
    const { continuous = false } = args;

    try {
      const command = continuous
        ? `python -c "from ENGINE.task_lifecycle_manager import TaskLifecycleManager; manager = TaskLifecycleManager(); manager.start_continuous_monitoring(60)"`
        : `python ENGINE/task_lifecycle_manager.py`;

      const { stdout, stderr } = await execAsync(command, {
        cwd: PROJECT_ROOT
      });

      let result = `🏦 Financial CTO Check Results:\n\n${stdout}`;
      if (stderr) {
        result += `\n⚠️ Warnings:\n${stderr}`;
      }

      return {
        content: [
          {
            type: "text",
            text: result
          }
        ]
      };

    } catch (error) {
      return {
        content: [
          {
            type: "text",
            text: `❌ Financial CTO check failed: ${error.message}`
          }
        ]
      };
    }
  }

  async getTaskStatus(args) {
    try {
      const taskLogPath = path.join(PROJECT_ROOT, 'HISTORY', 'task_log.json');
      const taskLogExists = await fs.access(taskLogPath).then(() => true).catch(() => false);

      if (!taskLogExists) {
        return {
          content: [
            {
              type: "text",
              text: "❌ Task log not found. System may not be initialized."
            }
          ]
        };
      }

      const taskLogContent = await fs.readFile(taskLogPath, 'utf-8');
      const taskLog = JSON.parse(taskLogContent);

      let status = "📊 CIS V10 Task Status Report\n";
      status += "=" * 40 + "\n\n";

      const stats = taskLog.statistics || {};
      status += `📈 Statistics:\n`;
      status += `   Total tasks: ${stats.total_tasks || 0}\n`;
      status += `   Active tasks: ${stats.active_tasks || 0}\n`;
      status += `   Completed tasks: ${stats.completed_tasks || 0}\n`;
      status += `   Failed tasks: ${stats.failed_tasks || 0}\n\n`;

      if (args.task_id) {
        // Show specific task
        const task = taskLog.tasks?.find(t => t.task_id === args.task_id);
        if (task) {
          status += `🔍 Task Details: ${args.task_id}\n`;
          status += `   Name: ${task.task_name || 'Unknown'}\n`;
          status += `   Status: ${task.status || 'Unknown'}\n`;
          status += `   Created: ${task.created || 'Unknown'}\n`;
          if (task.completed_time) {
            status += `   Completed: ${task.completed_time}\n`;
          }
        } else {
          status += `❌ Task ${args.task_id} not found\n`;
        }
      } else {
        // Show all tasks
        if (taskLog.tasks && taskLog.tasks.length > 0) {
          status += "📋 All Tasks:\n";
          for (const task of taskLog.tasks) {
            const statusIcon = task.status === 'COMPLETED' ? '✅' :
                             task.status === 'REGISTERED' ? '📝' : '❓';
            status += `   ${statusIcon} ${task.task_id}: ${task.task_name} (${task.status})\n`;
          }
        }
      }

      return {
        content: [
          {
            type: "text",
            text: status
          }
        ]
      };

    } catch (error) {
      return {
        content: [
          {
            type: "text",
            text: `❌ Error getting task status: ${error.message}`
          }
        ]
      };
    }
  }

  async analyzeMarketData(args) {
    const { symbol = "BTCUSDT", days = 30 } = args;

    try {
      const { stdout, stderr } = await execAsync(`python simple_analysis.py --symbol ${symbol} --days ${days}`, {
        cwd: PROJECT_ROOT
      });

      let result = `📊 Market Analysis Results for ${symbol} (${days} days):\n\n${stdout}`;
      if (stderr) {
        result += `\n⚠️ Warnings:\n${stderr}`;
      }

      return {
        content: [
          {
            type: "text",
            text: result
          }
        ]
      };

    } catch (error) {
      return {
        content: [
          {
            type: "text",
            text: `❌ Market analysis failed: ${error.message}`
          }
        ]
      };
    }
  }

  async validateSystemIntegrity() {
    try {
      let report = "🔍 CIS V10.0-r1 System Integrity Validation\n";
      report += "=" * 50 + "\n\n";

      // Check critical paths
      const criticalPaths = [
        'MARKET_MIND',
        'MARKET_MIND/CONFIG',
        'TASKS/ACTIVE',
        'TASKS/COMPLETED',
        'ENGINE/scripts',
        'HISTORY',
        'virtual_cto'
      ];

      for (const pathToCheck of criticalPaths) {
        const fullPath = path.join(PROJECT_ROOT, pathToCheck);
        const exists = await fs.access(fullPath).then(() => true).catch(() => false);
        const status = exists ? '✅' : '❌';
        report += `${status} ${pathToCheck}\n`;
      }

      // Check critical files
      const criticalFiles = [
        'MARKET_MIND/CONFIG/system_manifest.json',
        'HISTORY/task_log.json',
        'virtual_cto/financial_cto.md',
        'ENGINE/task_lifecycle_manager.py'
      ];

      report += "\n📄 Critical Files:\n";
      for (const fileToCheck of criticalFiles) {
        const fullPath = path.join(PROJECT_ROOT, fileToCheck);
        const exists = await fs.access(fullPath).then(() => true).catch(() => false);
        const status = exists ? '✅' : '❌';
        report += `${status} ${fileToCheck}\n`;
      }

      return {
        content: [
          {
            type: "text",
            text: report
          }
        ]
      };

    } catch (error) {
      return {
        content: [
          {
            type: "text",
            text: `❌ System integrity validation failed: ${error.message}`
          }
        ]
      };
    }
  }

  async listActiveTasks() {
    try {
      const activeTasksPath = path.join(PROJECT_ROOT, 'TASKS', 'ACTIVE');
      const tasks = await fs.readdir(activeTasksPath);
      return tasks.filter(f => f.endsWith('.md')).join('\n- ') || 'No active tasks';
    } catch {
      return 'Unable to list tasks';
    }
  }

  async getFinancialCTOGuidance(args) {
    const { scenario } = args;

    const guidance = `
🏦 Financial CTO Guidance for CIS V10.0-r1

Scenario: ${scenario}

Decision Framework:
1. 📊 Data Quality First - Ensure all inputs meet 6 Quality Gates
2. 🔍 Model Observability - Can we trace prediction failures?
3. 💰 Financial Risk Safety - Uncertainty calibration and shock detection
4. 📋 Regulatory Compliance - Full audit trail requirements
5. ⚡ Performance - Fast Lane ≤200ms non-negotiable

Risk Assessment:
- Check for stale data (>5min penalty)
- Validate regime consistency (R1-R6 modes)
- Monitor shock score trends
- Ensure conformal UQ coverage

Recommendations:
- Apply graduated brake if shock_score > 0.3
- Expand uncertainty intervals for stale data
- Use PI-lite control for non-stationary markets
- Maintain deterministic contract for reproducibility

Next Actions:
1. Validate current system state
2. Check deliverable requirements
3. Update task tracking system
4. Apply Financial CTO quality gates
`;

    return {
      content: [
        {
          type: "text",
          text: guidance
        }
      ]
    };
  }

  async getTaskAnalysis(args) {
    const { task_content } = args;

    const analysis = `
📋 CIS V10 Task Analysis

Task Content Analysis:
${task_content.substring(0, 500)}...

Financial CTO Assessment:
✅ Deliverable Requirements - Check for specific outputs
✅ Risk Level - Evaluate potential system impact
✅ Dependencies - Identify prerequisite tasks
✅ Quality Gates - Define validation criteria
✅ Performance Impact - Fast Lane compatibility

Implementation Guidance:
1. Create corresponding script in ENGINE/scripts/
2. Define clear deliverables for auto-detection
3. Add appropriate logging for audit trail
4. Include error handling and rollback capabilities
5. Test integration with existing 8-layer architecture

Quality Assurance:
- Validate against market axioms (AXM_001-AXM_009)
- Check structural priors (PRI_001-PRI_019)
- Ensure TRIZ contradiction resolution
- Verify conformal UQ compliance
`;

    return {
      content: [
        {
          type: "text",
          text: analysis
        }
      ]
    };
  }

  async run() {
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
    console.error("🏦 CIS V10.0-r1 MCP Server running...");
  }
}

// Start the server
const server = new CISMCPServer();
server.run().catch(console.error);