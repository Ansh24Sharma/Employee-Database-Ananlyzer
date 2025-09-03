import random
from datetime import datetime, timedelta
from typing import List, Dict
import logging
from models import EmployeeDatabase

logger = logging.getLogger(__name__)

class DataGenerator:
    """Generates sample data for demonstration purposes"""
    
    def __init__(self, database: EmployeeDatabase):
        self.db = database
        self.departments = ['Engineering', 'Sales', 'Marketing', 'HR', 'Finance', 'Operations']
        
        self.positions = {
            'Engineering': ['Software Engineer', 'Senior Engineer', 'Tech Lead', 'Engineering Manager', 'DevOps Engineer', 'QA Engineer'],
            'Sales': ['Sales Rep', 'Senior Sales Rep', 'Sales Manager', 'VP Sales', 'Account Manager', 'Business Development'],
            'Marketing': ['Marketing Specialist', 'Marketing Manager', 'Content Creator', 'CMO', 'SEO Specialist', 'Brand Manager'],
            'HR': ['HR Specialist', 'HR Manager', 'Recruiter', 'CHRO', 'Training Coordinator', 'Compensation Analyst'],
            'Finance': ['Accountant', 'Financial Analyst', 'Finance Manager', 'CFO', 'Auditor', 'Budget Analyst'],
            'Operations': ['Operations Specialist', 'Operations Manager', 'Logistics Coordinator', 'COO', 'Project Manager', 'Supply Chain Manager']
        }
        
        self.first_names = [
            'John', 'Jane', 'Mike', 'Sarah', 'David', 'Lisa', 'Chris', 'Emily', 
            'Robert', 'Jessica', 'Michael', 'Ashley', 'James', 'Amanda', 'Daniel',
            'Jennifer', 'William', 'Elizabeth', 'Richard', 'Linda', 'Thomas', 'Patricia',
            'Charles', 'Barbara', 'Joseph', 'Susan', 'Christopher', 'Karen', 'Matthew',
            'Nancy', 'Anthony', 'Betty', 'Mark', 'Helen', 'Donald', 'Sandra'
        ]
        
        self.last_names = [
            'Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 
            'Davis', 'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez',
            'Wilson', 'Anderson', 'Thomas', 'Taylor', 'Moore', 'Jackson', 'Martin',
            'Lee', 'Perez', 'Thompson', 'White', 'Harris', 'Sanchez', 'Clark',
            'Ramirez', 'Lewis', 'Robinson', 'Walker', 'Young', 'Allen', 'King'
        ]
    
    def get_salary_range(self, position: str) -> tuple:
        """Get salary range based on position level."""
        if any(title in position for title in ['VP', 'CMO', 'CHRO', 'CFO', 'COO']):
            return (150000, 250000)
        elif 'Manager' in position or 'Lead' in position:
            return (90000, 140000)
        elif 'Senior' in position:
            return (75000, 110000)
        elif any(title in position for title in ['Analyst', 'Specialist', 'Coordinator']):
            return (50000, 80000)
        else:
            return (45000, 75000)
    
    def generate_employees(self, num_employees: int = 50) -> List[int]:
        """Generate sample employees."""
        employee_ids = []
        
        for i in range(num_employees):
            # Generate basic info
            first_name = random.choice(self.first_names)
            last_name = random.choice(self.last_names)
            department = random.choice(self.departments)
            position = random.choice(self.positions[department])
            
            # Generate salary within range
            min_salary, max_salary = self.get_salary_range(position)
            salary = random.randint(min_salary, max_salary)
            
            # Generate unique email
            email = f"{first_name.lower()}.{last_name.lower()}{i}@company.com"
            
            # Generate dates
            hire_date = self.generate_hire_date()
            birth_date = self.generate_birth_date()
            
            # Generate phone
            phone = f"({random.randint(200,999)}) {random.randint(200,999)}-{random.randint(1000,9999)}"
            
            try:
                emp_id = self.db.add_employee(
                    first_name, last_name, email, department, 
                    position, salary, hire_date, birth_date, phone
                )
                employee_ids.append(emp_id)
                logger.info(f"Created employee: {first_name} {last_name} (ID: {emp_id})")
                
            except ValueError as e:
                logger.warning(f"Skipping duplicate employee: {e}")
                continue
        
        return employee_ids
    
    def generate_hire_date(self) -> str:
        """Generate realistic hire date."""
        # Hire dates between 2020 and 2024
        start_date = datetime(2020, 1, 1)
        end_date = datetime(2024, 12, 31)
        
        # Random date within range
        delta = end_date - start_date
        random_days = random.randint(0, delta.days)
        hire_date = start_date + timedelta(days=random_days)
        
        return hire_date.strftime('%Y-%m-%d')
    
    def generate_birth_date(self) -> str:
        """Generate realistic birth date."""
        # Birth dates for working age adults (22-65)
        current_year = datetime.now().year
        birth_year = random.randint(current_year - 65, current_year - 22)
        birth_month = random.randint(1, 12)
        birth_day = random.randint(1, 28)  # Safe for all months
        
        return f"{birth_year}-{birth_month:02d}-{birth_day:02d}"
    
    def generate_performance_reviews(self, employee_ids: List[int]) -> None:
        """Generate performance reviews for employees."""
        for emp_id in employee_ids:
            # Each employee gets 1-4 reviews
            num_reviews = random.randint(1, 4)
            
            for _ in range(num_reviews):
                # Review date within last 2 years
                review_date = self.generate_review_date()
                
                # Performance score (normally distributed around 3.5)
                score = max(1.0, min(5.0, random.normalvariate(3.5, 0.8)))
                score = round(score, 1)
                
                # Goals met (correlated with performance)
                if score >= 4.0:
                    goals = random.randint(7, 10)
                elif score >= 3.0:
                    goals = random.randint(4, 8)
                else:
                    goals = random.randint(1, 5)
                
                # Generate comment
                comments = self.generate_performance_comment(score)
                
                try:
                    self.db.add_performance_review(
                        emp_id, review_date, score, goals, comments
                    )
                except Exception as e:
                    logger.error(f"Error adding performance review: {e}")
    
    def generate_review_date(self) -> str:
        """Generate review date within last 2 years."""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=730)  # 2 years
        
        delta = end_date - start_date
        random_days = random.randint(0, delta.days)
        review_date = start_date + timedelta(days=random_days)
        
        return review_date.strftime('%Y-%m-%d')
    
    def generate_performance_comment(self, score: float) -> str:
        """Generate appropriate performance comment based on score."""
        if score >= 4.5:
            comments = [
                "Exceptional performance, consistently exceeds expectations",
                "Outstanding contributor, demonstrates leadership qualities",
                "Excellent work quality and strong team collaboration"
            ]
        elif score >= 3.5:
            comments = [
                "Good performance, meets most expectations",
                "Solid contributor with room for growth",
                "Reliable employee with consistent output"
            ]
        elif score >= 2.5:
            comments = [
                "Adequate performance, some areas need improvement",
                "Meeting basic requirements but could do better",
                "Shows potential but needs more focus"
            ]
        else:
            comments = [
                "Below expectations, requires significant improvement",
                "Performance issues need immediate attention",
                "Not meeting role requirements, improvement plan needed"
            ]
        
        return random.choice(comments)
    
    def generate_attendance_records(self, employee_ids: List[int], 
                                  days_back: int = 90) -> None:
        """Generate attendance records for employees."""
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days_back)
        
        for emp_id in employee_ids:
            current_date = start_date
            
            while current_date <= end_date:
                # Skip weekends (assuming Monday-Friday work schedule)
                if current_date.weekday() < 5:  # 0-6, where 0 is Monday
                    
                    # 95% chance of being present
                    if random.random() < 0.95:
                        status = 'Present'
                        hours_worked = random.uniform(7.5, 9.0)
                        # 20% chance of overtime when present
                        overtime = random.uniform(0.5, 3.0) if random.random() < 0.2 else 0.0
                    else:
                        # If not present, determine status
                        status_options = ['Absent', 'Late', 'Half Day']
                        weights = [0.6, 0.3, 0.1]  # Absent most likely
                        status = random.choices(status_options, weights=weights)[0]
                        
                        if status == 'Half Day':
                            hours_worked = 4.0
                            overtime = 0.0
                        elif status == 'Late':
                            hours_worked = random.uniform(6.0, 8.0)
                            overtime = 0.0
                        else:  # Absent
                            hours_worked = 0.0
                            overtime = 0.0
                    
                    try:
                        self.db.add_attendance(
                            emp_id, current_date.strftime('%Y-%m-%d'),
                            round(hours_worked, 2), round(overtime, 2), status
                        )
                    except Exception as e:
                        logger.error(f"Error adding attendance record: {e}")
                
                current_date += timedelta(days=1)
    
    def generate_complete_dataset(self, num_employees: int = 50, 
                                days_attendance: int = 90) -> Dict:
        """Generate complete sample dataset."""
        logger.info("Starting sample data generation...")
        
        # Generate employees
        logger.info(f"Generating {num_employees} employees...")
        employee_ids = self.generate_employees(num_employees)
        
        # Generate performance reviews
        logger.info("Generating performance reviews...")
        self.generate_performance_reviews(employee_ids)
        
        # Generate attendance records
        logger.info(f"Generating {days_attendance} days of attendance records...")
        self.generate_attendance_records(employee_ids, days_attendance)
        
        logger.info("Sample data generation completed successfully!")
        
        return {
            'employees_created': len(employee_ids),
            'employee_ids': employee_ids,
            'departments': self.departments,
            'positions': self.positions
        }

def generate_sample_data(db: EmployeeDatabase, num_employees: int = 50) -> Dict:
    """
    Convenience function to generate sample data.
    
    Args:
        db: EmployeeDatabase instance
        num_employees: Number of employees to generate
    
    Returns:
        Dict with generation statistics
    """
    generator = DataGenerator(db)
    return generator.generate_complete_dataset(num_employees)