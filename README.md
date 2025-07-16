📘 **README: Reddit Data Pipeline using AWS**

📌 **Project Overview**
This project is a Reddit data pipeline built using AWS to extract posts and comments from subreddits, clean and store them in a PostgreSQL RDS database, and prepare them for trend analysis.

The pipeline runs every 6 hours, fetching new data from Reddit using the PRAW API. It was designed to be cost-effective, scalable, and suitable for a real-time data engineering portfolio.

🚧 Although dashboards were planned using Metabase, AWS costs (EC2, NAT Gateway) led to the dashboard phase being skipped.

🚀 **Features**
⏰ Automated ETL: Scheduled extraction using AWS Lambda + EventBridge

🐍 PRAW API Integration: Python wrapper for Reddit

🗃️ Structured Storage: RDS PostgreSQL schema for posts & comments

🧹 Light Data Cleaning before insertion

🔒 IAM User and Roles and Custom Policies for secured access

🧰 pgAdmin 4 used for data exploration

🌐 Infrastructure manually provisioned via AWS Console

🔧 **Tech Stack**
| Layer         | Tools & Services                                          |
| ------------- | --------------------------------------------------------- |
| Language      | Python, SQL                                               |
| AWS Services  | Lambda, RDS PostgreSQL, EC2, IAM, EventBridge, CloudWatch |
| Libraries     | `praw`, `psycopg2`, `os`, `logging`, `datetime`           |
| Querying      | pgAdmin 4                                                 |
| Visualization | Metabase (planned, not completed)                         |


📊 **Database Schema**

📌 **Table: reddit_posts**
| Field                 | Type                    | Description           |
| --------------------- | ----------------------- | --------------------- |
| post\_id              | varchar(20) (PK)        | Unique Reddit post ID |
| title                 | text                    | Post title            |
| selftext              | text                    | Post body             |
| author                | varchar(50)             | Reddit username       |
| score                 | integer                 | Upvotes count         |
| upvote\_ratio         | double precision        | Ratio of upvotes      |
| url                   | text                    | Link to post          |
| created\_utc          | timestamp with timezone | Time created (UTC)    |
| subreddit             | varchar(20)             | Subreddit name        |
| is\_original\_content | boolean                 | Whether it's original |
| inserted\_at          | timestamp (default now) | Insertion timestamp   |
| last\_updated         | timestamp (default now) | Last update timestamp |


📌 **Table: reddit_comments**
| Field         | Type                    | Description           |
| ------------- | ----------------------- | --------------------- |
| comment\_id   | varchar(20) (PK)        | Comment ID            |
| post\_id      | varchar(20)             | Related post ID (FK)  |
| body          | text                    | Comment content       |
| author        | varchar(50)             | Reddit username       |
| score         | integer                 | Upvotes count         |
| created\_utc  | timestamp with timezone | Time created (UTC)    |
| inserted\_at  | timestamp               | Insertion timestamp   |
| last\_updated | timestamp               | Last update timestamp |


⚙️ **How It Works**
1. Scheduling
AWS EventBridge rule runs every 6 hours

Triggers Lambda function

2. Data Extraction (Lambda + PRAW)
Fetches recent posts and comments from selected subreddits

Parses and prepares the data for insertion

3. Data Storage (RDS Postgres)
Connects to AWS RDS PostgreSQL instance via psycopg2

Inserts data into structured tables reddit_posts and reddit_comments

4. Querying
Data accessed and verified via pgAdmin4

Metabase was intended for dashboards, but not completed due to EC2 cost

🔒 **IAM & Security**
A custom IAM Role was created for the Lambda function, granting access to:

Lambda, RDS, CloudWatch, EC2

An IAM User was also created for local development, testing, and CLI access, with permissions for:

CloudWatch, Lambda, EC2, RDS, EventBridge, CLI/Programmatic Access

RDS connection was configured to be outside the VPC, simplifying connectivity from services like Lambda and external tools (e.g., pgAdmin).

📈** Visualization Plan (Optional)**
EC2 was used to host Metabase, connected to the RDS DB

Due to rising AWS costs (IPv4 & EC2 charges), the instance was terminated before dashboarding began.

💸 **Cost Breakdown**
Most services were under Free Tier

Additional charges:

April: $1.73 (NAT Gateway + Public IPv4)

June: $6.21 (EC2 + IPv4)

Project was shut down to prevent unnecessary costs.
