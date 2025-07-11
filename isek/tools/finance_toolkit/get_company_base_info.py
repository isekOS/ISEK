from isek.tools.toolkit import Toolkit
import efinance as ef

import requests
from bs4 import BeautifulSoup


def get_stock_info(stock_code: str):
    """get base info of stock base on stock code"""

    return ef.stock.get_base_info(stock_code)


def get_company_info(url: str):
    """fetch additional company details base this url"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers)
        response.encoding = "utf-8"
        soup = BeautifulSoup(response.text, "html.parser")
        return soup.get_text(strip=True)
    except Exception:
        return ""


# Create toolkit with debug enabled
company_base_info_tools = Toolkit(
    name="stock_info_tool",
    tools=[get_stock_info, get_company_info],
    instructions="Fetch company information based on its stock code and the company's 'About' page or official website URL.",
    debug=True,
)


# Optionally, for demonstration, call list_functions and execute_function in debug mode
if __name__ == "__main__":
    company_base_info_tools.list_functions()
    stock_info = company_base_info_tools.execute_function(
        "get_stock_info", stock_code="00020"
    )
    company_info = company_base_info_tools.execute_function(
        "get_company_info", url="https://www.sensetime.com/cn/about-index#1"
    )
    print("Stock Info:", stock_info)
    print("Company Info:", company_info)
