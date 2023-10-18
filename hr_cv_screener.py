# This Python script uses Azure's Form Recognizer and OpenAI's GPT-3.5 to compare a CV or resume against a job description.

import tkinter as tk
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient
import openai

# Set up OpenAI API credentials
openai.api_type = "azure"
openai.api_key = "<your_openai_key>"
openai.api_base = "https://YOUR_DEPLOYMENT_ID.openai.azure.com/"
openai.api_version = "2023-09-15-preview"

# Set up Azure Form Recognizer API credentials
endpoint = "https://YOUR_DEPLOYMENT_ID.cognitiveservices.azure.com/"
key = "<your_formrecognizer_key>"
document_analysis_client = DocumentAnalysisClient(
    endpoint=endpoint, credential=AzureKeyCredential(key)
)

# Define a function to compare the CV/Resume against the job description
def compare():
    # Get the URLs for the CV/Resume and job description from the GUI input fields
    form_url = form_url_entry.get()
    job_description = job_description_entry.get()
    
    # Use Azure Form Recognizer to analyze the CV/Resume and get its content
    poller = document_analysis_client.begin_analyze_document_from_url(
        "prebuilt-read", form_url)
    result = poller.result()
    cv_content = result.content
    
    # Use OpenAI's GPT-3 to generate a rating for the CV/Resume against the job description
    prompt = f"Rate this CV/resume against the job description out of 10 in the categories Technical ability, Soft Skills, General Rating . CV:{cv_content}. Job Description: {job_description}. Ratings:"
    chat_completion = openai.Completion.create(
        deployment_id="gpt-35-turbo-instruct",
        prompt=prompt,
        max_tokens=500,
        temperature=0.7,
        top_p=1,
        frequency_penalty=0.5,
        presence_penalty=0.5,
        stop=["\n\n"]
    )
    rating = chat_completion.choices[0].text
    
    # Display the rating in the GUI
    rating_label.config(text=f"Rating: {rating}")

# Create the main window of the GUI
root = tk.Tk()
root.title("CV Comparison")
root.geometry("600x400")

# Add input fields for the CV/Resume and job description URLs
form_url_label = tk.Label(root, text="CV/Resume URL:")
form_url_label.pack()
form_url_entry = tk.Entry(root, width=80)
form_url_entry.pack()

job_description_label = tk.Label(root, text="Job Description URL:")
job_description_label.pack()
job_description_entry = tk.Entry(root, width=80)
job_description_entry.pack()

# Add a button to trigger the comparison function
compare_button = tk.Button(root, text="Compare", command=compare)
compare_button.pack()

# Add a label to display the rating
rating_label = tk.Label(root, text="", wraplength=500)
rating_label.pack()

# Run the main event loop of the tkinter GUI application
root.mainloop()
