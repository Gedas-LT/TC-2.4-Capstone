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


def valuetoday_usa_scraper(n_companies: int) -> DataFrame:
    """Takes in the number of companies and returns dataframe with financial information: 
    company name, business category, market value, annual revenue, operating incomes,
    net incomes, assets and liabilities."""

    max_companies = number_companies()

    if n_companies > max_companies:
        return print("Too much companies!")

    ua = UserAgent()
    header = {'User-Agent':str(ua.chrome)}

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

    url = "https://www.value.today/headquarters/united-states-america-usa?page="

    if n_companies <= 10:
        pages = 0
    elif n_companies % 10 == 0:
        pages = (n_companies // 10) - 1
    else:
        pages = n_companies // 10

    for page in range(0, pages + 1):

        source = requests.get(url + str(page), headers=header)
        soup = BeautifulSoup(source.content, "html.parser")

        # Create a list of divs with all required information.
        info_blocks = soup.find_all("div", class_="node node--type-listed-companies node--view-mode-teaser ds-2col-stacked clearfix")

        for item in info_blocks:

            def collect_values(item, collected_list):
                """Takes in parsed div tag, name of particular list and append extracted or None values to that list."""
                if len(item) == 0 or len(item) >= 2:
                    collected_list.append(None)
                else:
                    string = item[0].text.strip() 
                    value = re.findall("\d+[.,]\d+|\\b(?<![a-zA-Z]-)\d+\\b|(?<!\S)-\d+.\d+", string)[0]
                    collected_list.append(value)


            def collect_metrics(item, collected_list):
                """Takes in parsed div tag, name of particular list and append extracted or None values to that list."""
                if len(item) == 0 or len(item) >= 2:
                    collected_list.append(None)
                else:
                    string = item[0].text.strip()
                    if "billion" in string.lower():
                        collected_list.append("Billion")
                    if "million" in string.lower():
                        collected_list.append("Million")

            
            market_value_item = item.select("div.field--name-field-market-value-jan012021 > div.field--item")
            if len(market_value_item) == 0:
                continue
            else:
                market_value = market_value_item[0]["content"]
                collected_values.append(market_value)
            collect_metrics(market_value_item, collected_values_metrics)

            name = item.find("h2").text.strip()
            collected_names.append(name)

            business = item.select("div.field--name-field-company-category-primary > div > div.field--item > a")[0].text.strip()
            collected_businesses.append(business)

            revenue_item = item.select("div.field--name-field-annual-revenue > div.field--item")
            collect_values(revenue_item, collected_revenues)
            collect_metrics(revenue_item, collected_revenues_metrics)

            op_income_item = item.select("div.field--name-field-annual-operating-income > div.field--item")
            collect_values(op_income_item, collected_op_incomes)
            collect_metrics(op_income_item, collected_op_incomes_metrics)

            net_income_item = item.select("div.field--name-field-annual-net-income-lc > div.field--item")
            collect_values(net_income_item, collected_net_incomes)
            collect_metrics(net_income_item, collected_net_incomes_metrics)

            assets_item = item.select("div.field--name-field-total-assets > div.field--item")
            collect_values(assets_item, collected_assets)
            collect_metrics(assets_item, collected_assets_metrics)

            liabilities_item = item.select("div.field--name-field-total-liabilities- > div.field--item")
            collect_values(liabilities_item, collected_liabilities)
            collect_metrics(liabilities_item, collected_liabilities_metrics)

        sleep(2)

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


def save_csv(data: DataFrame, file_name: str) -> None:
    """Takes in dataframe, file name and save that dataframe to .csv file in working directory."""
    
    data.to_csv(f"{file_name}.csv", index=False)