"""Provided app plumbing. Students complete only the three integration TODOs."""
import asyncio
import json
import logging
import sys
from datetime import timedelta
from pathlib import Path

import streamlit as st
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

import design

WORKSPACE_FILE = Path(__file__).with_name(".workspace.json")


async def load_weather(city):
    server = StdioServerParameters(
        command=sys.executable,
        args=[str(Path(__file__).with_name("mcp_server.py"))],
    )
    async with stdio_client(server) as (read, write):
        async with ClientSession(read, write, read_timeout_seconds=timedelta(seconds=20)) as session:
            await session.initialize()

            # TODO 1: Set the tool name. Find it in mcp_server.py.
            tool_name = ""
            # TODO 2: Pass the selected city using the tool's parameter name.
            arguments = {}
            # TODO 3: Call the tool with session.call_tool(tool_name, arguments).
            result = None

    if result is None:
        raise NotImplementedError("Complete the three TODO lines in main.py to connect weather.")
    if result.isError:
        raise RuntimeError(result.content)
    return result.structuredContent


@st.cache_data(ttl=600, show_spinner=False)
def get_weather(city):
    return asyncio.run(load_weather(city))


def read_workspace():
    if WORKSPACE_FILE.exists():
        return json.loads(WORKSPACE_FILE.read_text(encoding="utf-8"))
    return {"tasks": [{"done": False, "task": "Choose today's main task"}], "notes": ""}


def save_workspace(workspace):
    temporary = WORKSPACE_FILE.with_suffix(".tmp")
    temporary.write_text(json.dumps(workspace, ensure_ascii=False, indent=2), encoding="utf-8")
    temporary.replace(WORKSPACE_FILE)


def main():
    city, refresh = design.controls()
    if refresh:
        get_weather.clear(city)
    weather, weather_message = None, None
    try:
        weather = get_weather(city)
    except NotImplementedError as error:
        weather_message = str(error)
    except Exception:
        weather_message = "Weather unavailable. Check your connection or try refreshing later."
        logging.exception("Weather MCP/API request failed")
    try:
        workspace = read_workspace()
    except (OSError, ValueError):
        design.message("Cannot read .workspace.json. Check the file before saving any changes.", error=True)
        return
    updated = design.render(weather, workspace, weather_message)
    if updated is not None:
        try:
            save_workspace(updated)
            design.message("Workspace saved on this computer.")
        except OSError:
            design.message("Cannot save the workspace. Check folder permissions.", error=True)


if __name__ == "__main__":
    main()
