import os 
import streamlit as st 
from textwrap import dedent
import pandas as pd 
import json

from crewai import Agent, Task, Crew, Process
from crew import create_crewai_setup
import sys 

os.environ['OPENAI_API_KEY']=st.secrets['OPENAI_API_KEY']

OUTPUT_FOLDER = "Out/"

PILLARS = ['Finance', 'Infrastructure', 'Management', 'Marketing']


class StreamToExpander:
    def __init__(self, expander):
        self.expander = expander
        self.buffer = []

    def write(self, data):
        # Filter out ANSI escape codes using a regular expression
        cleaned_data = re.sub(r'\x1B\[[0-9;]*[mK]', '', data)

        self.buffer.append(cleaned_data)
        if "\n" in data:
            self.expander.markdown(''.join(self.buffer))
            self.buffer = []


# # Redirect stdout to our custom stream
# sys.stdout = StreamToUI(st)
# sys.stdout = sys.__stdout__

def run_crewai_app():
    st.title("💼 Madison Fox AI")
    st.sidebar.header('⚙️ Parameters')

    if "folder" not in st.session_state.keys():
        st.session_state['folder'] = "Out10/"

    if "prompts" not in st.session_state.keys():
        st.session_state['prompts'] = "prompts.csv"

    def on_click_btn(folder_name):
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)
            for subfolder in PILLARS:
                subfolder_path = os.path.join(folder_name, subfolder)
                if not os.path.exists(subfolder_path):
                    os.makedirs(subfolder_path)
                    print(f"Subfolder '{subfolder}' created successfully in '{folder_name}'.")
                else:
                    st.error(f"Subfolder '{subfolder}' already exists in '{folder_name}'.")
            st.success('Folder created')
        else:
            st.error('Folder exists')
    
    def is_any_directory_not_empty(directories):
        """Check if any of the specified directories is not empty."""
        for directory_path in directories:
            if os.listdir(directory_path):
                # Found a non-empty directory
                return True
        # All directories are empty
        return False


    # Allow users to select a folder
    def file_selector(folder_path='.'):
        folders = []
        files = os.listdir(folder_path)
        new_folder = '➕ new folder'
        for folder in files:
            flags =['.streamlit','__pycache__', 'agents','components','.git','data','utils','assets']
            if os.path.isdir(folder) and folder not in flags:
                folders.append(folder)
        
        folders.append(new_folder)
        selected_filename = st.sidebar.selectbox('📁 Select a folder for saving', folders)
        if selected_filename==folders[-1]: #if we select "add new folder"
            fn,fb=st.sidebar.columns(2)
            folder_name = fn.text_input('Folder name',placeholder="Folder name", label_visibility='collapsed')
            add_btn = fb.button('Add')
            if add_btn:
                on_click_btn(folder_name=folder_name)
                st.experimental_rerun()
        elif is_any_directory_not_empty([os.path.join(selected_filename, subfolder)for subfolder in os.listdir(selected_filename)]):
            st.sidebar.warning("This folder is not empty! it's content will be erased ")
        return os.path.join(folder_path, selected_filename)

    filename = file_selector()
    filename+="/"
    st.sidebar.write('You selected `%s`' % filename)

    
    save= st.sidebar.button('Save')
    

    business_presentation = st.text_area("Talk about your business", placeholder="I run a Marketing digital agency in the US")

    c1,c2=st.columns(2)
    if save:

        st.sidebar.success('Parameters saved...')
    
    run = c1.button("Run Analysis")
    if run:
        stop=c2.button('stop')
        if not stop:
            with st.container(border=True):
                sys.stdout = StreamToExpander(st)
                
                with st.spinner("Generating Results"):
                    crew_result = create_crewai_setup(business_presentation,OUTPUT_FOLDER=filename)
            
        st.header("Results:")
        st.markdown(crew_result)
        # Create an expander
        # with st.expander("Output"):
        #     # Redirect stdout to our custom stream
        # sys.stdout = StreamToExpander(st)

if __name__ == "__main__":
    run_crewai_app()
