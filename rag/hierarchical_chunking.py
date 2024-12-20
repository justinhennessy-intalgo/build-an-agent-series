from pinecone import Pinecone
from openai import OpenAI
from dotenv import load_dotenv
from docx import Document
import os

# Load environment variables from the parent directory
load_dotenv()

# Initialize Pinecone
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

# Initialize the OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def process_markdown(markdown_content):
    content_blocks = []
    current_section = None
    current_subsection = None

    # Split content into lines
    lines = markdown_content.splitlines()

    for line in lines:
        # Check for markdown headings
        if line.startswith("# "):  # Heading 1
            current_section = line[2:].strip()
            current_subsection = None  # Reset subsection when a new section starts
        elif line.startswith("## "):  # Heading 2
            current_subsection = line[3:].strip()
        elif line.strip():  # Non-empty content
            # Add paragraph content with current section and subsection as metadata
            content_blocks.append({
                "content": line.strip(),
                "section": current_section,
                "subsection": current_subsection
            })

    return content_blocks

# Example text
text = """
# Introduction

In today’s digital age, organizations are increasingly reliant on technology to drive business outcomes and improve operational efficiency. As companies strive to stay competitive, understanding the importance of effective technology implementation and data management becomes crucial. This document serves as a comprehensive guide to understanding the basics of implementing and managing digital tools within an organization. It is designed to be a starting point for IT teams, business managers, and decision-makers who aim to improve their organization’s technological capabilities.

# Overview of Digital Transformation

Digital transformation is the integration of digital technology into all areas of business, fundamentally changing how companies operate and deliver value to customers. This transformation is not just about adopting new technology; it’s a cultural shift that requires organizations to continuously challenge the status quo, experiment, and become comfortable with failure. A successful digital transformation requires leadership, vision, and an understanding of the critical areas where technology can have the most impact.

# Key Components of Digital Strategy

A successful digital strategy incorporates several key components:

## Leadership and Vision
Leadership teams must establish a clear vision for digital transformation, outlining goals, strategies, and measurable outcomes.

## Data Management
Data is a core asset for any organization. Proper data management practices, including data collection, storage, security, and analysis, are essential for making informed decisions.

## Technology Selection
Choosing the right technology involves assessing current capabilities, understanding future needs, and selecting tools that align with the organization’s objectives.

## Employee Training and Engagement
Employees must be educated on new technologies and encouraged to engage with them actively. Training programs can foster a culture of continuous learning and adaptation.

# Technology Implementation Framework

Implementing technology within an organization requires a structured framework to ensure success. The following steps outline a high-level approach to implementing new digital tools:

## Step 1: Needs Assessment
Identify the key challenges and opportunities within the organization. What problems need solving? Where can technology make a measurable difference? A thorough needs assessment will highlight areas for improvement.

## Step 2: Solution Research and Evaluation
Once needs are identified, research potential solutions and evaluate them against specific criteria such as cost, scalability, ease of use, and compatibility with existing systems. Create a shortlist of solutions that meet the organization’s requirements.

## Step 3: Pilot Program
Conduct a pilot program to test the chosen technology on a smaller scale. Gather feedback from users, evaluate performance, and determine whether the solution meets expectations.

## Step 4: Full-Scale Deployment
If the pilot is successful, proceed with a full-scale deployment. Ensure that all users are adequately trained, and provide resources for troubleshooting common issues.

## Step 5: Continuous Monitoring and Improvement
After deployment, continuously monitor the system's performance and gather feedback from users. Identify areas for improvement and consider updates or upgrades as necessary.

# Data Management Best Practices

Data management is a critical component of digital transformation. Here are some best practices for managing data effectively:

## Data Quality Control
Implement processes to ensure that data is accurate, complete, and up-to-date. Poor data quality can lead to inaccurate insights and poor decision-making.

## Data Security
Protect data from unauthorized access, breaches, and loss. Implement security protocols such as encryption, access controls, and regular audits.

## Data Analytics
Use data analytics tools to extract insights from raw data. Analytics can help identify trends, measure performance, and support strategic decision-making.

# Training and Employee Engagement

The success of any digital initiative depends on employee engagement. Training programs should be tailored to different roles within the organization, ensuring that employees have the knowledge and skills to use new technologies effectively. Regular workshops, seminars, and interactive sessions can boost engagement and facilitate a smooth transition to new systems.

# Measuring Success

Measuring the success of a digital transformation initiative involves setting key performance indicators (KPIs) that align with the organization’s goals. KPIs may include metrics such as system uptime, user adoption rates, cost savings, and customer satisfaction. Regular assessments help identify whether the transformation is delivering the expected value and where further improvements can be made.

# Conclusion

Digital transformation is a journey, not a destination. Organizations that succeed in digital transformation continuously evolve their strategies, adapt to changing technologies, and place a strong emphasis on data management and employee engagement. By following a structured framework and embracing a culture of innovation, companies can position themselves for long-term success in a digital-first world.
"""

index = pc.Index('insert_your_index_name_here') # Ensure you put in the name of the index that you created in pinecone here
print("Assigned Pinecone index 'insert_your_index_name_here'")

# Process the markdown content and retrieve content with metadata
content_blocks = process_markdown(text)

# Generate embeddings and store in Pinecone
print("Starting to process and store text chunks...")
for i, block in enumerate(content_blocks):
    if block["content"].strip():  # Skip empty content
        print(f"Processing chunk {i+1}...")
        response = client.embeddings.create(input=block["content"], model="text-embedding-3-small")
        embedding = response.data[0].embedding
        print(f"Generated embedding for chunk {i+1}")

        # Clean metadata by removing None values and ensuring proper types
        metadata = {
            "DocID": "document_1",
            "ChunkNumber": i,
            "text": block["content"]
        }

        # Only add section and subsection if they exist
        if block.get("section"):
            metadata["Section"] = block["section"]
        if block.get("subsection"):
            metadata["Subsection"] = block["subsection"]

        index.upsert(
            vectors=[(f"document_1_chunk_{i}", embedding, metadata)],
            namespace="hierarchical_chunking"
        )
        print(f"Stored chunk {i+1} in Pinecone index")

print("Finished processing and storing all chunks")

