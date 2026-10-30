"""The whole workspace design. Edit manually or with an optional AI assistant."""
from html import escape

import pandas as pd
import streamlit as st
from pathlib import Path
import base64

CITY_IMAGES = {
    "Shanghai": "shanghai.png",
    "Beijing": "beijing.png",
    "London": "london.png",
    "New York": "new_york.png",
}



BASELINE_PROMPT = "Create a personal workspace with tasks, quick notes, and a weather panel."
# Optional: send this prompt and this file to an AI coding assistant.
# Manual editing is equally valid. Changing the prompt alone does not change the UI.
DESIGN_PROMPT = """
Improve this personal daily workspace by editing only design.py.
Keep controls() returning (city, refresh), message(text, error=False), and
render(weather, workspace, weather_message) returning saved edits or None.
Keep the task editor, notes, save button, city selector, and weather refresh.
Make the hierarchy, spacing, and colors consistent and the page usable on phones.
Keep weather values and the actual API's visible attribution. Use Streamlit and HTML/CSS.
Do not add dependencies, API calls, or algorithms.
"""

# All colors, spacing, and weather markup can be changed in this file.
STYLE = """
<style>
.block-container { max-width: 1120px; padding-top: 3rem; }
.weather { background: #edf5ff; color: #18304d; border-radius: 16px; padding: 24px; }
.weather h3 { margin: 0 0 16px; color: #18304d; }
.temperature { font-size: 52px; font-weight: 650; line-height: 1.2; }
.weather p { margin: 12px 0; }
.weather small { color: #405872; }

.weather--photo {
    padding: 0;
    overflow: hidden;
    background-size: cover;
    background-position: center;
}

.weather--photo .weather-details {
    padding: 24px;
    background: rgba(237, 245, 255, 0.75);
    -webkit-backdrop-filter: blur(1px);
    backdrop-filter: blur(1px);
}
</style>
"""
CONDITIONS = {
    0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Fog", 48: "Rime fog", 51: "Light drizzle", 53: "Drizzle", 55: "Heavy drizzle",
    56: "Freezing drizzle", 57: "Freezing drizzle", 61: "Light rain", 63: "Rain", 65: "Heavy rain",
    66: "Freezing rain", 67: "Freezing rain", 71: "Light snow", 73: "Snow", 75: "Heavy snow",
    77: "Snow grains", 80: "Rain showers", 81: "Rain showers", 82: "Heavy showers",
    85: "Snow showers", 86: "Heavy snow showers", 95: "Thunderstorm",
    96: "Thunderstorm with hail", 99: "Thunderstorm with hail",
}


def controls():
    st.set_page_config(page_title="My Workspace", page_icon="☀️", layout="wide")
    st.html(STYLE)
    title, settings = st.columns([3, 1])
    with title:
        st.title("My workspace")
        st.caption("A place for today's tasks, quick notes, and the weather outside.")
    with settings:
        city = st.selectbox("Weather city", ["Shanghai", "Beijing", "London", "New York"])
        refresh = st.button("Refresh weather")
    return city, refresh


def message(text, error=False):
    if error:
        st.error(text)
    else:
        st.success(text)


def render(weather, workspace, weather_message):
    personal, live_tools = st.columns([2, 1], gap="large")
    with personal, st.form("workspace"):
        st.subheader("Today's tasks")
        st.caption("Edit a task, tick Done, or use the empty row to add one. Save your edits below.")
        table = pd.DataFrame(workspace["tasks"], columns=["done", "task"]).astype({"done": "bool", "task": "str"})
        tasks = st.data_editor(
            table, num_rows="dynamic", hide_index=True, width="stretch",
            column_order=["done", "task"], key="task_editor",
            column_config={
                "done": st.column_config.CheckboxColumn("Done", default=False),
                "task": st.column_config.TextColumn("Task", required=True),
            },
        )
        st.subheader("Quick notes")
        notes = st.text_area("Notes", value=workspace["notes"], height=170, key="notes", label_visibility="collapsed")
        saved = st.form_submit_button("Save workspace", type="primary")
    with live_tools:
        st.subheader("Weather")
        if weather is None:
            st.info(weather_message or "Choose a city to load weather.")
        else:
            card_class = "weather"
            image_style = ""

            filename = CITY_IMAGES.get(weather["city"])

            if filename:
                image_path = Path(__file__).parent / "images" / filename

                try:
                    image_data = image_path.read_bytes()
                except OSError:
                    pass  # Missing or unreadable image: keep the blue card.
                else:
                    encoded = base64.b64encode(image_data).decode("ascii")
                    card_class = "weather weather--photo"
                    image_style = (
                        f' style="background-image: '
                        f'url(data:image/png;base64,{encoded});"'
                    )

            # Keep escaping data from the external API when changing this HTML.
            item = {key: escape(str(value)) for key, value in weather.items()}
            condition = CONDITIONS.get(weather.get("weather_code"), weather.get("condition", "Weather"))
            condition = escape(condition.replace("_", " ").replace("clearsky", "clear sky")
                               .replace("partlycloudy", "partly cloudy").capitalize())
            st.html(f"""
            <section class="{card_class}"{image_style}
                     aria-label="Weather estimate">
              <div class="weather-details">
                <h3>{item['city']}</h3>
                <div class="temperature">{item['temperature']}°C</div>
                <p>{condition}</p>
                <p>Humidity {item['humidity']}% · Wind {item['wind_speed']} m/s</p>
                <small>{item['kind']}<br>Time (UTC): {item['time']}</small>
              </div>
            </section>
            """)
            st.caption(f"Weather data from [{weather['source']}]({weather['source_url']}), "
                       "[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).")
        st.caption("Tries MET Norway, then Open-Meteo. Refresh may reuse a valid API cache.")
    return {"tasks": tasks.to_dict("records"), "notes": notes} if saved else None
