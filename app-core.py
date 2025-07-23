import seaborn as sns
import matplotlib.pyplot as plt
from faicons import icon_svg
from chatlas import ChatAnthropic
from dotenv import load_dotenv
import plotly.express as px
import faicons as fa
from shiny import App, reactive, render, ui
from shinywidgets import output_widget, render_plotly

# Import data from shared.py
from shared import app_dir, df
# Import plot explanation functionality
from explain_plot import explain_plot
from shiny import App, reactive, render, ui
from pathlib import Path
import pandas as pd
import numpy as np
from ridgeplot import ridgeplot
import matplotlib.pyplot as plt
import uuid

# Prepare the data
print(Path(__file__).parent)
location = Path(__file__).parent
file_name = 'mtcars.csv'
image_file_path = location / file_name
df1 = pd.read_csv(image_file_path)

column_mapping = {
    "mpg": "Miles per Gallon",
    "cyl": "No of cylinders", 
    "disp": "Displacement (cu.in.)",
    "hp": "Horsepower",
    "WEIGHT (1000 lbs)": "WEIGHT (1000 lbs)",  # Already correct
    "qsec": "1/4 mile time"
}

# Apply the renaming
df1 = df1.rename(columns=column_mapping)



app_ui = ui.page_auto(
    ui.sidebar(
        #ui.h5("Unique Key :"),
        ui.h5("Unique Key:", style="font-weight: bold;"),
        ui.output_text_verbatim("text"),
        ui.input_select("var1", "X Axis", choices=["Miles per Gallon","No of cylinders","Displacement (cu.in.)","Horsepower","WEIGHT (1000 lbs)","1/4 mile time"],),
        ui.input_select("var2", "Y Axis", choices=["Miles per Gallon","No of cylinders","Displacement (cu.in.)","Horsepower","WEIGHT (1000 lbs)","1/4 mile time"]),
            ),  
    ui.layout_columns(
        ui.card(
            ui.output_plot("plot1"),
            ui.input_action_button(
                "explain_plot_btn", 
                "Explain Plot", 
                class_="btn-sm btn-outline-primary ms-auto"
            ),
            #full_screen=True,
        ),

    ),
    ui.include_css(app_dir / "styles.css"),
    title="Vehicle Dashboard",
    fillable=True,
)


def server(input, output, session):
    _ = load_dotenv()
    chat_client = ChatAnthropic(
        system_prompt="You are a helpful assistant.",
    )

    chat = ui.Chat(id="chat")

    @render.text  
    def text():
        return str(uuid.uuid4())


    #session_id = str(uuid.uuid4())  #generating session ID

    # Generate a response when the user submits a message
    @chat.on_user_submit
    async def handle_user_input(user_input: str):
        response = await chat_client.stream_async(user_input)
        await chat.append_message_stream(response)

    # Function to create a plot widget for explanation

    def create_plot_widget():
    # Create the scatter plot
        fig, ax = plt.subplots(figsize=(8, 6))
        sns.scatterplot(
            data=df1,
            x=input.var1(),
            y=input.var2(),
            size='WEIGHT (1000 lbs)',
            hue='REGION',
            sizes=(20, 200),  # adjust size range as per your preference
            alpha=0.7
        )
        
    # Set titles and labels using plt or ax
        plt.title(f"{input.var2()} vs {input.var1()} (size = weight, color = region)")
        plt.xlabel(f"{input.var1()}")
        plt.ylabel(f"{input.var2()}")
    
    # Move legend outside the plot area
    #plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    #plt.figure(figsize=(8, 6))
    # Adjust layout to prevent clipping
        plt.tight_layout()
            

        # Create a simple plot widget-like object that has write_image method
        class PlotWidget:
            def __init__(self, figure):
                self.figure = figure
            
            def write_image(self, file_obj):
                self.figure.savefig(file_obj, format='png', bbox_inches='tight', dpi=150)
                plt.close(self.figure)  # Clean up
        
        return PlotWidget(fig)

    # Handle explain plot button click
    @reactive.effect
    @reactive.event(input.explain_plot_btn)
    async def handle_explain_plot():
        try:
            plot_widget = create_plot_widget()
            await explain_plot(chat_client, plot_widget, plot_type ="horsepower_vs_mpg")
        except Exception as e:
            import traceback
            traceback.print_exc()
            ui.notification_show(f"Error explaining plot: {str(e)}", type="error")

    @render.plot
    def plot1():
    # Set figure size BEFORE creating the plot
    #plt.figure(figsize=(10, 6))
    
    # Create the scatter plot
        ax = sns.scatterplot(
            data=df1,
            x=input.var1(),
            y=input.var2(),
            size='WEIGHT (1000 lbs)',
            hue='REGION',
            sizes=(20, 200),  # adjust size range as per your preference
            alpha=0.7
        )
        
    # Set titles and labels using plt or ax
        #title=f'Data Visualization ({input.embedding_type().split("_")[1].upper()} Embedding)')
        plt.title(f"{input.var2()} vs {input.var1()} (size = weight, color = region)")
        plt.xlabel(f"{input.var1()}")
        plt.ylabel(f"{input.var2()}")

    
    # Move legend outside the plot area
    #plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    #plt.figure(figsize=(8, 6))
    # Adjust layout to prevent clipping
        plt.tight_layout()
    


app = App(app_ui, server)