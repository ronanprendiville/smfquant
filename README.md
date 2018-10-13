# UCC SMF Quant Team Project

A project made for UCC students by UCC students which is gunna win us gold ya boi


## Setup

### IntelliJ

This will be your IDE (Integrated Development Environment) where the coding will happen. Download IntelliJ Ultimate edition from https://www.jetbrains.com/idea/download/#section=windows.

To get your student license to use IntelliJ ultimate for free, go to https://www.jetbrains.com/shop/eform/students.

### Database

The plan is to use Amazon Relational Database Service (RDB), with our SQL dialect to be PostgreSQL

### Git

Git will be our version control system, download Git at https://git-scm.com/.

To set up git in your IntelliJ project. Go to Settings -> Version Control -> Git. When here change your "Path to Git executable" to wherever your git.exe file is (found in 'Git\bin' folder which is likely in 'C:\Program Files').

You may also need to add git to your 'PATH' environment variable.

You can do it this way:

Go to Control panel/System/Advanced System Settings
  - Click Environment variables
  - Select PATH and click Edit
  - Append following string at the end of the variable value: ;C:\Program Files\Git\bin
      - The semicolon is important, because individual PATH entries are delimited by it
      - The path to git bin directory might be different on your system
      
You can check if git is working by going into your IntelliJ, clicking 'Terminal' at the bottom, typing in 'git --version' and clicking enter. If this doesn't error, all good.

### Stock Info

At present it looks like it will be a mix of yahoo finance with information being taken from their API using Pandas datareader.
There is also 'Thomson Reuters Eikon' which is a library resource which looks like it will have valuable information. Must look further into this.
