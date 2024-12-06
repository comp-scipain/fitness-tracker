from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db

router = APIRouter (
    prefix="/departments",
    tags=["departments"],
    dependencies=[Depends(auth.get_api_key)],
)

class Department(BaseModel):
    name: str
    basePay: float
    population: int


@router.post("/new")
def add_new_department(dept_name: str, dept_basePay: float):
    """
    Add a new department to the Database
    """
    if dept_basePay < 0:
        return {"error":"dept_basePay can't be a negative number"}
    print(f"Adding department named {dept_name} with ${dept_basePay} base pay and population {0}.")
    with db.engine.begin() as connection:
        connection.execute(
            sqlalchemy.text("INSERT INTO dept (dept_name, base_pay, dept_populus) VALUES (:name, :pay, :popul)"),
            {"name": dept_name, "pay": dept_basePay, "popul": 0}
        )
        print("Done")
    return {"status": f"Successfully added new department named {dept_name} with a base pay of ${dept_basePay}"}



@router.get("/daily_pay")
def get_total_department_pay(department_name: str):
    """
    Returns the total pay for all employees in the specified department
    """
    with db.engine.begin() as connection:
        result = connection.execute(
            sqlalchemy.text("SELECT ROUND(SUM(pay),2) FROM employees WHERE department = :department_name"),
            {"department_name": department_name}
        ).fetchone()

        if not result or not result[0]:
            raise HTTPException(status_code=404, detail="Department not found or no employees in the department")

        total_pay = result[0]
        
        print(f"Total pay for department {department_name} is: ${total_pay}")
        return {"department": department_name, "total_pay": total_pay}

@router.post("/total_paid")
def get_total_paid_by_department():
    """
    Calculates the total paid value for each employee by multiplying their wage by the days employed,
    and aggregates this total by department.
    """
    try:
        with db.engine.begin() as connection:
            # Execute an optimized query to aggregate totals by department
            history_records = connection.execute(sqlalchemy.text("""
                SELECT in_dept AS department, SUM(days_employed * day_wage) AS total_paid
                FROM history
                GROUP BY in_dept
            """)).fetchall()

            if not history_records:
                raise HTTPException(status_code=404, detail="No history records found")

            formatted_totals = [
                {"department": record["department"], "total_paid": round(record["total_paid"], 2)}
                for record in history_records
            ]

            print(f"Total paid by department: {formatted_totals}")
            return {"status": "OK", "total_paid_by_department": formatted_totals}

    except Exception as e:
        print(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while calculating the total paid by department")


@router.get("/history")
def get_department_history(department_name: str):
    """
    Fetches the employment history of all employees who were in the specified department,
    aggregating the days employed for each employee.
    """
    with db.engine.begin() as connection:
        history_records = connection.execute(
            sqlalchemy.text("SELECT emp_id, emp_name, days_employed, day_wage FROM history WHERE in_dept = :department_name"),
            {"department_name": department_name}
        ).fetchall()

        if not history_records:
            raise HTTPException(status_code=404, detail="No history records found for the specified department")

        employee_history = {}
        for record in history_records:
            emp_id = record[0]
            if emp_id in employee_history:
                employee_history[emp_id]["days_employed"] += record[2]
            else:
                employee_history[emp_id] = {
                    "emp_id": emp_id,
                    "emp_name": record[1],
                    "days_employed": record[2],
                    "day_wage": record[3]
                }

        department_history = list(employee_history.values())

        print(f"Fetched history for department: {department_name}")
        return {"status": "OK", "department_history": department_history}
