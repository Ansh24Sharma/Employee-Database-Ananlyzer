import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from typing import Optional
import logging
from analyzer import EmployeeAnalyzer

logger = logging.getLogger(__name__)

class EmployeeVisualization:
    """Employee data visualization class"""
    
    def __init__(self, analyzer: EmployeeAnalyzer):
        """Initialize visualization with analyzer."""
        self.analyzer = analyzer
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
        
        # Set default figure parameters
        plt.rcParams['figure.figsize'] = (12, 8)
        plt.rcParams['font.size'] = 10
    
    def plot_department_distribution(self, save_path: Optional[str] = None) -> None:
        """Plot employee distribution by department."""
        try:
            dept_stats = self.analyzer.get_department_stats()
            
            if dept_stats.empty:
                logger.warning("No department data available for visualization")
                return
            
            plt.figure(figsize=(12, 8))
            
            # Create bar plot
            bars = plt.bar(dept_stats['department'], dept_stats['employee_count'], 
                          color='skyblue', alpha=0.8, edgecolor='navy', linewidth=1.2)
            
            # Customize plot
            plt.title('Employee Distribution by Department', fontsize=18, fontweight='bold', pad=20)
            plt.xlabel('Department', fontsize=14, fontweight='bold')
            plt.ylabel('Number of Employees', fontsize=14, fontweight='bold')
            plt.xticks(rotation=45, ha='right')
            
            # Add value labels on bars
            for bar in bars:
                height = bar.get_height()
                plt.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                        f'{int(height)}', ha='center', va='bottom', fontweight='bold')
            
            # Add grid
            plt.grid(axis='y', alpha=0.3, linestyle='--')
            plt.tight_layout()
            
            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
                logger.info(f"Department distribution plot saved to {save_path}")
            
            plt.show()
            
        except Exception as e:
            logger.error(f"Error creating department distribution plot: {e}")
    
    def plot_salary_distribution(self, save_path: Optional[str] = None) -> None:
        """Plot salary distribution with multiple views."""
        try:
            query = """
                SELECT salary, department, position 
                FROM employees 
                WHERE status = 'Active'
            """
            df = self.analyzer.db.execute_query(query)
            
            if df.empty:
                logger.warning("No salary data available for visualization")
                return
            
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
            
            # 1. Overall salary histogram
            ax1.hist(df['salary'], bins=20, alpha=0.7, color='lightgreen', 
                    edgecolor='darkgreen', linewidth=1)
            ax1.set_title('Overall Salary Distribution', fontsize=14, fontweight='bold')
            ax1.set_xlabel('Salary ($)')
            ax1.set_ylabel('Frequency')
            ax1.axvline(df['salary'].mean(), color='red', linestyle='--', linewidth=2,
                       label=f'Mean: ${df["salary"].mean():.0f}')
            ax1.axvline(df['salary'].median(), color='orange', linestyle='--', linewidth=2,
                       label=f'Median: ${df["salary"].median():.0f}')
            ax1.legend()
            ax1.grid(alpha=0.3)
            
            # 2. Box plot by department
            dept_order = df.groupby('department')['salary'].median().sort_values(ascending=False).index
            sns.boxplot(data=df, x='department', y='salary', order=dept_order, ax=ax2)
            ax2.set_title('Salary Distribution by Department', fontsize=14, fontweight='bold')
            ax2.set_xlabel('Department')
            ax2.set_ylabel('Salary ($)')
            ax2.tick_params(axis='x', rotation=45)
            
            # 3. Violin plot by department
            sns.violinplot(data=df, x='department', y='salary', order=dept_order, ax=ax3)
            ax3.set_title('Salary Density by Department', fontsize=14, fontweight='bold')
            ax3.set_xlabel('Department')
            ax3.set_ylabel('Salary ($)')
            ax3.tick_params(axis='x', rotation=45)
            
            # 4. Department vs Average Salary
            dept_avg = df.groupby('department')['salary'].mean().sort_values(ascending=True)
            bars = ax4.barh(range(len(dept_avg)), dept_avg.values, color='coral', alpha=0.8)
            ax4.set_yticks(range(len(dept_avg)))
            ax4.set_yticklabels(dept_avg.index)
            ax4.set_title('Average Salary by Department', fontsize=14, fontweight='bold')
            ax4.set_xlabel('Average Salary ($)')
            
            # Add value labels
            for i, bar in enumerate(bars):
                width = bar.get_width()
                ax4.text(width + 1000, bar.get_y() + bar.get_height()/2,
                        f'${width:.0f}', ha='left', va='center', fontweight='bold')
            
            plt.tight_layout()
            
            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
                logger.info(f"Salary distribution plot saved to {save_path}")
            
            plt.show()
            
        except Exception as e:
            logger.error(f"Error creating salary distribution plot: {e}")
    
    def plot_performance_trends(self, save_path: Optional[str] = None) -> None:
        """Plot performance trends over time."""
        try:
            query = """
                SELECT e.department, p.review_date, p.performance_score,
                       DATE_FORMAT(p.review_date, '%Y-%m') as year_month
                FROM employees e
                JOIN performance p ON e.id = p.employee_id
                WHERE e.status = 'Active'
                ORDER BY p.review_date
            """
            perf_data = self.analyzer.db.execute_query(query)
            
            if perf_data.empty:
                logger.warning("No performance data available for visualization")
                return
            
            plt.figure(figsize=(14, 8))
            
            # Plot trends by department
            for dept in perf_data['department'].unique():
                dept_data = perf_data[perf_data['department'] == dept]
                monthly_avg = dept_data.groupby('year_month')['performance_score'].mean()
                
                plt.plot(monthly_avg.index, monthly_avg.values, 
                        marker='o', label=dept, linewidth=2.5, markersize=6)
            
            plt.title('Performance Trends by Department', fontsize=18, fontweight='bold', pad=20)
            plt.xlabel('Month', fontsize=14, fontweight='bold')
            plt.ylabel('Average Performance Score', fontsize=14, fontweight='bold')
            plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
            plt.xticks(rotation=45)
            plt.grid(True, alpha=0.3, linestyle='--')
            plt.ylim(1, 5)
            
            # Add horizontal line for average
            overall_avg = perf_data['performance_score'].mean()
            plt.axhline(y=overall_avg, color='red', linestyle='--', alpha=0.7,
                       label=f'Overall Average: {overall_avg:.2f}')
            
            plt.tight_layout()
            
            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
                logger.info(f"Performance trends plot saved to {save_path}")
            
            plt.show()
            
        except Exception as e:
            logger.error(f"Error creating performance trends plot: {e}")
    
    def plot_attendance_heatmap(self, start_date: str, end_date: str, 
                               save_path: Optional[str] = None) -> None:
        """Create attendance heatmap."""
        try:
            query = """
                SELECT e.first_name, e.last_name, a.date, a.status
                FROM employees e
                JOIN attendance a ON e.id = a.employee_id
                WHERE e.status = 'Active' AND a.date BETWEEN %s AND %s
                ORDER BY e.last_name, e.first_name, a.date
            """
            att_data = self.analyzer.db.execute_query(query, (start_date, end_date))
            
            if att_data.empty:
                logger.warning("No attendance data available for the specified period")
                return
            
            # Create employee names and pivot data
            att_data['employee'] = att_data['first_name'] + ' ' + att_data['last_name']
            att_data['date'] = pd.to_datetime(att_data['date'])
            att_data['status_code'] = att_data['status'].map({
                'Present': 1, 'Late': 0.5, 'Half Day': 0.3, 'Absent': 0
            })
            
            # Pivot data for heatmap
            pivot_data = att_data.pivot(index='employee', columns='date', values='status_code')
            
            plt.figure(figsize=(16, max(8, len(pivot_data.index) * 0.5)))
            
            # Create heatmap
            sns.heatmap(pivot_data, cmap='RdYlGn', cbar_kws={'label': 'Attendance Status'},
                       linewidths=0.5, annot=False, fmt='.1f',
                       xticklabels=[d.strftime('%m-%d') for d in pivot_data.columns])
            
            plt.title(f'Employee Attendance Heatmap ({start_date} to {end_date})', 
                     fontsize=16, fontweight='bold', pad=20)
            plt.xlabel('Date', fontsize=12, fontweight='bold')
            plt.ylabel('Employee', fontsize=12, fontweight='bold')
            plt.xticks(rotation=45)
            plt.yticks(rotation=0)
            
            # Add custom colorbar labels
            cbar = plt.gca().collections[0].colorbar
            cbar.set_ticks([0, 0.3, 0.5, 1])
            cbar.set_ticklabels(['Absent', 'Half Day', 'Late', 'Present'])
            
            plt.tight_layout()
            
            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
                logger.info(f"Attendance heatmap saved to {save_path}")
            
            plt.show()
            
        except Exception as e:
            logger.error(f"Error creating attendance heatmap: {e}")
    
    def plot_hiring_trends(self, save_path: Optional[str] = None) -> None:
        """Plot hiring trends over time."""
        try:
            hiring_data = self.analyzer.get_hiring_trends()
            
            if hiring_data.empty:
                logger.warning("No hiring data available for visualization")
                return
            
            # Create year-month column
            hiring_data['year_month'] = (hiring_data['year'].astype(str) + '-' + 
                                       hiring_data['month'].astype(str).str.zfill(2))
            
            plt.figure(figsize=(14, 8))
            
            # Plot hiring trends by department
            for dept in hiring_data['department'].unique():
                dept_data = hiring_data[hiring_data['department'] == dept]
                monthly_hires = dept_data.groupby('year_month')['hires'].sum()
                
                plt.plot(monthly_hires.index, monthly_hires.values,
                        marker='o', label=dept, linewidth=2, markersize=5)
            
            plt.title('Hiring Trends by Department', fontsize=18, fontweight='bold', pad=20)
            plt.xlabel('Month', fontsize=14, fontweight='bold')
            plt.ylabel('Number of Hires', fontsize=14, fontweight='bold')
            plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
            plt.xticks(rotation=45)
            plt.grid(True, alpha=0.3, linestyle='--')
            
            plt.tight_layout()
            
            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
                logger.info(f"Hiring trends plot saved to {save_path}")
            
            plt.show()
            
        except Exception as e:
            logger.error(f"Error creating hiring trends plot: {e}")
    
    def plot_performance_distribution(self, save_path: Optional[str] = None) -> None:
        """Plot performance score distribution."""
        try:
            query = """
                SELECT e.department, p.performance_score
                FROM employees e
                JOIN performance p ON e.id = p.employee_id
                WHERE e.status = 'Active'
            """
            perf_data = self.analyzer.db.execute_query(query)
            
            if perf_data.empty:
                logger.warning("No performance data available for visualization")
                return
            
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
            
            # Overall distribution
            ax1.hist(perf_data['performance_score'], bins=20, alpha=0.7, 
                    color='lightblue', edgecolor='navy')
            ax1.set_title('Overall Performance Score Distribution', fontsize=14, fontweight='bold')
            ax1.set_xlabel('Performance Score')
            ax1.set_ylabel('Frequency')
            ax1.axvline(perf_data['performance_score'].mean(), color='red', 
                       linestyle='--', label=f'Mean: {perf_data["performance_score"].mean():.2f}')
            ax1.legend()
            ax1.grid(alpha=0.3)
            
            # By department
            sns.boxplot(data=perf_data, x='department', y='performance_score', ax=ax2)
            ax2.set_title('Performance Score by Department', fontsize=14, fontweight='bold')
            ax2.set_xlabel('Department')
            ax2.set_ylabel('Performance Score')
            ax2.tick_params(axis='x', rotation=45)
            
            plt.tight_layout()
            
            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
                logger.info(f"Performance distribution plot saved to {save_path}")
            
            plt.show()
            
        except Exception as e:
            logger.error(f"Error creating performance distribution plot: {e}")
    
    def create_dashboard(self, save_path: Optional[str] = None) -> None:
        """Create a comprehensive dashboard with multiple visualizations."""
        try:
            fig = plt.figure(figsize=(20, 15))
            
            # 1. Department distribution
            ax1 = plt.subplot(2, 3, 1)
            dept_stats = self.analyzer.get_department_stats()
            if not dept_stats.empty:
                bars = ax1.bar(dept_stats['department'], dept_stats['employee_count'], 
                              color='skyblue', alpha=0.7)
                ax1.set_title('Employee Count by Department', fontweight='bold')
                ax1.set_xticklabels(dept_stats['department'], rotation=45)
                for bar in bars:
                    height = bar.get_height()
                    ax1.text(bar.get_x() + bar.get_width()/2., height,
                            f'{int(height)}', ha='center', va='bottom')
            
            # 2. Salary distribution
            ax2 = plt.subplot(2, 3, 2)
            salary_data = self.analyzer.db.execute_query(
                "SELECT salary FROM employees WHERE status = 'Active'")
            if not salary_data.empty:
                ax2.hist(salary_data['salary'], bins=15, alpha=0.7, color='lightgreen')
                ax2.set_title('Salary Distribution', fontweight='bold')
                ax2.set_xlabel('Salary')
                ax2.axvline(salary_data['salary'].mean(), color='red', linestyle='--')
            
            # 3. Performance trends
            ax3 = plt.subplot(2, 3, 3)
            perf_trends = self.analyzer.get_department_performance_comparison()
            if not perf_trends.empty:
                bars = ax3.bar(perf_trends['department'], perf_trends['avg_performance'], 
                              color='orange', alpha=0.7)
                ax3.set_title('Average Performance by Department', fontweight='bold')
                ax3.set_xticklabels(perf_trends['department'], rotation=45)
                ax3.set_ylim(1, 5)
            
            # 4. Budget by department
            ax4 = plt.subplot(2, 3, 4)
            budget_data = self.analyzer.get_salary_budget_by_department()
            if not budget_data.empty:
                ax4.pie(budget_data['total_budget'], labels=budget_data['department'], 
                       autopct='%1.1f%%', startangle=90)
                ax4.set_title('Salary Budget Distribution', fontweight='bold')
            
            # 5. Top performers
            ax5 = plt.subplot(2, 3, 5)
            top_perf = self.analyzer.get_top_performers(5)
            if not top_perf.empty:
                names = [f"{row['first_name']} {row['last_name']}" for _, row in top_perf.iterrows()]
                bars = ax5.barh(names, top_perf['avg_performance'], color='gold', alpha=0.8)
                ax5.set_title('Top 5 Performers', fontweight='bold')
                ax5.set_xlabel('Average Performance Score')
                ax5.set_xlim(1, 5)
            
            # 6. Tenure analysis
            ax6 = plt.subplot(2, 3, 6)
            tenure_data = self.analyzer.get_employee_tenure_analysis()
            if not tenure_data.empty:
                ax6.hist(tenure_data['years_employed'], bins=15, alpha=0.7, color='purple')
                ax6.set_title('Employee Tenure Distribution', fontweight='bold')
                ax6.set_xlabel('Years Employed')
                ax6.set_ylabel('Number of Employees')
            
            plt.suptitle('Employee Analytics Dashboard', fontsize=20, fontweight='bold', y=0.95)
            plt.tight_layout()
            
            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
                logger.info(f"Dashboard saved to {save_path}")
            
            plt.show()
            
        except Exception as e:
            logger.error(f"Error creating dashboard: {e}")