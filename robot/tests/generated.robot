*** Settings ***
Resource    ../resources/common.resource
Suite Setup    Open Login Page
Suite Teardown    Close Browser Session


*** Test Cases ***

| Test Case Name | Test Steps |
|----------------|------------|
| Verify Username field is visible | Open Login Page<br>Verify Username Field Is Visible |
| Verify Password field is visible | Open Login Page<br>Verify Password Field Is Visible |
| Verify Password visibility toggle is visible | Open Login Page<br>Verify Password Visibility Toggle Is Visible |
| Verify Log In button is visible | Open Login Page<br>Verify Log In Button Is Visible |
| Verify "Send me an email" link is visible | Open Login Page<br>Verify Send Me An Email Link Is Visible |
| Verify "Login details" link is visible | Open Login Page<br>Verify Login Details Link Is Visible |
| Verify Username is mandatory validation | Open Login Page<br>Leave Email Blank<br>Enter Valid Password<br>Click Login Button<br>Verify Error Message Is Displayed |
| Verify Password is mandatory validation | Open Login Page<br>Enter Valid Email<br>Leave Password Blank<br>Click Login Button<br>Verify Error Message Is Displayed |
| Verify successful login | Open Login Page<br>Enter Valid Email<br>Enter Valid Password<br>Click Login Button<br>Verify Dashboard Is Displayed |