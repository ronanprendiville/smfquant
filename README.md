# UCC SMF Quant Team Project

A project made for UCC students by UCC students which is gunna win us gold ya boi


## Setup

### IntelliJ

This will be your IDE (Integrated Development Environment) where the coding will happen. Download IntelliJ Ultimate edition from https://www.jetbrains.com/idea/download/#section=windows.

To get your student license to use IntelliJ ultimate for free, go to https://www.jetbrains.com/shop/eform/students.

### Database

The plan is to use Amazon Relational Database Service (RDS), with our SQL dialect to be PostgreSQL.

### Git

Git will be our version control system, download Git at https://git-scm.com/.

To set up git in your IntelliJ project. Go to Settings -> Version Control -> Git. When here change your "Path to Git executable" to wherever your git.exe file is (found in 'Git\bin' folder which is likely in 'C:\Program Files'). Then restart your IntelliJ.
      
You can check if git is working by going into your IntelliJ, clicking 'Terminal' at the bottom, typing in 'git --version' and clicking enter. If this doesn't error, all good.

### Stock Info

At present it looks like it will be a mix of yahoo finance with information being taken from their API using Pandas datareader, and there is also 'Thomson Reuters Eikon' which is a library resource which looks like it will have valuable information. Must look further into this.
