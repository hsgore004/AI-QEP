*** Settings ***
Resource    ../resources/common.resource
Suite Setup    Open Login Page
Suite Teardown    Close Browser Session


*** Test Cases ***
TC_UI_Verify mandatory Username validation
    Open Login Page
    Leave Email Blank
    Click Login Button
    Verify Error Message Is Displayed

TC_UI_Verify mandatory Password validation
    Open Login Page
    Leave Password Blank
    Click Login Button
    Verify Error Message Is Displayed

TC_UI_Verify successful login with valid credentials
    Open Login Page
    Enter Valid Email
    Enter Valid Password
    Click Login Button
    Verify Dashboard Is Displayed

TC_UI_Verify login functionality with Password visibility toggle
    Open Login Page
    Enter Valid Email
    Enter Valid Password
    # Missing keyword for Password visibility toggle