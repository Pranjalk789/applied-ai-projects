# Async AI Market Analysis Pipeline

A multi-stage, asynchronous AI research agent built with **Python**, **OpenAI**, and **Gradio**. This project demonstrates advanced prompt engineering and API chaining without relying on heavy external frameworks, offering a highly controlled and customizable data flow.

## 🏗️ Architecture & Pipeline Flow

Rather than using a single generic prompt, this application utilizes a custom-built sequential processing pipeline. The system passes contextual data through four distinct analytical functions, each powered by a highly tuned system prompt:

1. **Market Trend Analysis:** Scans and analyzes the target industry for macro trends and shifts.
2. **Competitor Comparison:** Performs a direct comparative analysis between a target company and a specified competitor.
3. **SWOT Generation:** Extracts and structures data into a formal Strengths, Weaknesses, Opportunities, and Threats matrix.
4. **Executive Synthesis:** Ingests the output of the previous three stages to generate a cohesive, high-level executive summary.

The entire pipeline is executed asynchronously (`asyncio`) to ensure a highly responsive user experience through the **Gradio** web interface.

## 🛠️ Tech Stack
* **Language:** Python 3.x
* **UI Framework:** Gradio
* **Concurrency:** `asyncio`
* **AI Integration:** Direct `openai` API
* **Environment Management:** `python-dotenv`

## 🚀 Local Setup & Installation

**1. Clone the repository**
```bash
git clone [https://github.com/YOUR-USERNAME/async-market-analysis-agent.git](https://github.com/YOUR-USERNAME/async-market-analysis-agent.git)
cd async-market-analysis-agent
**2. Set up the virtual environment

* **python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

**3. Install dependencies
(Ensure your requirements.txt includes openai, gradio, and python-dotenv)
* **pip install -r requirements.txt

**4. Configure Environment Variables
Create a .env file in the root directory and add your OpenAI API key:
Code snippet
* **OPENAI_API_KEY="sk-your-api-key-here"

**5. Run the Application
* **python app.py  # (Replace app.py with the name of your main python file)
The Gradio interface will automatically launch in your default web browser.