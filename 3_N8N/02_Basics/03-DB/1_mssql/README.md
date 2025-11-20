# Prerequisities

1. Create a DB via script (via VSCode extension)

```sql
IF EXISTS (SELECT name FROM sys.databases WHERE name = 'n8n_test_db')
BEGIN
    ALTER DATABASE [n8n_test_db] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    DROP DATABASE [n8n_test_db];
END
CREATE DATABASE [n8n_test_db];
```

2. Create a table via script on db `n8n_test_db`

```sql
CREATE TABLE products (
    id INT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT
);
```

# Steps

1. Run the workflow `3_1_1_MSSQL_Insert`

2. Run the workflow `3_1_2_MSSQL_Select`
