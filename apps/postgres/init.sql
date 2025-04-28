-- Create the users table if not exists
CREATE TABLE IF NOT EXISTS users (
                                     id INT PRIMARY KEY,
                                     name TEXT NOT NULL,
                                     email TEXT NOT NULL
);

-- Insert custom users with specific IDs
INSERT INTO users (id, name, email) VALUES
                                        (1, 'Alice Johnson', 'alice@example.com'),
                                        (2, 'Bob Smith', 'bob@example.com'),
                                        (3, 'Charlie Brown', 'charlie@example.com'),
                                        (10, 'David Miller', 'david@example.com'),
                                        (15, 'Eve Adams', 'eve@example.com'),
                                        (20, 'Frank Turner', 'frank@example.com'),
                                        (25, 'Grace Lee', 'grace@example.com'),
                                        (30, 'Hank Green', 'hank@example.com'),
                                        (35, 'Isabel Wilson', 'isabel@example.com'),
                                        (40, 'Jack White', 'jack@example.com'),
                                        (45, 'Karen Black', 'karen@example.com'),
                                        (50, 'Leo King', 'leo@example.com'),
                                        (55, 'Mona Queen', 'mona@example.com'),
                                        (60, 'Nate Young', 'nate@example.com'),
                                        (65, 'Olivia Moore', 'olivia@example.com'),
                                        (70, 'Paul Walker', 'paul@example.com'),
                                        (75, 'Quincy Harris', 'quincy@example.com'),
                                        (80, 'Rachel Ford', 'rachel@example.com'),
                                        (123, 'Steve Jobs', 'steve@example.com'),
                                        (555, 'Tony Stark', 'tony@example.com');