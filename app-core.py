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

# Prepare the data
print(Path(__file__).parent)
location = Path(__file__).parent
file_name = 'mtcars.csv'
image_file_path = location / file_name
df1 = pd.read_csv(image_file_path)




app_ui = ui.page_auto(
 
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
        ui.card(
            ui.output_plot("plot2"),
            ui.input_action_button(
                "explain_plot_btn2", 
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
            x='mpg',
            y='hp',
            size='WEIGHT (1000 lbs)',
            hue='REGION',
            sizes=(20, 200),  # adjust size range as per your preference
            alpha=0.7
        )
        
    # Set titles and labels using plt or ax
        plt.title("Horsepower vs MPG (size = weight, color = region)")
        plt.xlabel("Miles per Gallon (MPG)")
        plt.ylabel("Horsepower")
    
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
            await explain_plot(chat_client, plot_widget)
        except Exception as e:
            import traceback
            traceback.print_exc()
            ui.notification_show(f"Error explaining plot: {str(e)}", type="error")

    # Function to create a 2nd plot widget for explanation

    def create_plot_widget2():
    # Create the scatter plot
        fig, ax = plt.subplots(figsize=(8, 6))
        sns.scatterplot(
            data=df1,
            x='mpg',
            y='qsec',
            size='WEIGHT (1000 lbs)',
            hue='REGION',
            sizes=(20, 200),  # adjust size range as per your preference
            alpha=0.7
        )
        

    # Set titles and labels using plt or ax
        plt.title("Quarter Mile Time vs MPG (size = weight, color = region)")
        plt.xlabel("Miles per Gallon (MPG)")
        plt.ylabel("Quarter Mile Time")
    
    # Move legend outside the plot area
    #plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    #plt.figure(figsize=(8, 6))
    # Adjust layout to prevent clipping
        plt.tight_layout()
            

        # Create a simple plot widget-like object that has write_image method
        class PlotWidget2:
            def __init__(self, figure):
                self.figure = figure
            
            def write_image(self, file_obj):
                self.figure.savefig(file_obj, format='png', bbox_inches='tight', dpi=150)
                plt.close(self.figure)  # Clean up
        
        return PlotWidget2(fig)

    # Handle explain plot button click
    @reactive.effect
    @reactive.event(input.explain_plot_btn2)
    async def handle_explain_plot():
        try:
            plot_widget = create_plot_widget2()
            await explain_plot(chat_client, plot_widget)
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
            x='mpg',
            y='hp',
            size='WEIGHT (1000 lbs)',
            hue='REGION',
            sizes=(20, 200),  # adjust size range as per your preference
            alpha=0.7
        )
        
    # Set titles and labels using plt or ax
        plt.title("Horsepower vs MPG (size = weight, color = region)")
        plt.xlabel("Miles per Gallon (MPG)")
        plt.ylabel("Horsepower")

    
    # Move legend outside the plot area
    #plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    #plt.figure(figsize=(8, 6))
    # Adjust layout to prevent clipping
        plt.tight_layout()
    
    @render.plot
    def plot2():
    # Set figure size BEFORE creating the plot
    #plt1.figure(figsize=(10, 6))
    
    # Create the scatter plot
        ax = sns.scatterplot(
            data=df1,
            x='mpg',
            y='qsec',
            size='WEIGHT (1000 lbs)',
            hue='REGION',
            sizes=(20, 200),  # adjust size range as per your preference
            alpha=0.7
        )
        
    # Set titles and labels using plt or ax
        plt.title("Quarter Mile Time vs MPG (size = weight, color = region)")
        plt.xlabel("Miles per Gallon (MPG)")
        plt.ylabel("Quarter Mile Time")
    

        plt.tight_layout()



app = App(app_ui, server)