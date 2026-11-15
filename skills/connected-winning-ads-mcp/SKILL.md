---
name: connected-winning-ads-mcp
description: >-
  Provides the architecture and specification for building an MCP (Model Context Protocol) server to dynamically pull winning ad data from external platforms (e.g., Meta Ads Library, Foreplay.co).
---

# Connected Winning Ads MCP Spec

## Overview
This is a specification skill. Use this when the user wants to connect their AI agent to live ad performance data. An MCP server allows the agent to fetch "winning ads" in real-time.

## Workflow

### 1. Requirements Gathering
To build a `connected-winning-ads-mcp`, the user needs:
- Access to a platform API (like Facebook Ads API, Foreplay.co API, or a scraping service).
- A Node.js or Python environment to host the MCP server.

### 2. Proposed MCP Tools
When instructing the user or generating the MCP code, ensure it exposes the following tools to the agent:
- `search_ads(keyword, platform)`: Returns a list of active ads matching the keyword.
- `get_ad_details(ad_id)`: Returns the ad copy, media URL, and time active (a proxy for performance).
- `analyze_competitor(domain)`: Returns the top active creatives for a specific competitor.

### 3. Implementation Steps
If the user asks to build this:
1. Create a standard MCP server boilerplate (e.g., using `@modelcontextprotocol/sdk`).
2. Implement the authentication for the chosen Ads API.
3. Define the tool handlers.
4. Add the server to the `mcp_config.json` so the agent can use it locally.

*(Note: This skill provides the blueprint. To execute it, switch to a coding workflow to actually write the MCP server).*
