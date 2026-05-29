from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import boto3
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

class RateAgentToolInput(BaseModel):
    query: str = Field(..., description="DynamoDB query or key lookup expression")
    params: list = Field(default_factory=list, description="Optional query parameters")

class RateAgentTool(BaseTool):
    name: str = "RateAgentTool"
    description: str = "Tool to retrieve rate data from DynamoDB."
    args_schema: Type[BaseModel] = RateAgentToolInput

    def _run(self, query: str, params: list = None) -> str:
        dynamodb = boto3.resource(
            "dynamodb",
            region_name="us-east-1",
            aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
        )
        table = dynamodb.Table("rateMaster")
        try:
            if query and "=" in query and not params:
                key_name, key_value = [part.strip() for part in query.split("=", 1)]
                key_value = key_value.strip("'\"")
                response = table.get_item(Key={key_name: key_value})
                items = [response.get("Item")] if response.get("Item") else []
            else:
                response = table.scan()
                items = response.get("Items", [])
            print(f"rate data retrieved from DynamoDB: {items}")
            return str(items)
        except Exception as e:
            return f"Error fetching data from DynamoDB: {e}"

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