from pandas.core.frame import DataFrame
import requests
import re
import pandas as pd
import warnings
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from time import sleep

def number_companies() -> int:
    """Returns the number of how much companies could be scraped."""

    ua = UserAgent()
    header = {'User-Agent':str(ua.chrome)}

    url = "https://www.value.today/headquarters/united-states-america-usa"

    source = requests.get(url, headers=header)
    soup = BeautifulSoup(source.content, "html.parser")

    footer_text = soup.find(class_="view-footer").text.strip()
    n_companies = int(re.findall("(\d+)(?!.*\d)", footer_text)[0])

    return n_companies


def data_scraper() -> DataFrame:
    """Takes in the number of companies and returns dataframe with financial information."""

    ua = UserAgent()
    header = {'User-Agent':str(ua.chrome)}

    url = "https://www.value.today/headquarters/united-states-america-usa"

    source = requests.get(url, headers=header)
    soup = BeautifulSoup(source.content, "html.parser")

    # Create a list of divs with all required information.
    info_blocks = soup.find_all("div", class_="node node--type-listed-companies node--view-mode-teaser ds-2col-stacked clearfix")

    collected_names = []
    collected_businesses = []
    collected_values = []
    collected_values_metrics = []
    collected_revenues = []
    collected_revenues_metrics = []
    collected_op_incomes = []
    collected_op_incomes_metrics = []
    collected_net_incomes = []
    collected_net_incomes_metrics = []
    collected_assets = []
    collected_assets_metrics = []
    collected_liabilities = []
    collected_liabilities_metrics = []

    for item in info_blocks:

        name = item.find("h2").text.strip()
        collected_names.append(name)

        business = item.select("div.field--name-field-company-category-primary > div > div.field--item > a")[0].text.strip()
        collected_businesses.append(business)

        value = item.select("div.field--name-field-market-value-jan012021 > div.field--item")[0]["content"]
        collected_values.append(value)

        value_string = item.select("div.field--name-field-market-value-jan012021 > div.field--item")[0].text.strip()
        if "Billion" in value_string:
            collected_values_metrics.append("Billion")
        elif "Million" in value_string:
            collected_values_metrics.append("Million")

        revenue_string = item.select("div.field--name-field-annual-revenue > div.field--item")[0].text.strip()
        revenue = re.findall("\d+[.,]\d+", revenue_string)
        collected_revenues.append(revenue[0])

        if "Billion" in revenue_string:
            collected_revenues_metrics.append("Billion")
        elif "Million" in revenue_string:
            collected_revenues_metrics.append("Million")
            
        op_income_item = item.select("div.field--name-field-annual-operating-income > div.field--item")
        if len(op_income_item) == 0:
            collected_op_incomes.append(None)
        else:
            op_income_string = op_income_item[0].text.strip()
            op_income = re.findall("\d+[.,]\d+", op_income_string)
            collected_op_incomes.append(op_income[0])

        if len(op_income_item) == 0:
            collected_op_incomes_metrics.append(None)
        elif "Billion" in op_income_string:
            collected_op_incomes_metrics.append("Billion")
        elif "Million" in op_income_string:
            collected_op_incomes_metrics.append("Million")

        net_income_string = item.select("div.field--name-field-annual-revenue > div.field--item")[0].text.strip()
        net_income = re.findall("\d+[.,]\d+", net_income_string)
        collected_net_incomes.append(net_income[0])

        if "Billion" in net_income_string:
            collected_net_incomes_metrics.append("Billion")
        elif "Million" in net_income_string:
            collected_net_incomes_metrics.append("Million")

        assets_string = item.select("div.field--name-field-total-assets > div.field--item")[0].text.strip()
        assets = re.findall("\d+[.,]\d+", assets_string)
        collected_assets.append(assets[0])

        if "Billion" in assets_string:
            collected_assets_metrics.append("Billion")
        elif "Million" in assets_string:
            collected_assets_metrics.append("Million")

        liabilities_string = item.select("div.field--name-field-total-liabilities- > div.field--item")[0].text.strip()
        liabilities = re.findall("\d+[.,]\d+", liabilities_string)
        collected_liabilities.append(liabilities[0])

        if "Billion" in liabilities_string:
            collected_liabilities_metrics.append("Billion")
        elif "Million" in liabilities_string:
            collected_liabilities_metrics.append("Million")

    df = pd.DataFrame({"Company Name": collected_names, "Company Business": collected_businesses, "Market Value": collected_values, 
                       "Value Metric": collected_values_metrics, "Annual Revenue": collected_revenues, 
                       "Revenue Metric": collected_revenues_metrics, "Operating Income": collected_op_incomes, 
                       "Op Income Metric": collected_op_incomes_metrics, "Net Income": collected_net_incomes, 
                       "Net Income Metric": collected_net_incomes_metrics, "Assets": collected_assets, 
                       "Assets Metric": collected_assets_metrics, "Liabilities": collected_liabilities, 
                       "Liabilities Metric": collected_liabilities_metrics})

    return df


def df_cleaning(raw_df: DataFrame) -> DataFrame:
    """Takes in initial dataframe from data_scraper function and returns
    cleaned dataframe with whole numerical values."""

    numeric_columns = ["Market Value", "Annual Revenue", "Operating Income", "Net Income", "Assets", "Liabilities"]

    raw_df[numeric_columns] = raw_df[numeric_columns].replace(",", "", regex=True)
    raw_df[numeric_columns] = raw_df[numeric_columns].apply(pd.to_numeric)

    final_df = raw_df[["Company Name", "Company Business"]]

    def change_num_values(numerical_column: str, metric_column: str) -> None:
        """Takes in names of numerical and metric columns and changes values of numerical columns."""

        final_df[numerical_column] = 0 
        for count, row in enumerate(raw_df[metric_column]):
            if row == "Million":
                final_df[numerical_column][count] = raw_df[numerical_column][count] * 1000000
            if row == "Billion":
                final_df[numerical_column][count] = raw_df[numerical_column][count] * 1000000000

    # Ignore Python warnings about copying dafaframe.
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        change_num_values("Market Value", "Value Metric")
        change_num_values("Annual Revenue", "Revenue Metric")
        change_num_values("Operating Income", "Op Income Metric")
        change_num_values("Net Income", "Net Income Metric")
        change_num_values("Assets", "Assets Metric")
        change_num_values("Liabilities", "Liabilities Metric")

    return final_df