import os 
import streamlit as st 
from crewai import Agent, Task, Crew, Process
from textwrap import dedent
import pandas as pd 
import json
from langchain_groq import ChatGroq

os.environ['OPENAI_API_KEY']=st.secrets['OPENAI_API_KEY']
os.environ['GROQ_API_KEY']=st.secrets['GROQ_API_KEY']

llm = ChatGroq(temperature=0, model_name="llama3-8b-8192")

def create_crewai_setup(business_presentation,OUTPUT_FOLDER):

    #OUTPUT_FOLDER = "Out10/"
    CSV_PROMPTS="data/processed/prompts.csv"
    PILLARS = ['Finance', 'Infrastructure', 'Management', 'Marketing']

    HUMAN_INPUT=False 

    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)
        for subfolder in PILLARS:
            subfolder_path = os.path.join(OUTPUT_FOLDER, subfolder)
            if not os.path.exists(subfolder_path):
                os.makedirs(subfolder_path)
                print(f"Subfolder '{subfolder}' created successfully in '{OUTPUT_FOLDER}'.")
            else:
                print(f"Subfolder '{subfolder}' already exists in '{OUTPUT_FOLDER}'.")



    os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]

    from crewai import Agent, Task, Crew, Process
    from textwrap import dedent
    import pandas as pd 
    import json


    ai_data = pd.read_csv(CSV_PROMPTS)
    ai_data.columns[0]
    ai_data.rename(columns={'Seq #': 'id', 'LifeCycle Stage/Level': 'level', 'Ai Prompts - P5 Building Block Sequence': 'prompt','Document Title':'title','LLM':'llm'}, inplace=True)
    ai_data['title'] = ai_data['title'].astype(str).str.replace('/', '-')
    json_data = ai_data.to_json(orient='records')
    ai_dict = json.loads(json_data)


    def do_task(agent,description,output_file):
        if HUMAN_INPUT :
            description = description + "IMPORTANT : Make sure to check with a human if the draft is good before finalizing your answer. if he writes 'next' you can go and continue, if he writes comments, you should revisit your answer before passing to the next one"
        return Task(
            description=description,
            agent=agent,
            memory=True,
            final_answer='Your final answer must well formated and clear',
            expected_output='A full and detailed response, make sure to follow all instructions ',
            output_file=output_file
        )



    # Define the Analyst agent
    business_owner = Agent(
        role="Business Owner",
        backstory=dedent(f"""You are a seasoned business development strategist with a proven track record of helping businesses launch and achieve sustainable growth
                            Your approach is holistic, encompassing market research, competitor analysis, product positioning, marketing strategies, sales tactics, and operational efficiencies.
                            You are also highly skilled in writing comprehensive documentation
                            
                            """),
        goal=dedent(f"""Help businesses launching and growing by providing a comprehensive business development plan """),
        allow_delegation=False,
        verbose=True,
        llm=llm

        
    )

    task_list = []

    i=1
    for task in ai_dict:
        if task['prompt'] and task['Pillar'] and task['title']:
            prompt = task['prompt']
            folder = task['Pillar']
            filename = task['title']
            file_path = OUTPUT_FOLDER+folder+'/'+str(i)+'-'+filename+'.txt'
            temp_task = do_task(
                agent=business_owner,
                description= prompt,
                output_file= file_path
                )
            task_list.append(temp_task)
            i+=1


    # Instantiate the crew
    crew = Crew(
        agents=[business_owner],
        tasks=task_list,
        process=Process.sequential,
        verbose=True,
        memory=True,
    )

    # Execute the tasks
    result = crew.kickoff(inputs={'business_presentation': business_presentation})

    # Output the result
    return result
