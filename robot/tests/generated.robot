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

TC_UI_002 Login with invalid email format

    Enter Invalid Email
    Enter Valid Password
    Click Login Button
    Verify Error Message Is Displayed

TC_UI_003 Login with no email

    Leave Email Blank
    Enter Valid Password
    Click Login Button
    Verify Error Message Is Displayed

TC_UI_004 Login with no password

    Enter Valid Email
    Leave Password Blank
    Click Login Button
    Verify Error Message Is Displayed

TC_UI_005 Login with valid email but invalid password

    Enter Valid Email
    Enter Invalid Password
    Click Login Button
    Verify Error Message Is Displayed

TC_UI_006 Login with valid credentials but API failure

    Enter Valid Email
    Enter Valid Password
    Click Login Button
    [Simulate API failure]
    Verify Error Message Is Displayed

TC_UI_007 Check boundary value for email length

    Enter Email with Max Length
    Enter Valid Password
    Click Login Button
    Verify Dashboard Is Displayed

TC_UI_008 Check boundary value for password length

    Enter Valid Email
    Enter Password with Max Length
    Click Login Button
    Verify Dashboard Is Displayed

TC_UI_009 Verify UI elements are accessible

    [Use screen reader to navigate through the login page]
    Verify UI components are read aloud properly by the reader

TC_UI_010 Verify UI components are correctly positioned

    [Check the position of UI components on the page]
    Verify all components are positioned according to the design specs

TC_UI_011 Error handling for rapid successive login attempts

    Rapidly Enter Invalid Credentials
    Click Login Button
    Verify Error Message Is Displayed

TC_UI_012 Check for security (brute force protection)

    Simulate Multiple Rapid Unsuccessful Login Attempts
    Verify Account is Locked or User is Temporarily Blocked

TC_UI_013 Ensure error messages are user-friendly

    [Trigger error scenarios like empty fields, invalid credentials]
    Verify Error messages are clear and provide guidance

TC_UI_014 Test UI RTL layout for accessibility

    [Change UI language/locale to one with RTL preference]
    Verify all elements are correctly adjusted for RTL languages