# Personal Finance Manager

A desktop-based Personal Finance Manager built with Python that helps users organize, track, and visualize their personal financial activities in one application.

The project was developed as a practical application of Python programming, GUI development, database management, financial data handling, and data visualization.

---

## 📌 Overview

Managing personal finances often involves keeping track of income, expenses, savings, debts, investments, and other financial commitments across multiple applications or spreadsheets.

The **Personal Finance Manager** aims to bring these activities together into a single desktop application.

The application provides a graphical interface through which users can manage their financial information, record transactions, monitor savings, track debts, maintain fixed deposits, and visualize financial activity.

The project was developed with a focus on creating a practical application while applying core concepts of Python, GUI programming, databases, data structures, and software design.

---

## ✨ Features

### 👤 User Management

- User registration and login
- Individual user data management
- User-specific financial records
- Separation of financial information between users

### 💰 Income & Expense Management

Users can record and manage their financial transactions.

Typical transaction information includes:

- Transaction type
- Amount
- Category
- Date
- Description

This allows users to maintain a structured record of their financial activity.

### 📊 Financial Dashboard

The application provides a central dashboard for viewing important financial information.

Depending on the configured features, the dashboard can display information such as:

- Total income
- Total expenses
- Current savings
- Outstanding debts
- Fixed deposits
- Recent transactions

### 💵 Savings Management

Users can keep track of their savings and monitor how their financial position changes over time.

The application provides a structured way to record and review savings-related information.

### 💳 Debt Management

The application allows users to record and monitor debts.

Information can be maintained regarding:

- Debt amount
- Amount repaid
- Remaining balance
- Relevant dates
- Description or source of the debt

This provides a clearer view of outstanding financial obligations.

### 🏦 Fixed Deposit Management

Users can maintain information about fixed deposits and other savings instruments.

Relevant information can include:

- Principal amount
- Interest-related information
- Start date
- Maturity information
- Deposit details

### 📈 Financial Visualization

Financial information can be represented visually through graphs and charts.

This makes it easier to identify:

- Spending patterns
- Changes in savings
- Income versus expenditure
- Financial trends over time

### 🗄️ Database Management

The application uses a database to persist user and financial information.

Instead of relying only on temporary Python variables, the project stores application data so that it can be accessed across sessions.

---

## 🛠️ Technologies Used

### Programming Language

**Python**

Python is used for the application's core logic, data processing, database interaction, and GUI functionality.

### GUI

**Tkinter / ttkbootstrap**

The graphical interface is built using Python's GUI ecosystem, with `ttkbootstrap` used where applicable to provide a more modern interface and styling.

### Database

**MySQL / SQL**

The database layer is used to store and retrieve persistent financial information.

### Data Visualization

The project uses Python-based visualization tools to represent financial information graphically.

### Development Tools

- Git
- GitHub
- Visual Studio Code
- Python virtual environments

---

## 🏗️ Application Architecture

The project follows a modular structure so that different parts of the application can be developed and maintained independently.

A simplified representation of the application architecture is:

```text
                   ┌──────────────────┐
                   │      User        │
                   └────────┬─────────┘
                            │
                            ▼
                   ┌──────────────────┐
                   │   GUI Interface  │
                   └────────┬─────────┘
                            │
                            ▼
                   ┌──────────────────┐
                   │ Application Logic│
                   └────────┬─────────┘
                            │
              ┌─────────────┼─────────────┐
              │             │             │
              ▼             ▼             ▼
          Transactions     Debts       Savings
              │             │             │
              └─────────────┼─────────────┘
                            │
                            ▼
                   ┌──────────────────┐
                   │     Database     │
                   └──────────────────┘
```

This separation makes the project easier to understand, debug, extend, and maintain.

---

## 📂 Project Structure

A typical project structure can look like:

```text
Personal-Finance-Manager/
│
├── README.md
├── .gitignore
├── main.py
│
├── database/
│   └── ...
│
├── assets/
│   └── ...
│
├── modules/
│   └── ...
│
└── requirements.txt
```

> The exact structure may differ depending on the current implementation of the project.

---

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/YOUR-USERNAME/YOUR-REPOSITORY.git
```

Navigate into the project:

```bash
cd Personal-Finance-Manager
```

---

### 2. Create a virtual environment

Windows:

```bash
python -m venv .venv
```

Activate it:

```bash
.venv\Scripts\activate
```

Linux/macOS:

```bash
python3 -m venv .venv
```

Activate it:

```bash
source .venv/bin/activate
```

---

### 3. Install dependencies

If a `requirements.txt` file is included:

```bash
pip install -r requirements.txt
```

---

### 4. Configure the database

If the project uses MySQL, make sure MySQL is installed and running.

Create the required database and configure the connection details according to the project's database configuration.

**Do not commit database passwords or other sensitive credentials to GitHub.**

Environment variables can be used for sensitive configuration.

Example:

```text
DB_HOST=localhost
DB_USER=your_username
DB_PASSWORD=your_password
DB_NAME=finance_manager
```

Keep credentials inside `.env` or another secure configuration method.

---

## ▶️ Running the Application

After installing the dependencies and configuring the database, run the application's main Python file.

For example:

```bash
python main.py
```

If the project uses another entry-point file, replace `main.py` with the appropriate filename.

---

## 🔐 Security & Privacy

Financial applications can contain sensitive information.

This project should therefore follow basic security practices such as:

- Never committing passwords to GitHub
- Keeping `.env` files out of version control
- Avoiding real personal financial information in demonstration databases
- Using parameterized SQL queries
- Validating user input
- Restricting access to user-specific records

For public demonstrations, use **dummy financial data** rather than real financial information.

---

## 📊 Example Use Cases

The Personal Finance Manager can be used for:

- Recording monthly income
- Tracking daily expenses
- Monitoring savings
- Managing outstanding debts
- Maintaining fixed deposit information
- Reviewing spending patterns
- Viewing financial trends
- Organizing personal financial records

---

## 🎯 Project Objectives

The primary objectives of this project are:

1. Build a practical desktop application using Python.
2. Apply object-oriented and modular programming concepts.
3. Implement persistent data storage using a relational database.
4. Develop a functional graphical user interface.
5. Process and organize financial data.
6. Represent financial information using visualizations.
7. Practice database operations and SQL.
8. Apply software engineering principles to a real-world problem.
9. Build a foundation for developing larger software projects.

---

## 🧠 Concepts Demonstrated

This project demonstrates practical knowledge of:

- Python programming
- Object-oriented programming
- Functions and modules
- Exception handling
- File handling
- GUI development
- Database connectivity
- SQL queries
- CRUD operations
- Data validation
- Data visualization
- Application architecture
- Version control with Git
- GitHub repository management

---

## 🚀 Future Improvements

Possible future improvements include:

- Advanced financial analytics
- Budget planning
- Monthly and yearly financial reports
- Recurring transactions
- Automated expense categorization
- Investment portfolio tracking
- More detailed financial dashboards
- Exporting reports to PDF or Excel
- Data backup and restoration
- Improved authentication and password security
- Cloud synchronization
- Mobile or web version
- AI-assisted financial categorization and insights

---

## 🤖 Potential AI Integration

One possible future direction is integrating AI into the application.

For example, an AI-powered financial assistant could:

```text
User Financial Data
        ↓
Data Analysis
        ↓
AI Assistant
        ↓
┌───────────────────────────┐
│ Spending Analysis         │
│ Category Detection        │
│ Budget Suggestions        │
│ Financial Summaries       │
│ Anomaly Detection         │
└───────────────────────────┘
```

The AI system could summarize spending patterns and help users understand their financial data.

Any such feature would need to prioritize privacy and security, particularly because financial information is sensitive.

---

## 🧪 Testing

Testing should cover important application components such as:

- User registration
- Login functionality
- Transaction creation
- Transaction modification
- Transaction deletion
- Database operations
- Input validation
- Calculations
- Graph generation
- Error handling

Automated tests can be added progressively as the project develops.

---

## 📚 Learning Outcomes

Building this project provided practical experience in moving from individual programming exercises toward a complete software application.

The project combines multiple areas of computer science:

```text
Python
  ↓
Application Logic
  ↓
GUI Development
  ↓
Database
  ↓
Data Processing
  ↓
Visualization
  ↓
Software Engineering
```

Rather than implementing isolated programming exercises, the project demonstrates how these concepts can work together inside a complete application.

---

## 🔮 Future Vision

The long-term goal of the project is to evolve from a basic personal finance application into a more complete financial management platform.

Potential directions include:

- Intelligent financial insights
- Automated categorization
- Advanced analytics
- Personalized dashboards
- Secure cloud synchronization
- AI-assisted financial analysis
- Cross-platform support

The current project provides the foundation for experimenting with these ideas while maintaining a focus on practical software engineering.

---

## 👨‍💻 Author

**Lalith**

Computer Science Engineering Student

Interested in:

- Software Development
- Artificial Intelligence
- Game Development
- AI Agents
- Computer Science
- Technology

---

## 📜 License

This project is intended primarily as an educational and portfolio project.

If a specific open-source license is added to the repository, the terms of that license will apply.

---

## ⭐ Acknowledgements

This project was developed as a practical learning exercise combining programming, databases, GUI development, and software engineering concepts.

---

## 📌 Disclaimer

This application is an educational software project and is **not intended to provide professional financial advice**.

Any financial calculations, analysis, or suggestions generated by the application should be independently verified before being used for real financial decisions.
