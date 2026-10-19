# Mini-project 1: My Workspace + MCP

A small **personal workspace** with editable tasks, quick notes, and real
weather data. Complete **three integration lines**, then improve **one design
file** manually, with an AI coding assistant, or using both.
No algorithms, database, account, or API key are needed.

The connection is: **workspace → MCP client → MCP server → weather HTTP API**.
The server calls a real external API; it does not return mock weather.
The page code can be generated with AI during design iteration. This lightweight
app does not generate pages at runtime.

## Start

Install **Python 3.10 or newer**:

```bash
git clone https://github.com/jinghan-yu/genui-mini-project1.git
cd genui-mini-project1
python -m venv .venv
```

Activate the environment:

- macOS / Linux: `source .venv/bin/activate`
- Windows PowerShell: `.venv\Scripts\Activate.ps1`
- Windows Command Prompt: `.venv\Scripts\activate.bat`

```bash
python -m pip install -r requirements.txt
python -m streamlit run main.py
```

Open [localhost:8501](http://localhost:8501). Tasks and notes work immediately.
Weather displays a TODO message until you complete the integration.
The MCP server starts automatically; one terminal is enough.

## Your task

1. **Connect weather.** Read the tool in `mcp_server.py`. Complete the three
   `# TODO` lines in `main.py`: the tool name, the selected city's argument,
   and `await session.call_tool(tool_name, arguments)`. Save and reload.
   Switch cities and confirm that the weather panel changes.
2. **Improve your workspace.** Take a baseline screenshot. Edit only `design.py`
   to improve hierarchy, layout, and visual consistency. You can change the
   Streamlit layout, CSS, and HTML directly. If using AI, edit `DESIGN_PROMPT`
   and send it with this file to your assistant. The prompt alone does not
   change the page.
3. **Check the result.** Edit tasks, mark one done, save notes, and reload.
   Check the weather refresh button and a narrow window. Preserve the function
   signatures, working controls, weather values, and source attribution.

## Submit

- Completed `main.py` and improved `design.py`.
- Before and after screenshots at the same window width and selected city.
- A short explanation (100–150 words) of your changes and usability checks.
  Include before and after prompts if using AI; describe code changes if editing manually.

Manual and AI-assisted work use the same criteria: a working MCP connection,
clear design, and a reasoned comparison.

## Files and data

| File | Purpose |
| --- | --- |
| `main.py` | MCP connection, weather cache, and local saving; three TODOs |
| `mcp_server.py` | Complete API list, automatic fallback, and provider cache |
| `design.py` | All page layout, controls, styling, and optional design prompts |

Tasks and notes are saved in `.workspace.json` beside the app, excluded from Git.
This is a local, single-user workspace; it has no login or cloud syncing.
Internet access is required for weather. The server tries `API_LIST` in order:
**MET Norway, then Open-Meteo**. Timeouts, HTTP errors (including rate limits),
or invalid responses trigger the next provider. The panel shows the actual source,
units, and forecast/estimate time in UTC. If both fail, tasks and notes still work.

The page caches results for 10 minutes. The server also saves `.weather-cache.json`
(excluded from Git): MET Norway data stays cached until the API's `Expires` time
and uses `If-Modified-Since` when checking again; Open-Meteo uses a 10-minute cache.
Refresh calls MCP again, but may reuse valid cached data to respect API limits.

## Open source and API use

Our code uses the [MIT license](LICENSE), including the MCP adapter. The
[official MCP SDK](https://github.com/modelcontextprotocol/python-sdk/tree/v1.26.0)
uses MIT, [Streamlit](https://github.com/streamlit/streamlit) uses Apache 2.0,
and [HTTPX](https://github.com/encode/httpx) uses BSD 3-Clause.

Both APIs work without keys. [MET Norway](https://api.met.no/doc/TermsOfService)
provides public forecasts and requires an identifying User-Agent and caching.
[Open-Meteo's free API](https://open-meteo.com/en/terms) supports noncommercial
use subject to request limits. Keep the actual provider's visible credit and
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) link when redesigning.
Code licensing and third-party API terms are separate. See
[MET Norway's data license](https://api.met.no/doc/License) before reusing its data.
