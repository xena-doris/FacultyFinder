# LLM Prompts Log

## 1) Prompt given:
**“Scrape faculty details from the institute website and store them in a structured database for analytics.”**

Tool used: ChatGPT

Response received:
Used Scrapy to parse faculty listing pages, extracted names, profile links, specializations, and publications, and stored them in SQLite with JSON fields where required.

Problem faced & solution:
Issue: Inconsistent HTML structure and nested tags caused missing or partial data.
Solution: Carefully inspected the DOM, used robust CSS selectors, handled optional fields safely, and validated extracted data before inserting into the database.

## 2) Prompt given:
**“Clean and normalize scraped JSON data into CSV files suitable for FastAPI ingestion.”** 

Tool used: ChatGPT

Response received:
Cleaned malformed text fields, normalized JSON structures, and converted the processed data into well-structured CSV files that could be reliably loaded and served by FastAPI.

Problem faced & solution:
Issue: Inconsistent quotations, special characters, and punctuation in scraped text caused JSON decoding errors and malformed CSV rows.
Solution: Sanitized text fields, escaped or removed problematic characters, validated JSON before parsing, and ensured consistent column formatting while exporting to CSV.

## 3) Prompt given:
**“Build a FastAPI endpoint to search faculty by name or ID."**

Tool used: ChatGPT

Response received:
Implemented a FastAPI /faculty/search endpoint using query parameters and SQLite queries with case-insensitive matching.

Problem faced & solution:
Issue: FastAPI expected query parameters, but the request format didn’t match (422 error).
Solution: Explicitly defined parameters using Query(...), ensured correct request format (?name=xyz), and validated input before executing the SQL query.

## 4) Prompt given:
**"Help in writing proper docstrings for all functions in my project and creating a single pipeline script to run the entire project easily from the terminal or command prompt."**

Tool used: ChatGPT

Response received:
Clear and consistent docstrings explaining each function’s purpose, parameters, and outputs.
A single pipeline script that integrates all modules and allows execution through one terminal command.

Problem faced & solution:
Struggled with maintaining consistent docstring formatting and understanding how to combine multiple modules into one executable pipeline. This was resolved by following a standard docstring structure and using a main pipeline file with a proper entry point, enabling smooth execution of the project from the terminal.

## 5) Prompt given:
**"Give guidance on selecting an appropriate model type and a specific Sentence Transformer to generate text embeddings for faculty profiles, and then use those embeddings to find semantically related faculty members based on a user query."** 

Tool used: ChatGPT

Response received:
ChatGPT suggested using a Sentence Transformer model (all-mpnet-base-v2) suitable for semantic similarity tasks on academic data, explained how to generate embeddings for faculty data, and demonstrated how cosine similarity can be used to compare query embeddings with stored faculty embeddings to retrieve the most relevant matches.

Problem faced & solution:
We initially struggled with deciding which transformer model was best for my use case and had confusion around correctly generating embeddings and applying cosine similarity in a way that returned meaningful and accurate faculty matches.

## 6) Prompt given:
**"Help in improving the frontend layout, formatting, and overall visual design of the application."** 

Tool used: ChatGPT

Response received:
Suggested UI and styling improvements to make the interface cleaner, better aligned, and more user-friendly.

Problem faced & solution:
The frontend initially looked cluttered and poorly formatted, with spacing, alignment, and design issues affecting usability.

## 7) Prompt given:
**"Give guidance on deploying the project online, including suitable platforms for hosting a data-driven application and recommendations for free or low-cost deployment options."**

Tool used: ChatGPT & Antigravity

Response received:
ChatGPT explained multiple deployment services, discussed their limitations, and suggested trying different platforms based on resource availability, data limits, and ease of setup, eventually recommending Streamlit Cloud as a practical choice.

Problem faced & solution:
We encountered data and resource limitations on several deployment platforms, which caused failures or restricted functionality. After experimenting with multiple services, I resolved the issue by deploying the application on Streamlit Cloud, which better supported the project’s requirements