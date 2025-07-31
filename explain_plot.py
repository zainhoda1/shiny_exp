import base64
import tempfile

import chatlas
from shiny import ui

INSTRUCTIONS = """
You are analyzing a scatter plot from an automotive dataset dashboard. Your goal is to help users understand patterns in their data and guide them toward actionable insights by suggesting dashboard adjustments.

**Dataset Context:**
- Source: Automotive performance metrics
- Available columns: "Miles per Gallon", "No of cylinders", "Displacement (cu.in.)", "Horsepower", "WEIGHT (1000 lbs)", "1/4 mile time"
- Current state: Reflects any active filters or selections

**Analysis Framework:**
1. **Describe what you observe** - patterns, clusters, outliers, trends
2. **Identify relationships** - correlations, dependencies between variables
3. **Note limitations** - what the current view might be hiding or unclear about
4. **Suggest improvements** - specific dashboard adjustments to reveal deeper insights

**Guidelines:**
- Be specific about patterns you can clearly see
- Express uncertainty when patterns are ambiguous
- Suggest concrete dashboard changes (filters, axis changes, additional variables from the list of available columns)
- Connect observations to automotive domain knowledge when relevant.
""".strip()

counter = 0  # Never re-use the same chat ID


async def explain_plot(
    chat_session: chatlas.Chat,
    plot_widget,  # Can be either Plotly FigureWidget or matplotlib figure wrapper
    plot_type: str = "plot"  # Added parameter to identify plot type
) -> None:
    try:
        with tempfile.TemporaryFile() as f:
            plot_widget.write_image(f)
            f.seek(0)
            img_b64 = base64.b64encode(f.read()).decode("utf-8")
            img_url = f"data:image/png;base64,{img_b64}"

        global counter
        counter += 1
        chat_id = f"explain_plot_chat_{counter}"
        chat = ui.Chat(id=chat_id)

        # TODO: Call chat.destroy() when the modal is dismissed?
        dialog = make_modal_dialog(img_url, ui.chat_ui(id=chat_id, height="100%"))
        ui.modal_show(dialog)

        async def ask(*user_prompt: str | chatlas.types.Content):
            resp = await chat_session.stream_async(*user_prompt)
            await chat.append_message_stream(resp)

        # Ask the initial question
        await ask(INSTRUCTIONS, chatlas.content_image_url(img_url))

        # Allow followup questions
        @chat.on_user_submit
        async def on_user_submit(user_input: str):
            await ask(user_input)

    except Exception as e:
        import traceback

        traceback.print_exc()
        ui.notification_show(str(e), type="error")


def make_modal_dialog(img_url, chat_ui):
    return ui.modal(
        ui.tags.button(
            type="button",
            class_="btn-close d-block ms-auto mb-3",
            data_bs_dismiss="modal",
            aria_label="Close",
        ),
        ui.img(
            src=img_url,
            style="max-width: min(100%, 500px);",
            class_="d-block border mx-auto mb-3",
        ),
        ui.div(
            chat_ui,
            style="overflow-y: auto; max-height: min(60vh, 600px);",
        ),
        size="l",
        easy_close=True,
        title=None,
        footer=None,
    ).add_style("--bs-modal-margin: 1.75rem;")