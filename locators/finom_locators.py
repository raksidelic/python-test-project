from selenium.webdriver.common.by import By

class FinomLandingLocators:
    # --- Cookie Consent ---
    # Any button containing "Allow all" or "Accept"
    COOKIE_ACCEPT_BUTTON = (By.XPATH, "//button[@data-test='cookie-finom-card-accept-all']")

    # --- Country Selection ---
    # Country selection header (Used for wait condition)
    COUNTRY_MODAL_TITLE = (By.XPATH, "//*[contains(text(), 'Please, select the country')]")
    
    # Dynamic Country Selection (String to be formatted)
    # Example: //div[text()='Germany']
    COUNTRY_OPTION_TEMPLATE = "//*[contains(@class, 'locale-switcher')]//*[text()='{}']"

    # --- Language Selection ---
    # Language selection header
    LANGUAGE_MODAL_TITLE = (By.XPATH, "//*[contains(text(), 'Choose your language')]")
    
    # Dynamic Language Selection (EN, DE, FR etc.)
    LANGUAGE_OPTION_TEMPLATE = "//*[contains(@class, 'locale-switcher')]//*[text()='{}']"

    # --- Landing Page Elements ---
    # Homepage Login button (id="sign-in_header_btn")
    LOGIN_BUTTON = (By.ID, "sign-in_header_btn")