*** Settings ***
Library     Browser
Resource    login.resource

*** Keywords ***

Open Login Page
    New Browser    chromium    headless=False
    New Context
    New Page
    # Go To will be implemented after providing the application URL.
    No Operation

Close Browser Session
    Close Browser