import json
from research_agent import chat

def create_market_analysis_prompt(industry: str, timeframe: str, data_focus: str) -> str:
    """
    Generates a market trend analysis prompt for generative AI.
    Args:
        industry (str): The industry to analyze.
        timeframe (str): The period for analysis (e.g., "2020-2023").
        data_focus (str): The key metrics to focus on (e.g., "growth rate, customer demographics, competitor activity").
    Returns:
        str: A formatted prompt for generative AI use.
    """
    return (
        f"Role: Senior Business Consultant reporting to C-Level Executives.\n"
        f"Analyze the main trends for the {industry} industry from {timeframe}, "
        f"focusing on: {data_focus}. If data is missing, explicitly state 'Data unavailable'. "
        "Summarize three key trends, provide supporting stats, and give a short forecast."
    )


def create_competitor_comparison_prompt(comp1: str, comp2: str, category: str) -> str:
    """
    Generates a competitor comparison prompt. 
    Args:
        comp1 (str): Name of first competitor.
        comp2 (str): Name of second competitor.
        category (str): The product/service segment to compare.
    Returns:
        str: A formatted competitor comparison prompt.
    """
    return (
        f"Role: Senior Business Consultant reporting to C-Level Executives.\n"
        f"Compare {comp1} and {comp2} focusing on {category}. "
        "List three strengths and three weaknesses for each company. If a comparison point is unclear, note it."
    )


#def create_swot_prompt(company: str, market: str) -> str:

#    return (
#        f"Role: Senior Business Consultant reporting to C-Level Executives.\n"
#        f"Conduct a SWOT analysis for {company} in the {market} market. "
#        "Return the response STRICTLY as a raw JSON object with no markdown formatting and no conversational text. "
#        "Example format: {\"strengths\": [\"S1\"], \"weaknesses\": [\"W1\"], \"opportunities\": [\"O1\"], \"threats\": [\"T1\"]}"
#    )
    
def create_swot_prompt_with_fewshot(company, market):
    """
    Generate a SWOT (Strengths, Weaknesses, Opportunities, Threats) analysis prompt.
    Args:
        company (str): The company to analyze.
        market (str): The market context (e.g., "North American SaaS").
    Returns:
        str: A prompt for SWOT analysis.
    """
    sample_output = '{"strengths": ["brand recognition"], "weaknesses": ["limited locations"], "opportunities": ["growing tourism"], "threats": ["rising costs"]}'
    return (
        "SYSTEM INSTRUCTION: You are a JSON-only API. The ONLY response must be a JSON object that strictly adheres to the provided example. Do not include markdown formatting or conversational text.\n"
        f"Role: Senior Business Consultant reporting to C-Level Executives.\n"
        f"Required Format: {sample_output}\n\n"
        f"Task: Conduct a SWOT analysis for {company} in {market}."
    )

def validate_json_output(output: str) -> bool:
    try:
        data = json.loads(output)
        return all(key in data for key in ["strengths", "weaknesses", "opportunities", "threats"])
    except Exception:
        return False
# ---------------------------------

def create_exec_summary_prompt(subject: str, max_words: int = 200) -> str:
    """
    Generate an executive summary prompt with optional maximum length.
    Args:
        subject (str): Subject of the report.
        max_words (int, optional): Maximum word count.
    Returns:
        str: Prompt formatted for executive summary.
    """
    return (
        f"Role: Senior Business Consultant reporting to C-Level Executives.\n"
        f"Write an actionable executive summary under {max_words} words based on this input: '{subject}'. "
        "If any input data contains the status 'NOT_AVAILABLE', ignore that section completely and proceed with summarizing the available data."
    )

import json

def run_robust_research_chain(industry, timeframe, data_points, comp1, comp2, category, market):
    print("Starting Robust Research Chain...\n")
    
    # ==========================================
    # STEP 1: Market Trend Analysis
    # ==========================================
    print(f"1. Analyzing {industry} market trends...")
    try:
        market_prompt = create_market_analysis_prompt(industry, timeframe, data_points)
        market_ai_result = chat(market_prompt, stream=False)
        
        if not market_ai_result or len(market_ai_result.strip()) < 15:
            raise ValueError("Output string too short or empty.")
            
    except Exception as e:
        print(f"   [Error in Step 1: {e}. Injecting structured placeholder.]")
        market_ai_result = json.dumps({"status": "NOT_AVAILABLE", "step": "Market Analysis"})

    # ==========================================
    # STEP 2: Competitor Comparison (The Missing Step!)
    # ==========================================
    print(f"2. Comparing {comp1} vs {comp2}...")
    try:
        comp_prompt = create_competitor_comparison_prompt(comp1, comp2, category)
        comp_ai_result = chat(comp_prompt, stream=False)
        
        # Validation Check
        if not comp_ai_result or len(comp_ai_result.strip()) < 15:
            raise ValueError("Competitor output string too short or empty.")
            
    except Exception as e:
        print(f"   [Error in Step 2: {e}. Injecting structured placeholder.]")
        comp_ai_result = json.dumps({"status": "NOT_AVAILABLE", "step": "Competitor Comparison"})

    # ==========================================
    # STEP 3: SWOT Analysis (With Validation & Retries)
    # ==========================================
    print(f"3. Generating SWOT data for {comp1}...")
    swot_string = ""
    max_retries = 3
    
    for attempt in range(max_retries):
        try:
            swot_prompt = create_swot_prompt_with_fewshot(comp1, market)
            swot_ai_result = chat(swot_prompt, stream=False)
            
            is_valid = validate_json_output(swot_ai_result)
            
            if is_valid:
                swot_data = json.loads(swot_ai_result)
                swot_string = json.dumps(swot_data, indent=2)
                break  # Success! Exit the retry loop
            else:
                if attempt < max_retries - 1:
                    print(f"   [Attempt {attempt + 1} failed JSON validation. Retrying...]")
                else:
                    raise ValueError("AI failed JSON schema validation after maximum retries.")
                    
        except Exception as e:
            if attempt == max_retries - 1:
                print(f"   [Error in Step 3: {e}. Injecting placeholder.]")
                swot_string = json.dumps({"status": "NOT_AVAILABLE", "step": "SWOT Analysis"})
                
    # ==========================================
    # STEP 4: Executive Summary (The Chain)
    # ==========================================
    print("4. Synthesizing data into Executive Summary...\n")
    try:
        # We now combine ALL THREE previous outputs to form the subject!
        combined_context = (
            f"Market Analysis:\n{market_ai_result}\n\n"
            f"Competitor Comparison:\n{comp_ai_result}\n\n"
            f"SWOT Data:\n{swot_string}"
        )
        
        exec_prompt = create_exec_summary_prompt(subject=combined_context, max_words=200)

        print("================ FINAL EXECUTIVE SUMMARY ================\n")
        chat(exec_prompt, stream=True)
        print("\n\n=========================================================")
        
    except Exception as e:
        print(f"\n❌ Pipeline Error during final synthesis: {e}")

# Run the test
if __name__ == "__main__":
    run_robust_research_chain(
        industry="Hospitality", 
        timeframe="2023-2024", 
        data_points="growth rate, digital bookings",
        comp1="Marriott", 
        comp2="Hilton", 
        category="digital experience", 
        market="North American Midmarket"
    )