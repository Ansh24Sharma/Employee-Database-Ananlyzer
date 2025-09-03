"""
Main application entry point for Employee Management System
"""

import os
import logging
from typing import Optional
import pandas as pd

# Import our modules
from config import db_config
from models import EmployeeDatabase
from analyzer import EmployeeAnalyzer
from visualization import EmployeeVisualization
from data_generator import generate_sample_data

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('employee_system.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class EmployeeManagementSystem:
    """Main application class for Employee Management System"""
    
    def __init__(self):
        """Initialize the Employee Management System."""
        self.db = None
        self.analyzer = None
        self.visualizer = None
        
    def initialize(self) -> bool:
        """Initialize database connection and components."""
        try:
            logger.info("Initializing Employee Management System...")
            
            # Initialize database
            self.db = EmployeeDatabase()
            logger.info("Database connection established")
            
            # Initialize analyzer and visualizer
            self.analyzer = EmployeeAnalyzer(self.db)
            self.visualizer = EmployeeVisualization(self.analyzer)
            
            logger.info("System initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize system: {e}")
            return False
    
    def check_and_populate_data(self, force_regenerate: bool = False) -> None:
        """Check if database has data, populate if empty."""
        try:
            employees = self.db.get_all_employees()
            
            if not employees or force_regenerate:
                if force_regenerate:
                    logger.info("Force regenerating sample data...")
                else:
                    logger.info("No employee data found. Generating sample data...")
                
                # Generate sample data
                result = generate_sample_data(self.db, 50)
                
                logger.info(f"Sample data generated successfully!")
                logger.info(f"- Employees created: {result['employees_created']}")
                logger.info(f"- Departments: {', '.join(result['departments'])}")
                
            else:
                logger.info(f"Found {len(employees)} existing employees in database")
                
        except Exception as e:
            logger.error(f"Error checking/populating data: {e}")
            raise
    
    def display_department_analysis(self) -> None:
        """Display department analysis."""
        print("\n" + "="*60)
        print("DEPARTMENT ANALYSIS")
        print("="*60)
        
        try:
            dept_stats = self.analyzer.get_department_stats()
            if not dept_stats.empty:
                print("\nEmployee Count and Salary Statistics by Department:")
                print("-" * 55)
                for _, row in dept_stats.iterrows():
                    # Safely convert to int/float
                    emp_count = int(float(row['employee_count'])) if pd.notnull(row['employee_count']) else 0
                    avg_salary = float(row['avg_salary']) if pd.notnull(row['avg_salary']) else 0
                    min_salary = float(row['min_salary']) if pd.notnull(row['min_salary']) else 0
                    max_salary = float(row['max_salary']) if pd.notnull(row['max_salary']) else 0
                    
                    print(f"{row['department']:<15} | "
                          f"Employees: {emp_count:<3} | "
                          f"Avg Salary: ${avg_salary:>8,.0f} | "
                          f"Range: ${min_salary:>6,.0f} - ${max_salary:>6,.0f}")
            else:
                print("No department data available.")
                
        except Exception as e:
            logger.error(f"Error in department analysis: {e}")
            print(f"Error displaying department analysis: {e}")
    
    def display_salary_analysis(self) -> None:
        """Display salary analysis."""
        print("\n" + "="*60)
        print("SALARY ANALYSIS")
        print("="*60)
        
        try:
            salary_analysis = self.analyzer.get_salary_analysis()
            
            print(f"\nOverall Salary Statistics:")
            print(f"- Average: ${salary_analysis['overall_avg']:,.2f}")
            print(f"- Median:  ${salary_analysis['overall_median']:,.2f}")
            print(f"- Std Dev: ${salary_analysis['overall_std']:,.2f}")
            
            if not salary_analysis['by_department'].empty:
                print(f"\nSalary by Department:")
                print("-" * 50)
                dept_salary = salary_analysis['by_department']
                for dept in dept_salary.index:
                    try:
                        avg_sal = float(dept_salary.loc[dept, 'mean']) if pd.notnull(dept_salary.loc[dept, 'mean']) else 0
                        med_sal = float(dept_salary.loc[dept, 'median']) if pd.notnull(dept_salary.loc[dept, 'median']) else 0
                        print(f"{dept:<15} | Avg: ${avg_sal:>8,.0f} | "
                              f"Median: ${med_sal:>8,.0f}")
                    except Exception as e:
                        logger.error(f"Error processing department {dept}: {e}")
                        continue
            else:
                print("No salary data available by department.")
                    
        except Exception as e:
            logger.error(f"Error in salary analysis: {e}")
            print(f"Error displaying salary analysis: {e}")
    
    def display_performance_analysis(self) -> None:
        """Display performance analysis."""
        print("\n" + "="*60)
        print("PERFORMANCE ANALYSIS")
        print("="*60)
        
        try:
            perf_analysis = self.analyzer.get_performance_analysis()
            
            if not perf_analysis.empty:
                print("\nPerformance by Department and Position:")
                print("-" * 70)
                for _, row in perf_analysis.head(10).iterrows():
                    print(f"{row['department']:<12} | {row['position']:<20} | "
                          f"Avg Score: {row['avg_performance']:.2f} | "
                          f"Reviews: {int(row['review_count']):<3} | "
                          f"Goals Met: {row['avg_goals_met']:.1f}")
            else:
                print("No performance data available.")
                
            # Top performers
            top_performers = self.analyzer.get_top_performers(5)
            if not top_performers.empty:
                print(f"\nTop 5 Performers:")
                print("-" * 50)
                for _, row in top_performers.iterrows():
                    print(f"{row['first_name']} {row['last_name']:<15} | "
                          f"{row['department']:<12} | "
                          f"Score: {row['avg_performance']:.2f}")
                          
        except Exception as e:
            logger.error(f"Error in performance analysis: {e}")
    
    def display_attendance_analysis(self) -> None:
        """Display attendance analysis."""
        print("\n" + "="*60)
        print("ATTENDANCE ANALYSIS")
        print("="*60)
        
        try:
            # Last 30 days attendance
            from datetime import datetime, timedelta
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=30)
            
            attendance = self.analyzer.get_attendance_summary(
                start_date.strftime('%Y-%m-%d'), 
                end_date.strftime('%Y-%m-%d')
            )
            
            if not attendance.empty:
                print(f"\nAttendance Summary (Last 30 Days):")
                print("-" * 80)
                print(f"{'Name':<20} | {'Department':<12} | {'Avg Hours':<10} | "
                      f"{'Overtime':<9} | {'Attendance Rate':<15}")
                print("-" * 80)
                
                for _, row in attendance.head(10).iterrows():
                    attendance_rate = (row['days_present'] / row['total_days'] * 100) if row['total_days'] > 0 else 0
                    print(f"{row['first_name']} {row['last_name']:<12} | "
                          f"{row['department']:<12} | "
                          f"{row['avg_hours']:<10.1f} | "
                          f"{row['total_overtime']:<9.1f} | "
                          f"{attendance_rate:<15.1f}%")
            else:
                print("No attendance data available for the specified period.")
                
        except Exception as e:
            logger.error(f"Error in attendance analysis: {e}")
    
    def display_employee_report(self, employee_id: Optional[int] = None) -> None:
        """Display individual employee report."""
        print("\n" + "="*60)
        print("INDIVIDUAL EMPLOYEE REPORT")
        print("="*60)
        
        try:
            if employee_id is None:
                # Get first employee as sample
                employees = self.db.get_all_employees()
                if employees:
                    employee_id = employees[0]['id']
                else:
                    print("No employees found.")
                    return
            
            report = self.analyzer.generate_employee_report(employee_id)
            
            if 'error' in report:
                print(f"Error: {report['error']}")
                return
            
            emp_info = report['employee_info']
            metrics = report['metrics']
            
            print(f"\nEmployee Information:")
            print(f"- Name: {emp_info['first_name']} {emp_info['last_name']}")
            print(f"- Department: {emp_info['department']}")
            print(f"- Position: {emp_info['position']}")
            print(f"- Email: {emp_info['email']}")
            print(f"- Salary: ${emp_info['salary']:,.2f}")
            print(f"- Hire Date: {emp_info['hire_date']}")
            print(f"- Status: {emp_info['status']}")
            
            print(f"\nPerformance Metrics:")
            print(f"- Average Performance Score: {metrics['avg_performance']:.2f}" if metrics['avg_performance'] else "- No performance data available")
            print(f"- Total Performance Reviews: {metrics['total_reviews']}")
            print(f"- Average Hours Worked: {metrics['avg_hours_worked']:.1f}" if metrics['avg_hours_worked'] else "- No attendance data available")
            print(f"- Attendance Rate: {metrics['attendance_rate']:.1f}%" if metrics['attendance_rate'] else "- No attendance rate available")
            
            if report['performance_reviews']:
                print(f"\nRecent Performance Reviews:")
                for review in report['performance_reviews'][:3]:
                    print(f"  - {review['review_date']}: Score {review['performance_score']}, Goals Met: {review['goals_met']}")
                    
        except Exception as e:
            logger.error(f"Error generating employee report: {e}")
    
    def generate_visualizations(self, save_plots: bool = False) -> None:
        """Generate and display visualizations."""
        print("\n" + "="*60)
        print("GENERATING VISUALIZATIONS")
        print("="*60)
        
        try:
            output_dir = "plots" if save_plots else None
            if save_plots and not os.path.exists("plots"):
                os.makedirs("plots")
            
            print("\n1. Department Distribution...")
            self.visualizer.plot_department_distribution(
                f"{output_dir}/department_distribution.png" if save_plots else None
            )
            
            print("2. Salary Distribution...")
            self.visualizer.plot_salary_distribution(
                f"{output_dir}/salary_distribution.png" if save_plots else None
            )
            
            print("3. Performance Trends...")
            self.visualizer.plot_performance_trends(
                f"{output_dir}/performance_trends.png" if save_plots else None
            )
            
            print("4. Performance Distribution...")
            self.visualizer.plot_performance_distribution(
                f"{output_dir}/performance_distribution.png" if save_plots else None
            )
            
            print("5. Hiring Trends...")
            self.visualizer.plot_hiring_trends(
                f"{output_dir}/hiring_trends.png" if save_plots else None
            )
            
            print("6. Comprehensive Dashboard...")
            self.visualizer.create_dashboard(
                f"{output_dir}/dashboard.png" if save_plots else None
            )
            
            if save_plots:
                print(f"\nAll plots saved to '{output_dir}/' directory")
                
        except Exception as e:
            logger.error(f"Error generating visualizations: {e}")
    
    def display_budget_analysis(self) -> None:
        """Display budget analysis."""
        print("\n" + "="*60)
        print("BUDGET ANALYSIS")
        print("="*60)
        
        try:
            budget_data = self.analyzer.get_salary_budget_by_department()
            
            if not budget_data.empty:
                total_budget = budget_data['total_budget'].sum()
                
                print(f"\nTotal Company Salary Budget: ${total_budget:,.2f}")
                print("\nBudget Breakdown by Department:")
                print("-" * 70)
                
                for _, row in budget_data.iterrows():
                    percentage = (row['total_budget'] / total_budget) * 100
                    print(f"{row['department']:<15} | "
                          f"Employees: {int(row['employee_count']):<3} | "
                          f"Budget: ${row['total_budget']:>10,.0f} | "
                          f"Percentage: {percentage:>5.1f}%")
            else:
                print("No budget data available.")
                
        except Exception as e:
            logger.error(f"Error in budget analysis: {e}")
    
    def run_complete_analysis(self) -> None:
        """Run complete analysis and display all reports."""
        print("\n" + "="*80)
        print(" " * 25 + "EMPLOYEE MANAGEMENT SYSTEM")
        print(" " * 28 + "COMPREHENSIVE ANALYSIS")
        print("="*80)
        
        try:
            # Display all analyses
            self.display_department_analysis()
            self.display_salary_analysis()
            self.display_budget_analysis()
            self.display_performance_analysis()
            self.display_attendance_analysis()
            self.display_employee_report()
            
            print("\n" + "="*60)
            print("ANALYSIS COMPLETE")
            print("="*60)
            
        except Exception as e:
            logger.error(f"Error running complete analysis: {e}")
    
    def interactive_menu(self) -> None:
        """Display interactive menu for user interaction."""
        while True:
            print("\n" + "="*50)
            print("EMPLOYEE MANAGEMENT SYSTEM - MAIN MENU")
            print("="*50)
            print("1. View Department Analysis")
            print("2. View Salary Analysis")
            print("3. View Performance Analysis")
            print("4. View Attendance Analysis")
            print("5. View Budget Analysis")
            print("6. Generate Employee Report")
            print("7. Generate Visualizations")
            print("8. Run Complete Analysis")
            print("9. Generate New Sample Data")
            print("0. Exit")
            print("-"*50)
            
            try:
                choice = input("Enter your choice (0-9): ").strip()
                
                if choice == '0':
                    print("Exiting Employee Management System. Goodbye!")
                    break
                elif choice == '1':
                    self.display_department_analysis()
                elif choice == '2':
                    self.display_salary_analysis()
                elif choice == '3':
                    self.display_performance_analysis()
                elif choice == '4':
                    self.display_attendance_analysis()
                elif choice == '5':
                    self.display_budget_analysis()
                elif choice == '6':
                    emp_id = input("Enter employee ID (or press Enter for sample): ").strip()
                    emp_id = int(emp_id) if emp_id.isdigit() else None
                    self.display_employee_report(emp_id)
                elif choice == '7':
                    save_choice = input("Save plots to file? (y/N): ").strip().lower()
                    save_plots = save_choice == 'y'
                    self.generate_visualizations(save_plots)
                elif choice == '8':
                    self.run_complete_analysis()
                elif choice == '9':
                    print("Regenerating sample data...")
                    self.check_and_populate_data(force_regenerate=True)
                    print("Sample data regenerated successfully!")
                else:
                    print("Invalid choice. Please try again.")
                    
            except KeyboardInterrupt:
                print("\n\nExiting Employee Management System. Goodbye!")
                break
            except Exception as e:
                logger.error(f"Error in interactive menu: {e}")
                print(f"An error occurred: {e}")
    
    def cleanup(self) -> None:
        """Cleanup resources."""
        if self.db:
            self.db.close()
            logger.info("Database connection closed")

def main():
    """Main function to run the Employee Management System."""
    system = None
    
    try:
        # Initialize system
        system = EmployeeManagementSystem()
        
        if not system.initialize():
            print("Failed to initialize Employee Management System")
            return
        
        # Check and populate data
        system.check_and_populate_data()
        
        # Check if running interactively
        import sys
        if len(sys.argv) > 1 and sys.argv[1] == '--batch':
            # Run batch analysis
            system.run_complete_analysis()
            system.generate_visualizations(save_plots=True)
        else:
            # Run interactive menu
            system.interactive_menu()
    
    except KeyboardInterrupt:
        print("\n\nProgram interrupted by user")
    except Exception as e:
        logger.error(f"Unexpected error in main: {e}")
        print(f"An unexpected error occurred: {e}")
    finally:
        if system:
            system.cleanup()

if __name__ == "__main__":
    main()