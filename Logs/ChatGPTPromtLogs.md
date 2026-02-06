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
**"Help in writing proper docstrings for all functions in my project and creating a single pipeline script to run the entire project easily from the terminal or command prompt.."**

Tool used: ChatGPT

Response received:
Clear and consistent docstrings explaining each function’s purpose, parameters, and outputs.
A single pipeline script that integrates all modules and allows execution through one terminal command.

Problem faced & solution:
Struggled with maintaining consistent docstring formatting and understanding how to combine multiple modules into one executable pipeline. This was resolved by following a standard docstring structure and using a main pipeline file with a proper entry point, enabling smooth execution of the project from the terminal.

5) model 
6) frontend
7) deploy