# UCC SMF Quant Team Project

A project created by students of University College Cork for the 2018/19 Student Managed Fund competition.

## Setup

To have access to edit the project, set up a github account and send me your username. I will then add you as a contributor.

### IntelliJ

This will be your IDE (Integrated Development Environment) where the coding will happen. Download IntelliJ Ultimate edition from https://www.jetbrains.com/idea/download/#section=windows.

To get your student license to use IntelliJ ultimate for free, go to https://www.jetbrains.com/shop/eform/students.

### Git

Git will be our version control system, download Git at https://git-scm.com/.

To set up git in your IntelliJ project. Go to Settings -> Version Control -> Git. When here change your "Path to Git executable" to wherever your git.exe file is (found in 'Git\bin' folder which is likely in 'C:\Program Files'). Then restart your IntelliJ.
      
You can check if git is working by going into your IntelliJ, clicking 'Terminal' at the bottom, typing in 'git --version' and clicking enter. If this doesn't error, all good.

To get the project on your intelliJ:
- Open Git Bash on your computer
- Use the 'cd' command to get to where you want to store the project
- Enter git clone https://github.com/ronanprendiville/smfquant.git
- Go to IntelliJ
- Click open and find the project smfquant and open it.

### Database

Our database is hosted by an AWS server, using the Amazon Relational Database Service (RDS). Our SQL dialect is PostgreSQL.

When you have cloned and opened the project, to access the database click 'database' on right of IntelliJ.
Input credentials (ask me for credentials) and then go SMF Quant DB -> databases -> smfquant -> schemas -> public

### Stock Data

At present our plan is to use Python library 'Pandas' in order to read stock price data from yahoo finance.
For valuation data we will use http requests to access 'Eikon' which is a resource from Thomson Reuters that we have access to as UCC students. This will be a somewhat more technical process but I can go through it with whoever is interested.
