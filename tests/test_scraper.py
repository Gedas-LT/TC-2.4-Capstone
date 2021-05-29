import pytest

from value_today.scraper import Scraper

scraper = Scraper()

def test_number_companies():
    assert type(scraper.number_companies()) == int
    assert scraper.number_companies() > 0

def test_valuetoday_usa_scraper():
    assert scraper.valuetoday_usa_scraper(16).shape == (20, 14)
    assert scraper.valuetoday_usa_scraper(6000) == "Too much companies."
    assert scraper.valuetoday_usa_scraper(-1) == "Check the number."

def test_df_cleaning():
    df = scraper.valuetoday_usa_scraper(16)
    assert scraper.df_cleaning(df).shape == (20, 8)