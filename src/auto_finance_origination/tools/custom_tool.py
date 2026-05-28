from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import psycopg2
import os

class CustomerAgentToolInput(BaseModel):
    query: str = Field(..., description="SQL query to execute")
    params: list = Field(default_factory=list, description="Query parameters")

class CustomerAgentTool(BaseTool):
    name: str = "CustomerAgentTool"
    description: str = "Tool to retrieve customer data."
    args_schema: Type[BaseModel] = CustomerAgentToolInput

    def _run(self, query: str, params: list = None) -> str:
        conn = None
        cursor = None
        try:
            conn = psycopg2.connect(
                host=os.environ.get('DB_HOST'),
                database=os.environ.get('DB_NAME'),
                user=os.environ.get('DB_USER'),
                password=os.environ.get('DB_PASSWORD'),
                port=int(os.environ.get('DB_PORT', 5432))
            )
            cursor = conn.cursor()
            query = """
                select *
                from customer_master
                where phone_number = %s;
            """
            cursor.execute(query, params or [])
            results = cursor.fetchall()
            print(f"customer details retrieved from DB:{results}")        
            return str(results)
        except Exception as e:
            return f"Error fetching data: {e}"
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

class VehicleAgentToolInput(BaseModel):
    query: str = Field(..., description="SQL query to execute")
    params: list = Field(default_factory=list, description="Query parameters")

class VehicleAgentTool(BaseTool):
    name: str = "VehicleAgentTool"
    description: str = "Tool to retrieve vehicle data."
    args_schema: Type[BaseModel] = VehicleAgentToolInput

    def _run(self, query: str, params: list = None) -> str:
        conn = None
        cursor = None
        try:
            conn = psycopg2.connect(
                host=os.environ.get('DB_HOST'),
                database=os.environ.get('DB_NAME'),
                user=os.environ.get('DB_USER'),
                password=os.environ.get('DB_PASSWORD'),
                port=int(os.environ.get('DB_PORT', 5432))
            )
            # Build dynamic WHERE clause and parameters
            # where_clauses = []
            # # params = []
            # if 'budget' in params:
            #     where_clauses.append('msrp <= %s')
            # if 'make' in params:
            #     where_clauses.append('make ILIKE %s')
            # if 'model' in params:
            #     where_clauses.append('model ILIKE %s')
            # if 'year' in params:
            #     where_clauses.append('model_year = %s')
            # if 'trim' in params:
            #     where_clauses.append('trim ILIKE %s')
            # if 'vehicleType' in params:
            #     where_clauses.append('vehicle_type ILIKE %s')


            # cursor = conn.cursor()
            # # Build the final query
            # base_query = "SELECT * FROM vehicle_master"
            # if where_clauses:
            #     base_query += " WHERE " + " AND ".join(where_clauses)
            # base_query += " LIMIT 5;"
            # print(base_query)
            # print(f"Query params: {params}")
            # cursor.execute(base_query, params)
            # results = cursor.fetchall()
            cursor = conn.cursor()
            
            # Directly execute the clean query string provided by the LLM
            cursor.execute(query, params or [])
            results = cursor.fetchall()
            print(f"vehicle details retrieved from DB:{results}")    
            return str(results)
        except Exception as e:
            return f"Error fetching data: {e}"
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()