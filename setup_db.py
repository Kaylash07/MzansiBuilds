"""Helper script to create the database and tables."""
import psycopg


def create_database():
    """Create the mzansibuilds database if it doesn't exist."""
    try:
        conn = psycopg.connect(
            host="localhost",
            port=5432,
            user="postgres",
            password="Jasmica@20",
            dbname="postgres",
            autocommit=True,
        )
        cur = conn.cursor()

        cur.execute("SELECT 1 FROM pg_database WHERE datname = 'mzansibuilds'")
        if not cur.fetchone():
            cur.execute("CREATE DATABASE mzansibuilds")
            print("Database 'mzansibuilds' created successfully.")
        else:
            print("Database 'mzansibuilds' already exists.")

        cur.close()
        conn.close()
    except psycopg.OperationalError as e:
        print(f"Could not connect to PostgreSQL: {e}")
        print("\nPlease ensure:")
        print("  1. PostgreSQL is installed and running")
        print("  2. The 'postgres' user exists with password 'postgres'")
        print("  3. Or update DATABASE_URL in your .env file")
        raise SystemExit(1)


def create_tables():
    """Create all tables using Flask-SQLAlchemy."""
    from app import app, db
    with app.app_context():
        db.create_all()
        print("All database tables created.")


if __name__ == "__main__":
    create_database()
    create_tables()
    print("\nSetup complete! Run 'flask run' to start the application.")
    print("Optionally run 'flask seed-db' to add sample data.")
