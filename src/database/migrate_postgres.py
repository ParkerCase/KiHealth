"""
PostgreSQL Migration Script for Xata
Creates tables using PostgreSQL DDL for Postgres-enabled Xata databases
"""

import os
import json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# PostgreSQL connection string from environment
PG_URL = "postgresql://postgres:nbTPPKCTE8uiiJVrEZNQX9Mr28JyFub50qt6hzeoyZjWarwZxECb5DYb7AQwQ8Li@hni109cm916jn15jk5hkfg338s.us-east-1.xata.tech:5432/postgres?sslmode=require"


class Colors:
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"


def print_success(text):
    print(f"{Colors.OKGREEN}✅ {text}{Colors.ENDC}")


def print_error(text):
    print(f"{Colors.FAIL}❌ {text}{Colors.ENDC}")


def print_warning(text):
    print(f"{Colors.WARNING}⚠️  {text}{Colors.ENDC}")


def load_schema():
    """Load schema from JSON file"""
    schema_path = Path(__file__).parent / "xata_schema.json"
    with open(schema_path, "r") as f:
        return json.load(f)


def map_xata_type_to_pg(xata_type):
    """Map Xata types to PostgreSQL types"""
    mapping = {
        "string": "TEXT",
        "text": "TEXT",
        "int": "INTEGER",
        "float": "DOUBLE PRECISION",
        "bool": "BOOLEAN",
        "datetime": "TIMESTAMP WITH TIME ZONE",
        "json": "JSONB",
        "multiple": "TEXT[]",
    }
    return mapping.get(xata_type, "TEXT")


def create_tables():
    """Create tables using PostgreSQL"""
    try:
        import psycopg2
    except ImportError:
        print_error("psycopg2 not installed")
        print("   Install with: pip install psycopg2-binary")
        return False

    print("\n" + "=" * 70)
    print("Creating PostgreSQL Tables")
    print("=" * 70 + "\n")

    schema = load_schema()

    try:
        # Connect to PostgreSQL
        print("Connecting to PostgreSQL...")
        conn = psycopg2.connect(PG_URL)
        cursor = conn.cursor()
        print_success("Connected to PostgreSQL")

        # Create tables
        for table in schema["tables"]:
            table_name = table["name"]
            print(f"\n Creating table: {Colors.BOLD}{table_name}{Colors.ENDC}")

            # Build CREATE TABLE statement
            columns_sql = []
            for col in table["columns"]:
                col_name = col["name"]
                pg_type = map_xata_type_to_pg(col["type"])
                columns_sql.append(f'    "{col_name}" {pg_type}')

            # Add Xata metadata columns
            columns_sql.append(
                "    \"xata_id\" TEXT PRIMARY KEY DEFAULT 'rec_' || gen_random_uuid()::text"
            )
            columns_sql.append('    "xata_version" INTEGER DEFAULT 0')
            columns_sql.append(
                '    "xata_createdat" TIMESTAMP WITH TIME ZONE DEFAULT NOW()'
            )
            columns_sql.append(
                '    "xata_updatedat" TIMESTAMP WITH TIME ZONE DEFAULT NOW()'
            )

            create_sql = f"""
            CREATE TABLE IF NOT EXISTS "{table_name}" (
{",\n".join(columns_sql)}
            );
            """

            try:
                cursor.execute(create_sql)
                conn.commit()
                print_success(
                    f"Created {table_name} with {len(table['columns'])} columns"
                )
            except Exception as e:
                print_error(f"Error creating {table_name}: {e}")
                conn.rollback()

        cursor.close()
        conn.close()

        print("\n" + "=" * 70)
        print_success("All tables created successfully!")
        print("=" * 70 + "\n")

        return True

    except Exception as e:
        print_error(f"Database connection error: {e}")
        return False


if __name__ == "__main__":
    create_tables()
