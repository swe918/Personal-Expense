# Installing and Importing Necessary Libraries
from faker import Faker
import random
import pandas as pd
import sqlite3
from datetime import datetime
import matplotlib.pyplot as plt
import streamlit as st

fake = Faker()
## Initialize Faker

# Defining Expense Categories and Payment Modes
Category = ["Food", "Education", "Transportation","Subscription","Health","Bills" ]
Payment_Mode = ["UPI", "Cash", "Debit Card", "Credit Card", "Digital wallet"]
Food=["Groceries", "Snack","Restrauant"]
Transportation=["Uber", "Fuel", "Flights"]
Subscription=["Spotify", "Textbook","Netflix"]
Health=["Check up" ,"Illness", "Medicine" ]
Bills=[ "Water Bill", "Electricity Bill", "Wifi"]



#Description of Categories
Description={
    "Food":["Bought groceries", "Bought snacks", "went to Restaurant"],
    "Education":["paid my course fee","Bought stationary", "Bought books"],
    "Transportation":["Paid for Uber ride","Paid for petrol","Paid for flight tickets"],
    "Subscription":["Paid for spotify subscription","Paid for Textbook subscription", "Paid for Netflix subscription"],
    "Health":["Bought medicine","went for check up","Got ill"],

    "Bills":["Paid water bill", "Paid for electricity bill", "paid for wifi"]
}

Other_exp={"Date":fake.date_this_month(),
           "Amount": round(random.uniform(100,2000),2),
           "Cash_back": round(random.uniform(10,50),2)
           }

# Function to Generate Expense Data

def generating_data(year, month,entries=150):
# We need to take 150 enteries for each month , so I added default value as 150
    data=[]
    start_date=datetime(year,month,1)
    end_date=datetime(year,month,28)
    for _ in range(entries):
         Category_selected=random.choice(Category)
         Description_selected=random.choice(Description[Category_selected])

         expenses ={"Date":fake.date_between(start_date=start_date, end_date=end_date),
           "Amount":round(random.uniform(100,6000),2),
           "Cash_back": round(random.uniform(10,50),2),
           "Payment_Mode":random.choice(Payment_Mode),
           "Category":Category_selected,
           "Description":Description_selected
          }
         data.append(expenses)
    return pd.DataFrame(data)
# Generate Monthly DataFrames
Monthly_dfs={month:generating_data(2024,month) for month in range(1,13)}
print(Monthly_dfs[3].head(15))

# Combined in one DataFrame
All_year_expense=pd.concat(Monthly_dfs.values(),
ignore_index=True)
#Concat

print(All_year_expense)
# Convered into CSV file
All_year_expense.to_csv("All_year_expence.csv",index=False)
print("CSV file saved sucessfully")

#IMPORTING sqlite3
import sqlite3
conn=sqlite3.connect("expense_tracker.db")
cursor=conn.cursor()
print("Connected successfully")
#CONNECTION ESTABLISHED


create_table_query = """
CREATE TABLE IF NOT EXISTS expenses (
    Date DATE,
    Category VARCHAR(100),
    Payment_Mode VARCHAR(100),
    Description VARCHAR(150),
    Amount FLOAT,
    Cash_back FLOAT
);
"""
cursor.execute(create_table_query)
print("Table created successfully")

df=pd.read_csv("All_year_expence.csv")
#IMPORTED DATAFRAME INTO SQL
df.to_sql("expenses",conn,
if_exists="append",index=False)

Viewing_quary="SELECT*fROM expenses;"
cursor.execute(Viewing_quary)

for _ in cursor.fetchall():
     print(_)
#QUARIES
#1 WHAT IS THE TOTAL EXPENSE AND AVERAGE EXPENSE OF THE YEAR 2024 ?

Yealy_expense="""
SELECT
      SUM(Amount) AS Total_Expense,
      AVG(Amount) AS Average_Expense,
      SUM(Cash_back) AS Total_Cashback 
FROM expenses;
"""
cursor.execute(Yealy_expense)
for _ in cursor.fetchall():
     print(_)


#2 WHAT IS MY MONTHLY EXPENSE ALONG WITH THE NUMBER OF TRANSACTION?
Monthy_expense="""
Select 
     strftime('%m',Date) AS MONTH,
     COUNT(*) AS Total_Tranasaction,
     ROUND(SUM(Amount),2)AS Monthly_Expense
FROM expenses
GROUP BY strftime('%m',Date)
ORDER BY strftime('%m',Date);"""
cursor.execute(Monthy_expense)
for _ in cursor.fetchall():
     print(_)
#3 WHICH MODE OF PAYMENT I USED MOST GIVE ME THIS INSIGHT BY RANKING THEM.

Mode_of_payment="""
SELECT
   Payment_Mode ,
   SUM(Amount) ,
   COUNT(*) AS Total_Transaction, 
   RANK()OVER (ORDER BY SUM(Amount)DESC) AS RANK
FROM expenses
GROUP BY Payment_Mode 
ORDER BY RANK;
"""
cursor.execute(Mode_of_payment)
for _ in cursor.fetchall():
     print(_)
#4 HOW WAS MY HEALTH THIS YEAR

My_Health="""
SELECT
    strftime('%m', Date) AS Month ,
    COUNT(*) AS Hospital_visit
FROM expenses 
WHERE Category=='Health' 
GROUP BY strftime('%m',Date)
ORDER BY COUNT(*) DESC
;"""
cursor.execute(My_Health)
for _ in cursor.fetchall():
     print(_)

#5 WHAT IS MY AVERAGE EXPENSE YEAR AND AVERAGE CASHBACK FOR EACH MONTH?
Average_expense="""
SELECT 
    strftime('%m',Date) AS MONTH, 
    ROUND(AVG(Amount),2) AS Average_Expense, 
    ROUND(AVG(Cash_Back),2) AS Average_Cashback 
FROM expenses 
GROUP BY MONTH
ORDER BY MONTH
;"""
cursor.execute(Average_expense)
for _ in cursor.fetchall():
     print(_)
#6  WHAT ARE TOP 5 MONTHS IN WHICH I SPENT THE MOST MONEY ?
Most_Expensive_Month="""
Select 
      strftime('%m',Date) AS MONTH,
      COUNT(*) AS Total_Tranasaction,
     ROUND(SUM(Amount),2)AS Monthly_Expense
     RANK()OVER (ORDER BY SUM(Amount)DESC) AS RANK
FROM expenses
GROUP BY MONTH
ORDER BY RANK
LIMIT 5 ;"""
cursor.execute(Monthy_expense)
for _ in cursor.fetchall():
     print(_)
#7 SHOW ME CATEGORY WISE EXPENSE FOR WHOLE YEAR?
Category_wise_expense="""
SELECT
    Category,
    ROUND(SUM(Amount),2),
    ROUND(SUM(Amount)*100/(SELECT SUM(Amount)FROM expenses),2) AS Percentage
FROM expenses
GROUP BY Category
ORDER BY Amount DESC
"""
cursor.execute(Category_wise_expense)
for _ in cursor.fetchall():
     print(_)
#8 HOW MUCH  I SPENT ON FOOD EACH MONTH ?
Food_Expense="""
SELECT 
    Category ,
    Description,
    strftime('%m',Date) AS MONTH,
    COUNT(*) AS No_OF_TRANSACTION,
    ROUND(SUM(Amount),2) AS AMOUNT
FROM expenses
WHERE Category ='Food'
AND (Description LIKE '%groceries%'
OR Description LIKE '%snacks%'
OR Description LIKE '%Restaurant%')
GROUP BY Category , MONTH
ORDER BY MONTH ;
"""
cursor.execute(Food_Expense)
for _ in cursor.fetchall():
     print(_)
#9 LOWEST EXPENSIVE MONTH
Least_Expensive_Month="""
Select 
     strftime('%m',Date) AS MONTH,
     ROUND(MIN(Amount),2) 
FROM expenses 
GROUP BY MONTH
ORDER BY Amount
;"""
cursor.execute(Least_Expensive_Month)
for _ in cursor.fetchall():
     print(_)
 #10 THE DAY I SPENT THE MOST

Day ="""
SELECT
   DATE(Date) AS EXPENSIVE_DAY, 
   SUM(Amount)
FROM expenses
GROUP BY EXPENSIVE_DAY
ORDER BY Amount
LIMIT 1;"""
cursor.execute(Day)
for _ in cursor.fetchall():
     print(_)


# PROJECT QUESTIONS
# # 1. What is the total amount spent in each category?
# 2. What is the total amount spent using each payment mode?
# 3. What is the total cashback received across all transactions?
# 4. Which are the top 5 most expensive categories in terms of spending?
# 5. How much was spent on transportation using different payment modes?
# 6. Which transactions resulted in cashback?
# 7. What is the total spending in each month of the year?
# 8. Which months have the highest spending in categories like "Travel," "Entertainment," or "Gifts"?
# 9. Are there any recurring expenses that occur during specific months of the year 
# (e.g., insurance premiums, property taxes)?
# 10. How much cashback or rewards were earned in each month?
# 11. How has your overall spending changed over time 
# (e.g., increasing, decreasing, remaining stable)?
# 12. What are the typical costs associated with different types of travel 
# (e.g., flights, accommodation, transportation)?
# 13. Are there any patterns in grocery spending 
# (e.g., higher spending on weekends, increased spending during specific seasons)?
# 14. Define High and Low Priority Categories
# 15. Which category contributes the highest percentage of the total spending?
# SOLUTIONS


#ANSWER1:-
Total_amount="""
SELECT
    Category,
    ROUND(SUM(Amount),2)
FROM expenses
GROUP BY Category
ORDER BY SUM(Amount) DESC;
"""
cursor.execute(Total_amount)
for _ in cursor.fetchall():
     print(_)

# ANSWER2:-
# Date DATE,
#     Category VARCHAR(100),
#     Payment_Mode VARCHAR(100),
#     Description VARCHAR(150),
#     Amount FLOAT,
# #     Cash_back FLOAT


Mode_of_payment_used ="""
SELECT Payment_Mode, ROUND(SUM(Amount),2) FROM expenses 
GROUP BY Payment_Mode
ORDER BY SUM(Amount) DESC;"""

cursor.execute(Mode_of_payment_used)
for _ in cursor.fetchall():
     print(_)

# ANSWER=3
Total_Cash_back="""
SELECT
   ROUND(SUM(Cash_back),2) AS TOTAL_CASHBACK,
   COUNT(*) AS TOTAL_TRANSACTIONS
 FROM expenses 
;"""
cursor.execute(Total_Cash_back)
for _ in cursor.fetchall():
     print(_)

#  Which are the top 5 most expensive categories in terms of spending?
Top_Five="""SELECT
    Category,
    ROUND(SUM(Amount),2)
FROM expenses
GROUP BY Category
ORDER BY SUM(Amount) DESC
LIMIT 5;"""
cursor.execute(Top_Five)
for _ in cursor.fetchall():
     print(_)
#5. How much was spent on transportation using different payment modes?
TRANSPORTAION_EXPENSE="""
SELECT Payment_Mode,ROUND(SUM(AMOUNT),2) AS TRANSPORTATION_AMOUNT 
FROM expenses
WHERE Category="Transportation"
GROUP BY Payment_Mode 
ORDER BY TRANSPORTATION_AMOUNT DESC;
"""
cursor.execute(TRANSPORTAION_EXPENSE)
for _ in cursor.fetchall():
     print(_)
# Which transactions resulted in cashback?
GOT_CASH_BACK="""
SELECT
   ROUND(SUM(Cash_back),2) AS TOTAL_CASHBACK,
   COUNT(*) AS TOTAL_TRANSACTIONS
 FROM expenses 
;"""
cursor.execute(GOT_CASH_BACK)
for _ in cursor.fetchall():
     print(_)

# What is the total spending in each month of the year?

Monthy_expenses="""
Select 
     strftime('%m',Date) AS MONTH,
     ROUND(SUM(Amount),2)AS Monthly_Expense
FROM expenses
GROUP BY  MONTH
ORDER BY MONTH;"""
cursor.execute(Monthy_expenses)
for _ in cursor.fetchall():
     print(_)

#Which months have the highest spending in categories like "Travel," "Entertainment," or "Gifts"?
Entertainment_expenses="""
Select 
     strftime('%m',Date) AS MONTH,
     ROUND(SUM(Amount),2)AS Monthly_Expense
FROM expenses
WHERE Category ='Subscription'
AND (Description LIKE '%NEtflix%'
OR Description LIKE '%spotify%')
GROUP BY Category , MONTH
ORDER BY Monthly_Expense DESC ;
"""
cursor.execute(Entertainment_expenses)
for _ in cursor.fetchall():
     print(_)

# 9. Are there any recurring expenses that occur during specific months of the year 
Recurring_expenses="""
Select 
     strftime('%m',Date) AS MONTH,
     Description,
     ROUND(SUM(Amount),2)AS Recurring_Expense
FROM expenses
WHERE Category IN('Subscription' , 'Bills')
GROUP BY  MONTH , Description
ORDER BY MONTH;"""
cursor.execute(Recurring_expenses)
for _ in cursor.fetchall():
     print(_)

# 10. How much cashback or rewards were earned in each month?
CASH_BACK="""
Select 
     strftime('%m',Date) AS MONTH,
     ROUND(SUM(Cash_back),2)AS Total_Cashback
FROM expenses
GROUP BY  MONTH
ORDER BY MONTH;"""
cursor.execute(CASH_BACK)
for _ in cursor.fetchall():
     print(_)
# 11. How has your overall spending changed over time (e.g., increasing, decreasing, remaining stable)?
Overall_expense="""
SELECT
      strftime('%m',Date) AS MONTH,
      ROUND(AVG(Amount),2) AS Average_Expense
FROM expenses;
"""
cursor.execute(Overall_expense)
for _ in cursor.fetchall():
     print(_)
#ITS STABLE SINCE THE AVERAGE IS AROUND 4000 EACH MONTH

# 12. What are the typical costs associated with different types of travel
#  (e.g., flights, accommodation, transportation)?
TRAVEL="""SELECT 
    Category ,
    Description,
    strftime('%m',Date) AS MONTH,
    COUNT(*) AS No_OF_TRANSACTION,
    ROUND(SUM(Amount),2) AS AMOUNT
FROM expenses
WHERE Category ='Transportaion'
AND (Description LIKE '%Uber%'
OR Description LIKE '%flight%')
GROUP BY MONTH, Category, Description
ORDER BY MONTH ASC ;
"""
cursor.execute(TRAVEL)
for _ in cursor.fetchall():
     print(_)
print('TRAVELLING ANALYSIS DONE')

# 13. Are there any patterns in grocery spending 
# (e.g., higher spending on weekends, increased spending during specific seasons)?

Expensive_DAYS="""SELECT CASE strftime('%w', date)
           WHEN '0' THEN 'Sunday'
           WHEN '1' THEN 'Monday'
           WHEN '2' THEN 'Tuesday'
           WHEN '3' THEN 'Wednesday'
           WHEN '4' THEN 'Thursday'
           WHEN '5' THEN 'Friday'
           WHEN '6' THEN 'Saturday'
       END AS day_of_week,
      ROUND(SUM(AMOUNT),2) AS total_spent 
FROM expenses 
WHERE Category = 'Food' AND Description LIKE '%groceries%'
GROUP BY day_of_week 
ORDER BY total_spent DESC;"""
cursor.execute(Expensive_DAYS)
for _ in cursor.fetchall():
     print(_)
## 14. Define High and Low Priority Categories

priorities="""
SELECT 
    Category, 
    ROUND(SUM(Amount),2) AS Total_Spent,
    CASE 
        WHEN Category IN ('Food', 'Health', 'Bills', 'Transportation', 'Education') THEN 'High Priority'
        ELSE 'Low Priority'
    END AS Priority
FROM expenses
GROUP BY Category
ORDER BY Total_Spent DESC;
"""
cursor.execute(priorities)
for _ in cursor.fetchall():
     print(_)
# 15. Which category contributes the highest percentage of the total spending?
Category_expense_percentage="""
SELECT
    Category,
    ROUND(SUM(Amount),2),
    ROUND(SUM(Amount)*100/(SELECT SUM(Amount)FROM expenses),2) AS Percentage
FROM expenses
GROUP BY Category
ORDER BY Percentage DESC
LIMIT 1
"""
cursor.execute(Category_expense_percentage)
for _ in cursor.fetchall():
     print(_)

import matplotlib.pyplot as plt

# Convert Date column to datetime
df["Date"] = pd.to_datetime(df["Date"])

# Extract month for aggregation
df["Month"] = df["Date"].dt.month

#  1. Monthly Expense Trend (Bar Chart)
monthly_expense = df.groupby("Month")["Amount"].sum()

plt.figure(figsize=(10, 5))
monthly_expense.plot(kind="bar", color="skyblue", edgecolor="black")
plt.title("Total Monthly Expense")
plt.xlabel("Month")
plt.ylabel("Total Amount Spent")
plt.xticks(range(12), ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"])
plt.grid(axis="y", linestyle="--", alpha=0.7)
plt.show(block=False)

#  2. Category-wise Spending (Pie Chart)
category_expense = df.groupby("Category")["Amount"].sum()

plt.figure(figsize=(7, 7))
category_expense.plot(kind="pie", autopct="%1.1f%%", colors=plt.cm.Paired.colors, startangle=90)
plt.title("Category-wise Spending")
plt.ylabel("")  # Hide y-axis label
plt.show(block=False)

# 3. Spending Trend Over Time (Line Chart)
daily_expense = df.groupby("Date")["Amount"].sum()

plt.figure(figsize=(12, 5))
daily_expense.plot(kind="line", marker="o", linestyle="-", color="blue", alpha=0.7)
plt.title("Spending Trend Over Time")
plt.xlabel("Date")

plt.ylabel("Total Amount Spent")
plt.grid(axis="both", linestyle="--", alpha=0.5)
plt.show(block=False)


import streamlit as st

# Streamlit App Title
st.title(" Personal Expense Tracker")

# Database Connection
conn = sqlite3.connect("expense_tracker.db")
df = pd.read_sql_query("SELECT * FROM expenses", conn)
df["Date"] = pd.to_datetime(df["Date"])
df["Month"] = df["Date"].dt.month
 # Sidebar Filters
st.sidebar.header("Filter Data")
selected_month = st.sidebar.selectbox("Select Month", options=sorted(df["Month"].unique()))
selected_category = st.sidebar.selectbox("Select Category", options=["All"] + sorted(df["Category"].unique()))

# # Filter Data Based on Selection
filtered_df = df[df["Month"] == selected_month]
if selected_category != "All":
     filtered_df = filtered_df[filtered_df["Category"] == selected_category]

# # Display Filtered Data
st.subheader(f" Expense Data for Month: {selected_month}")
st.dataframe(filtered_df)

# #  Monthly Expense Bar
#  Chart
st.subheader(" Monthly Expense Trend")
monthly_expense = df.groupby("Month")["Amount"].sum()

fig, ax = plt.subplots()
ax.bar(monthly_expense.index, monthly_expense.values, color="skyblue", edgecolor="black")
ax.set_xlabel("Month")
ax.set_ylabel("Total Amount Spent")
ax.set_title("Total Monthly Expense")
ax.set_xticks(range(1, 13))
ax.set_xticklabels(["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"])
ax.grid(axis="y", linestyle="--", alpha=0.7)
st.pyplot(fig)

# #  Category-wise Spending Pie Chart
st.subheader(" Category-wise Spending")
category_expense = df.groupby("Category")["Amount"].sum()

fig, ax = plt.subplots()
ax.pie(category_expense, labels=category_expense.index, autopct="%1.1f%%", colors=plt.cm.Paired.colors, startangle=90)
ax.set_title("Spending by Category")
st.pyplot(fig)

# #  Spending Trend Line Chart
st.subheader(" Spending Trend Over Time")
daily_expense = df.groupby("Date")["Amount"].sum()

fig, ax = plt.subplots()
ax.plot(daily_expense.index, daily_expense.values, marker="o", linestyle="-", color="blue", alpha=0.7) 
ax.set_xlabel("Date")
ax.set_ylabel("Total Amount Spent")
ax.set_title("Spending Trend Over Time")
ax.grid(axis="both", linestyle="--", alpha=0.5)
st.pyplot(fig)

# Close database connection
conn.close()
print("Project Done")