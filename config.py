import os
from dataclasses import dataclass

@dataclass
class DatabaseConfig:
    """Database configuration class"""
    host: str = os.getenv('DB_HOST', 'localhost')
    port: int = int(os.getenv('DB_PORT', 3306))
    user: str = os.getenv('DB_USER', 'root')
    password: str = os.getenv('DB_PASSWORD', '')
    database: str = os.getenv('DB_NAME', 'employee_db')
    charset: str = 'utf8mb4'
    
    def get_connection_string(self) -> str:
        """Generate MySQL connection string"""
        return f"mysql+pymysql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}?charset={self.charset}"

# Default configuration instance
db_config = DatabaseConfig()

# SQL Queries
class Queries:
    """Centralized SQL queries"""
    
    CREATE_EMPLOYEES_TABLE = """
        CREATE TABLE IF NOT EXISTS employees (
            id INT AUTO_INCREMENT PRIMARY KEY,
            first_name VARCHAR(100) NOT NULL,
            last_name VARCHAR(100) NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL,
            department VARCHAR(100) NOT NULL,
            position VARCHAR(100) NOT NULL,
            salary DECIMAL(10,2) NOT NULL,
            hire_date DATE NOT NULL,
            birth_date DATE,
            phone VARCHAR(20),
            status ENUM('Active', 'Inactive') DEFAULT 'Active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """
    
    CREATE_PERFORMANCE_TABLE = """
        CREATE TABLE IF NOT EXISTS performance (
            id INT AUTO_INCREMENT PRIMARY KEY,
            employee_id INT NOT NULL,
            review_date DATE NOT NULL,
            performance_score DECIMAL(3,2) CHECK(performance_score >= 1.0 AND performance_score <= 5.0),
            goals_met INT DEFAULT 0,
            comments TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE,
            INDEX idx_employee_review (employee_id, review_date)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """
    
    CREATE_ATTENDANCE_TABLE = """
        CREATE TABLE IF NOT EXISTS attendance (
            id INT AUTO_INCREMENT PRIMARY KEY,
            employee_id INT NOT NULL,
            date DATE NOT NULL,
            hours_worked DECIMAL(4,2) DEFAULT 8.00,
            overtime_hours DECIMAL(4,2) DEFAULT 0.00,
            status ENUM('Present', 'Absent', 'Late', 'Half Day') DEFAULT 'Present',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE,
            UNIQUE KEY unique_employee_date (employee_id, date),
            INDEX idx_date (date)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """