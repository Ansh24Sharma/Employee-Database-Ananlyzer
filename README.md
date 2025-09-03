# Employee Management System

A comprehensive Employee Database Analyzer built with Python and MySQL that provides data analysis, visualization, and reporting capabilities for employee management.

## Features

- **Employee Management**: Add, update, and manage employee records
- **Performance Tracking**: Track and analyze employee performance reviews
- **Attendance Management**: Monitor employee attendance and working hours
- **Data Analytics**: Comprehensive analysis of employee data including:
  - Department statistics
  - Salary analysis
  - Performance trends
  - Attendance summaries
  - Budget analysis
- **Visualizations**: Generate various charts and graphs including:
  - Department distribution
  - Salary distributions
  - Performance trends
  - Attendance heatmaps
  - Comprehensive dashboards
- **Reporting**: Generate detailed employee reports
- **Sample Data Generation**: Automatically generate realistic sample data for testing

## Project Structure

```
employee-management-system/
├── config.py              # Database configuration and queries
├── models.py              # Database models and connection management
├── analyzer.py            # Data analysis module
├── visualization.py       # Data visualization module
├── data_generator.py      # Sample data generation
├── main.py               # Main application entry point
├── requirements.txt      # Project dependencies
├── .env.template        # Environment variables template
├── README.md           # Project documentation
└── plots/              # Generated visualization plots (created automatically)
```

## Installation

### Prerequisites

- Python 3.8 or higher
- MySQL Server 5.7 or higher
- pip (Python package manager)

### Setup Instructions

1. **Clone or download the project files**

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up MySQL database**:
   - Install MySQL Server if not already installed
   - Create a database named `employee_db` (or your preferred name)
   - Create a MySQL user with appropriate privileges

4. **Configure environment variables**:
   - Copy `.env.template` to `.env`
   - Update the database connection details in `.env`:
   ```
   DB_HOST=localhost
   DB_PORT=3306
   DB_USER=your_mysql_username
   DB_PASSWORD=your_mysql_password
   DB_NAME=employee_db
   ```

5. **Run the application**:
   ```bash
   python main.py
   ```

## Usage

### Interactive Mode (Default)

Run the application and navigate through the interactive menu:

```bash
python main.py
```

The interactive menu provides options to:
- View various analytics reports
- Generate visualizations
- Create individual employee reports
- Generate new sample data

### Batch Mode

Run complete analysis and generate all visualizations automatically:

```bash
python main.py --batch
```

This will:
- Run all analysis reports
- Generate and save all visualizations to the `plots/` directory

## Database Schema

The system uses three main tables:

### `employees`
- `id` (Primary Key)
- `first_name`, `last_name`
- `email` (Unique)
- `department`, `position`
- `salary`
- `hire_date`, `birth_date`
- `phone`, `status`
- `created_at`, `updated_at`

### `performance`
- `id` (Primary Key)
- `employee_id` (Foreign Key)
- `review_date`
- `performance_score` (1.0-5.0)
- `goals_met`
- `comments`

### `attendance`
- `id` (Primary Key)
- `employee_id` (Foreign Key)
- `date`
- `hours_worked`, `overtime_hours`
- `status` (Present, Absent, Late, Half Day)

## Key Features Explained

### Data Analysis
- **Department Statistics**: Employee counts, salary ranges by department
- **Salary Analysis**: Comprehensive salary statistics and comparisons
- **Performance Analysis**: Performance scoring and trending
- **Attendance Analysis**: Attendance rates, average hours, overtime tracking
- **Budget Analysis**: Salary budget breakdown by department

### Visualizations
- **Department Distribution**: Bar charts showing employee distribution
- **Salary Distribution**: Histograms, box plots, and violin plots for salary data
- **Performance Trends**: Line charts showing performance over time
- **Attendance Heatmaps**: Visual representation of attendance patterns
- **Comprehensive Dashboard**: Multi-panel overview of all key metrics

### Sample Data Generation
The system can automatically generate realistic sample data including:
- 50+ employees across 6 departments
- Multiple performance reviews per employee
- 90 days of attendance records
- Realistic salary ranges based on position levels

## API Reference

### Core Classes

#### `EmployeeDatabase`
Main database interface for CRUD operations.

```python
db = EmployeeDatabase()

# Add employee
emp_id = db.add_employee("John", "Doe", "john.doe@company.com", 
                        "Engineering", "Software Engineer", 75000, "2024-01-15")

# Get employee
employee = db.get_employee(emp_id)

# Update employee
db.update_employee(emp_id, salary=80000, position="Senior Software Engineer")
```

#### `EmployeeAnalyzer`
Data analysis and reporting.

```python
analyzer = EmployeeAnalyzer(db)

# Get department statistics
dept_stats = analyzer.get_department_stats()

# Get salary analysis
salary_analysis = analyzer.get_salary_analysis()

# Generate employee report
report = analyzer.generate_employee_report(emp_id)
```

#### `EmployeeVisualization`
Generate charts and visualizations.

```python
viz = EmployeeVisualization(analyzer)

# Plot department distribution
viz.plot_department_distribution()

# Create comprehensive dashboard
viz.create_dashboard("dashboard.png")
```

## Configuration

### Database Configuration
Update `config.py` or use environment variables:

```python
DB_HOST=localhost
DB_PORT=3306
DB_USER=your_username
DB_PASSWORD=your_password
DB_NAME=employee_db
```

### Logging Configuration
The system logs important events and errors. Logs are written to:
- Console output
- `employee_system.log` file

## Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Verify MySQL server is running
   - Check database credentials in `.env` file
   - Ensure database exists and user has proper privileges

2. **Missing Dependencies**
   - Run `pip install -r requirements.txt`
   - Ensure Python 3.8+ is installed

3. **Visualization Issues**
   - Install required plotting libraries: `matplotlib`, `seaborn`
   - For headless servers, set matplotlib backend: `export MPLBACKEND=Agg`

4. **Sample Data Generation Fails**
   - Check database connection
   - Ensure tables are created properly
   - Verify database user has INSERT privileges

### Performance Tips

- For large datasets, consider adding database indexes
- Use batch operations for bulk data insertion
- Limit visualization data for better performance

## Contributing

1. Follow PEP 8 style guidelines
2. Add appropriate error handling and logging
3. Update documentation for new features
4. Test thoroughly with sample data

## License

This project is open source and available under the MIT License.

## Support

For questions or issues:
1. Check the troubleshooting section
2. Review the logs in `employee_system.log`
3. Ensure all dependencies are correctly installed