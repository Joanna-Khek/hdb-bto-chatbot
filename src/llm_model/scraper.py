import pandas as pd
import hydra
import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By

class HDBData:
    def __init__(self, url_pages, webdriver):
        self.url_pages = url_pages
        self.driver = webdriver
        
    def _check_if_accordian_present(self):
        return (len(self.driver.find_elements(By.CLASS_NAME, "accordion-navigation")) > 0)
    
    def _text_formatter(self, text):
        cleaned_text = text.replace("\n", " ").strip()
        cleaned_text = " ".join(cleaned_text.split(" "))
        return cleaned_text
    
    def extract(self):
        texts_information = []
        count = 1
        for url in self.url_pages:
            print(f"Scraping: {count}/{len(self.url_pages)}\nPage: {url}")
            self.driver.get(url)
            page_category = self.driver.find_element(By.CLASS_NAME, "main-content").find_element(By.TAG_NAME, "h1").text
            extracted_text = self.driver.find_element(By.CLASS_NAME, "main-content").text
            extracted_text = self._text_formatter(extracted_text)
            texts_information.append({"page_url": url,
                                "page_category": page_category,
                                "page_section": "Main",
                                "page_char_count": len(extracted_text),
                                "page_word_count": len(extracted_text.split(" ")),
                                "page_sentence_count_raw": len(extracted_text.split(". ")),
                                "page_token_count": len(extracted_text)/4,
                                "texts": extracted_text}) 
            
            if self._check_if_accordian_present:
                for accordion_item in self.driver.find_elements(By.CLASS_NAME, "accordion-navigation"):
                    accordion_item.click()
                    time.sleep(1)
                    extracted_text = self._text_formatter(accordion_item.text)
                    texts_information.append({"page_url": url,
                                            "page_category": page_category,
                                            "page_section": "Accordion",
                                            "page_char_count": len(extracted_text),
                                            "page_word_count": len(extracted_text.split(" ")),
                                            "page_sentence_count_raw": len(extracted_text.split(". ")),
                                            "page_token_count": len(extracted_text)/4,
                                            "texts": extracted_text})
            count += 1
                       
        return texts_information            

@hydra.main(version_base=None, config_path='conf', config_name='config.yaml')            
def main(cfg):
    # Chrome driver options
    #chrome_options = webdriver.ChromeOptions()
    #chrome_options.add_argument("--headless")

    
    # Initialise driver
    driver = webdriver.Chrome()
    
    # Get data
    hdb_data = HDBData(cfg.url_pages, webdriver=driver)
    data = hdb_data.extract()
    
    # Save to file
    with open('data/data.json', 'w') as fp:
        json.dump(data, fp)

    print("Saved file to data/data.json")
    
if __name__ == "__main__":
    main()