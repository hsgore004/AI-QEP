*** Settings ***
Resource    ../resources/common.resource
Suite Setup    Open Login Page
Suite Teardown    Close Browser Session


*** Test Cases ***

TC_UI_001 Successful login with valid credentials

    Enter Valid Email
    Enter Valid Password
    Click Login Button
    Verify Dashboard Is Displayed


TC_UI_002 Email field is mandatory

    Leave Email Blank
    Enter Valid Password
    Click Login Button
    Verify Error Message Is Displayed


TC_UI_003 Password field is mandatory

    Enter Valid Email
    Leave Password Blank
    Click Login Button
    Verify Error Message Is Displayed


TC_UI_004 Login with invalid credentials

    Enter Invalid Email
    Enter Invalid Password
    Click Login Button
    Verify Error Message Is Displayed


TC_UI_005 Login with email in incorrect format

    Enter Invalid Email
    Enter Valid Password
    Click Login Button
    Verify Error Message Is Displayed


TC_UI_006 Minimum length for password

    Enter Valid Email
    Leave Password Blank
    Click Login Button
    Verify Error Message Is Displayed


TC_UI_007 UI behavior on page load

    Open Login Page


TC_UI_008 Navigation to the dashboard after successful login

    Enter Valid Email
    Enter Valid Password
    Click Login Button
    Verify Dashboard Is Displayed


TC_UI_009 UI handles multiple fast submissions

    Enter Valid Email
    Enter Valid Password
    Click Login Button
    Click Login Button
    Click Login Button


TC_UI_010 Accessibility - Screen Reader Support

    Open Login Page


TC_UI_011 Security - Prevent SQL injection attacks

    Enter Invalid Email
    Enter Invalid Password
    Click Login Button
    Verify Error Message Is Displayed


TC_UI_012 Security - Check for sensitive password handling

    Open Login Page


TC_UI_013 Field length validation for email

    Enter Invalid Email
    Enter Valid Password
    Click Login Button
    Verify Error Message Is Displayed