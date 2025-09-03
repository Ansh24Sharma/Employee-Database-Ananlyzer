"""
Database models and connection management for Employee Management System
"""

import pymysql
import pandas as pd
from typing import List, Dict, Optional, Any
from datetime import datetime
import logging
from config import db_config, Queries

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseConnection:
    """Manages MySQL database connections"""
    
    def __init__(self):
        self.config = db_config
        self.connection = None
        
    def connect(self):
        """Establish database connection"""
        try:
            self.connection = pymysql.connect(
                host=self.config.host,
                port=self.config.port,
                user=self.config.user,
                password=self.config.password,
                database=self.config.database,
                charset=self.config.charset,
                autocommit=False,
                cursorclass=pymysql.cursors.DictCursor
            )
            logger.info("Database connection established successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            return False
    
    def disconnect(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            logger.info("Database connection closed")
    
    def get_cursor(self):
        """Get database cursor"""
        if not self.connection:
            self.connect()
        return self.connection.cursor()
    
    def commit(self):
        """Commit transaction"""
        if self.connection:
            self.connection.commit()
    
    def rollback(self):
        """Rollback transaction"""
        if self.connection:
            self.connection.rollback()

class EmployeeDatabase:
    """Employee Database Management Class"""
    
    def __init__(self):
        """Initialize the Employee Database with MySQL connection."""
        self.db_conn = DatabaseConnection()
        self.db_conn.connect()
        self.create_tables()
        
    def create_tables(self):
        """Create the necessary tables for employee data."""
        try:
            cursor = self.db_conn.get_cursor()
            
            # Create tables
            cursor.execute(Queries.CREATE_EMPLOYEES_TABLE)
            cursor.execute(Queries.CREATE_PERFORMANCE_TABLE)
            cursor.execute(Queries.CREATE_ATTENDANCE_TABLE)
            
            self.db_conn.commit()
            logger.info("Database tables created successfully")
            
        except Exception as e:
            logger.error(f"Error creating tables: {e}")
            self.db_conn.rollback()
            raise
        finally:
            cursor.close()
    
    def add_employee(self, first_name: str, last_name: str, email: str, 
                    department: str, position: str, salary: float, 
                    hire_date: str, birth_date: str = None, phone: str = None) -> int:
        """Add a new employee to the database."""
        cursor = self.db_conn.get_cursor()
        try:
            query = """
                INSERT INTO employees (first_name, last_name, email, department, 
                                     position, salary, hire_date, birth_date, phone)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (first_name, last_name, email, department, 
                                 position, salary, hire_date, birth_date, phone))
            self.db_conn.commit()
            employee_id = cursor.lastrowid
            logger.info(f"Employee {first_name} {last_name} added successfully with ID: {employee_id}")
            return employee_id
            
        except pymysql.IntegrityError as e:
            self.db_conn.rollback()
            logger.error(f"Integrity error: {e}")
            raise ValueError(f"Employee with email {email} already exists!")
        except Exception as e:
            self.db_conn.rollback()
            logger.error(f"Error adding employee: {e}")
            raise
        finally:
            cursor.close()
    
    def update_employee(self, employee_id: int, **kwargs) -> bool:
        """Update employee information."""
        valid_fields = ['first_name', 'last_name', 'email', 'department', 
                       'position', 'salary', 'birth_date', 'phone', 'status']
        
        updates = []
        values = []
        
        for field, value in kwargs.items():
            if field in valid_fields:
                updates.append(f"{field} = %s")
                values.append(value)
        
        if not updates:
            return False
            
        cursor = self.db_conn.get_cursor()
        try:
            values.append(employee_id)
            query = f"UPDATE employees SET {', '.join(updates)} WHERE id = %s"
            cursor.execute(query, values)
            self.db_conn.commit()
            
            rows_affected = cursor.rowcount
            logger.info(f"Updated employee ID {employee_id}: {rows_affected} rows affected")
            return rows_affected > 0
            
        except Exception as e:
            self.db_conn.rollback()
            logger.error(f"Error updating employee: {e}")
            raise
        finally:
            cursor.close()
    
    def delete_employee(self, employee_id: int) -> bool:
        """Delete an employee (soft delete by setting status to 'Inactive')."""
        return self.update_employee(employee_id, status='Inactive')
    
    def get_employee(self, employee_id: int) -> Optional[Dict]:
        """Get employee information by ID."""
        cursor = self.db_conn.get_cursor()
        try:
            cursor.execute("SELECT * FROM employees WHERE id = %s", (employee_id,))
            result = cursor.fetchone()
            return result
        except Exception as e:
            logger.error(f"Error fetching employee: {e}")
            return None
        finally:
            cursor.close()
    
    def get_all_employees(self, active_only: bool = True) -> List[Dict]:
        """Get all employees."""
        cursor = self.db_conn.get_cursor()
        try:
            query = "SELECT * FROM employees"
            if active_only:
                query += " WHERE status = 'Active'"
            
            cursor.execute(query)
            results = cursor.fetchall()
            return results
        except Exception as e:
            logger.error(f"Error fetching employees: {e}")
            return []
        finally:
            cursor.close()
    
    def add_performance_review(self, employee_id: int, review_date: str, 
                             performance_score: float, goals_met: int = 0, 
                             comments: str = "") -> int:
        """Add performance review for an employee."""
        cursor = self.db_conn.get_cursor()
        try:
            query = """
                INSERT INTO performance (employee_id, review_date, performance_score, 
                                       goals_met, comments)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(query, (employee_id, review_date, performance_score, 
                                 goals_met, comments))
            self.db_conn.commit()
            review_id = cursor.lastrowid
            logger.info(f"Performance review added for employee {employee_id}")
            return review_id
            
        except Exception as e:
            self.db_conn.rollback()
            logger.error(f"Error adding performance review: {e}")
            raise
        finally:
            cursor.close()
    
    def add_attendance(self, employee_id: int, date: str, hours_worked: float = 8.0,
                      overtime_hours: float = 0.0, status: str = "Present") -> int:
        """Add attendance record for an employee."""
        cursor = self.db_conn.get_cursor()
        try:
            query = """
                INSERT INTO attendance (employee_id, date, hours_worked, 
                                      overtime_hours, status)
                VALUES (%s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                hours_worked = VALUES(hours_worked),
                overtime_hours = VALUES(overtime_hours),
                status = VALUES(status)
            """
            cursor.execute(query, (employee_id, date, hours_worked, 
                                 overtime_hours, status))
            self.db_conn.commit()
            attendance_id = cursor.lastrowid
            return attendance_id
            
        except Exception as e:
            self.db_conn.rollback()
            logger.error(f"Error adding attendance: {e}")
            raise
        finally:
            cursor.close()
    
    def execute_query(self, query: str, params: tuple = None) -> pd.DataFrame:
        """Execute a query and return results as DataFrame"""
        cursor = self.db_conn.get_cursor()
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            # Fetch results
            results = cursor.fetchall()
            
            # If no results, return empty DataFrame
            if not results:
                return pd.DataFrame()
            
            # Convert to DataFrame
            df = pd.DataFrame(results)
            
            # Ensure numeric columns are properly typed
            for col in df.columns:
                if df[col].dtype == 'object':
                    # Try to convert to numeric if possible
                    try:
                        df[col] = pd.to_numeric(df[col], errors='ignore')
                    except:
                        pass
            
            return df
            
        except Exception as e:
            logger.error(f"Error executing query: {e}")
            logger.error(f"Query: {query}")
            if params:
                logger.error(f"Params: {params}")
            return pd.DataFrame()
        finally:
            cursor.close()
    
    def close(self):
        """Close database connection"""
        self.db_conn.disconnect()