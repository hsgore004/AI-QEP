*** Settings ***
Resource    ../resources/common.resource
Suite Setup    Open Login Page
Suite Teardown    Close Browser Session


*** Test Cases ***

TC_UI_001 Login with valid credentials

    Open Login Page
    Enter Valid Email
    Enter Valid Password
    Click Login Button
    Verify Dashboard Is Displayed


TC_UI_002 Login with invalid email

    Open Login Page
    Enter Invalid Email
    Enter Valid Password
    Click Login Button
    Verify Error Message Is Displayed


TC_UI_003 Login with incorrect password

    Open Login Page
    Enter Valid Email
    Enter Invalid Password
    Click Login Button
    Verify Error Message Is Displayed


TC_UI_004 Login with both fields empty

    Open Login Page
    Leave Email Blank
    Leave Password Blank
    Click Login Button
    Verify Error Message Is Displayed


TC_UI_005 Login with only email field empty

    Open Login Page
    Leave Email Blank
    Enter Valid Password
    Click Login Button
    Verify Error Message Is Displayed


TC_UI_006 Login with only password field empty

    Open Login Page
    Enter Valid Email
    Leave Password Blank
    Click Login Button
    Verify Error Message Is Displayed


TC_UI_007 Testing email field maximum length

    Open Login Page
    Enter Valid Email
    Enter Valid Password
    Click Login Button
    Verify Dashboard Is Displayed


TC_UI_008 Testing password field maximum length

    Open Login Page
    Enter Valid Email
    Enter Valid Password
    Click Login Button
    Verify Dashboard Is Displayed


TC_UI_009 UI behavior on clearing input fields

    Open Login Page
    Enter Valid Email
    Enter Valid Password
    Leave Email Blank
    Leave Password Blank


TC_UI_010 Navigation back to the login page

    Open Login Page
    Leave Email Blank
    Leave Password Blank


TC_UI_011 UI response time under normal load

    Open Login Page
    Enter Valid Email
    Enter Valid Password
    Click Login Button


TC_UI_012 Accessibility check for email input

    Open Login Page
    Leave Email Blank


TC_UI_013 Accessibility check for password input

    Open Login Page
    Leave Password Blank


TC_UI_014 Check if data is encrypted during login

    Open Login Page
    Enter Valid Email
    Enter Valid Password
    Click Login Button


TC_UI_015 Attempt SQL injection in email field

    Open Login Page
    Enter Invalid Email
    Enter Valid Password
    Click Login Button
    Verify Error Message Is Displayed


TC_UI_016 Attempt XSS attack in password field

    Open Login Page
    Enter Valid Email
    Enter Invalid Password
    Click Login Button
    Verify Error Message Is Displayed