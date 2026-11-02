RECURRING DEPOSIT MANAGEMENT SYSTEM

Requirements: Python 3.10 or newer and an internet connection for the first installation.

WINDOWS SETUP
1. Extract this ZIP into a normal folder (for example, Documents\Recurring_Deposit_Management_Website).
2. Open that folder in Visual Studio Code.
3. In VS Code, select Terminal > New Terminal.
4. Run these commands one at a time:
   py -m venv .venv
   .venv\Scripts\activate
   py -m pip install -r requirements.txt
   py app.py
5. Open http://127.0.0.1:5000 in your browser.
6. Keep the terminal open while using the website. Press Ctrl+C in the terminal to stop it.

The app stores local demo records in rd_management.db in this folder. It is a student project/demo, not real banking software. The maturity calculator uses an approximate recurring-deposit formula; actual bank calculations can differ.
