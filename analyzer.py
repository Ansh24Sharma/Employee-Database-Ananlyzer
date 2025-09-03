"""
Employee data analysis module
"""

import pandas as pd
from typing import Dict, Optional
import logging
from models import EmployeeDatabase

logger = logging.getLogger(__name__)

class EmployeeAnalyzer:
    """Employee data analyzer class"""
    
    def __init__(self, database: EmployeeDatabase):
        """Initialize the analyzer with a database connection."""
        self.db = database
    
    def get_department_stats(self) -> pd.DataFrame:
        """Get statistics by department."""
        query = """
            SELECT department, 
                   COUNT(*) as employee_count,
                   AVG(salary) as avg_salary,
                   MIN(salary) as min_salary,
                   MAX(salary) as max_salary
            FROM employees 
            WHERE status = 'Active'
            GROUP BY department
            ORDER BY employee_count DESC
        """
        return self.db.execute_query(query)
    
    def get_salary_analysis(self) -> Dict:
        """Get comprehensive salary analysis."""
        query = """
            SELECT salary, department, position 
            FROM employees 
            WHERE status = 'Active'
        """
        df = self.db.execute_query(query)
        
        if df.empty:
            return {
                'overall_avg': 0,
                'overall_median': 0,
                'overall_std': 0,
                'by_department': pd.DataFrame(),
                'by_position': pd.DataFrame()
            }
        
        return {
            'overall_avg': df['salary'].mean(),
            'overall_median': df['salary'].median(),
            'overall_std': df['salary'].std(),
            'by_department': df.groupby('department')['salary'].agg(['mean', 'median', 'std']),
            'by_position': df.groupby('position')['salary'].agg(['mean', 'median', 'std'])
        }
    
    def get_performance_analysis(self) -> pd.DataFrame:
        """Analyze employee performance data."""
        query = """
            SELECT e.department, e.position, 
                   AVG(p.performance_score) as avg_performance,
                   COUNT(p.id) as review_count,
                   AVG(p.goals_met) as avg_goals_met
            FROM employees e
            JOIN performance p ON e.id = p.employee_id
            WHERE e.status = 'Active'
            GROUP BY e.department, e.position
            ORDER BY avg_performance DESC
        """
        return self.db.execute_query(query)
    
    def get_attendance_summary(self, start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """Get attendance summary for specified date range."""
        query = """
            SELECT e.id, e.first_name, e.last_name, e.department,
                   AVG(a.hours_worked) as avg_hours,
                   SUM(a.overtime_hours) as total_overtime,
                   COUNT(CASE WHEN a.status = 'Present' THEN 1 END) as days_present,
                   COUNT(a.id) as total_days,
                   ROUND((COUNT(CASE WHEN a.status = 'Present' THEN 1 END) * 100.0 / COUNT(a.id)), 2) as attendance_rate
            FROM employees e
            JOIN attendance a ON e.id = a.employee_id
            WHERE e.status = 'Active'
        """
        
        params = []
        if start_date:
            query += " AND a.date >= %s"
            params.append(start_date)
        if end_date:
            query += " AND a.date <= %s"
            params.append(end_date)
            
        query += " GROUP BY e.id ORDER BY avg_hours DESC"
        
        return self.db.execute_query(query, tuple(params) if params else None)
    
    def get_hiring_trends(self) -> pd.DataFrame:
        """Analyze hiring trends by year and month."""
        query = """
            SELECT YEAR(hire_date) as year,
                   MONTH(hire_date) as month,
                   department,
                   COUNT(*) as hires
            FROM employees
            GROUP BY year, month, department
            ORDER BY year DESC, month DESC
        """
        return self.db.execute_query(query)
    
    def get_top_performers(self, limit: int = 10) -> pd.DataFrame:
        """Get top performing employees."""
        query = """
            SELECT e.id, e.first_name, e.last_name, e.department, e.position,
                   AVG(p.performance_score) as avg_performance,
                   COUNT(p.id) as review_count
            FROM employees e
            JOIN performance p ON e.id = p.employee_id
            WHERE e.status = 'Active'
            GROUP BY e.id
            HAVING review_count >= 2
            ORDER BY avg_performance DESC
            LIMIT %s
        """
        return self.db.execute_query(query, (limit,))
    
    def get_department_performance_comparison(self) -> pd.DataFrame:
        """Compare performance across departments."""
        query = """
            SELECT e.department,
                   AVG(p.performance_score) as avg_performance,
                   COUNT(DISTINCT e.id) as employee_count,
                   COUNT(p.id) as total_reviews,
                   MIN(p.performance_score) as min_score,
                   MAX(p.performance_score) as max_score
            FROM employees e
            JOIN performance p ON e.id = p.employee_id
            WHERE e.status = 'Active'
            GROUP BY e.department
            ORDER BY avg_performance DESC
        """
        return self.db.execute_query(query)
    
    def generate_employee_report(self, employee_id: int) -> Dict:
        """Generate comprehensive report for a specific employee."""
        try:
            # Basic employee info
            employee = self.db.get_employee(employee_id)
            if not employee:
                return {"error": "Employee not found"}
            
            # Performance data
            perf_query = """
                SELECT review_date, performance_score, goals_met, comments
                FROM performance 
                WHERE employee_id = %s 
                ORDER BY review_date DESC
            """
            performance = self.db.execute_query(perf_query, (employee_id,))
            
            # Attendance data (last 30 records)
            att_query = """
                SELECT date, hours_worked, overtime_hours, status
                FROM attendance 
                WHERE employee_id = %s 
                ORDER BY date DESC
                LIMIT 30
            """
            attendance = self.db.execute_query(att_query, (employee_id,))
            
            # Calculate metrics safely
            avg_performance = None
            total_reviews = 0
            avg_hours_worked = None
            attendance_rate = None
            
            # Performance metrics
            if not performance.empty:
                try:
                    # Ensure performance_score is numeric
                    performance['performance_score'] = pd.to_numeric(performance['performance_score'], errors='coerce')
                    performance = performance.dropna(subset=['performance_score'])
                    
                    if not performance.empty:
                        avg_performance = float(performance['performance_score'].mean())
                        total_reviews = len(performance)
                except Exception as e:
                    logger.error(f"Error processing performance data: {e}")
            
            # Attendance metrics
            if not attendance.empty:
                try:
                    # Ensure hours_worked is numeric
                    attendance['hours_worked'] = pd.to_numeric(attendance['hours_worked'], errors='coerce')
                    attendance = attendance.dropna(subset=['hours_worked'])
                    
                    if not attendance.empty:
                        avg_hours_worked = float(attendance['hours_worked'].mean())
                        present_days = len(attendance[attendance['status'] == 'Present'])
                        total_days = len(attendance)
                        if total_days > 0:
                            attendance_rate = (present_days / total_days) * 100
                except Exception as e:
                    logger.error(f"Error processing attendance data: {e}")
            
            return {
                'employee_info': employee,
                'performance_reviews': performance.to_dict('records') if not performance.empty else [],
                'recent_attendance': attendance.to_dict('records') if not attendance.empty else [],
                'metrics': {
                    'avg_performance': avg_performance,
                    'total_reviews': total_reviews,
                    'avg_hours_worked': avg_hours_worked,
                    'attendance_rate': attendance_rate
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating employee report: {e}")
            return {"error": str(e)}
    
    def get_salary_budget_by_department(self) -> pd.DataFrame:
        """Calculate total salary budget by department."""
        query = """
            SELECT department,
                   COUNT(*) as employee_count,
                   SUM(salary) as total_budget,
                   AVG(salary) as avg_salary,
                   MIN(salary) as min_salary,
                   MAX(salary) as max_salary
            FROM employees
            WHERE status = 'Active'
            GROUP BY department
            ORDER BY total_budget DESC
        """
        return self.db.execute_query(query)
    
    def get_employee_tenure_analysis(self) -> pd.DataFrame:
        """Analyze employee tenure."""
        query = """
            SELECT id, first_name, last_name, department, position,
                   hire_date,
                   DATEDIFF(CURDATE(), hire_date) as days_employed,
                   ROUND(DATEDIFF(CURDATE(), hire_date) / 365.25, 1) as years_employed
            FROM employees
            WHERE status = 'Active'
            ORDER BY days_employed DESC
        """
        return self.db.execute_query(query)