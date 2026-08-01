*** Settings ***
Resource    ../resources/common.resource
Suite Setup    Open Login Page
Suite Teardown    Close Browser Session


*** Test Cases ***

TC_UI_001 Successful login

    Enter Valid Email
    Enter Valid Password
    Click Login Button
    Verify Dashboard Is Displayed

TC_UI_002 Login with empty email

    Leave Email Blank
    Enter Valid Password
    Click Login Button
    Verify Error Message Is Displayed

TC_UI_003 Login with empty password

    Enter Valid Email
    Leave Password Blank
    Click Login Button
    Verify Error Message Is Displayed

TC_UI_004 Login with invalid email format

    Enter Invalid Email
    Enter Valid Password
    Click Login Button
    Verify Error Message Is Displayed

TC_UI_005 Login with incorrect credentials

    Enter Valid Email
    Enter Invalid Password
    Click Login Button
    Verify Error Message Is Displayed

TC_UI_006 Login with correct credentials after failed attempt

    Enter Valid Email
    Enter Invalid Password
    Click Login Button
    Enter Valid Password
    Click Login Button
    Verify Dashboard Is Displayed

TC_UI_007 Check Login Button behavior with empty fields

    Leave Email Blank
    Leave Password Blank
    Click Login Button
    Verify Error Message Is Displayed

TC_UI_008 Check UI behavior on login failure

    Enter Valid Email
    Enter Invalid Password
    Click Login Button
    Verify Password Field Is Accessible

TC_UI_009 Validate error message accessibility

    Enter Invalid Email
    Enter Invalid Password
    Click Login Button
    Verify Error Message Is Displayed

TC_UI_010 Test UI for SQL Injection attack

    Enter SQL Injection String
    Enter Any Password
    Click Login Button
    Verify Error Message Is Displayed

TC_UI_011 Boundary value: max length email

    Enter Maximum Length Email
    Enter Valid Password
    Click Login Button
    Verify Dashboard Is Displayed

TC_UI_012 Boundary value: max length password

    Enter Valid Email
    Enter Maximum Length Password
    Click Login Button
    Verify Dashboard Is Displayed