from collections.abc import Generator

from sqlmodel import Session, SQLModel, create_engine

DATABASE_URL = "sqlite:///./reflection_records.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)


def create_db_and_tables() -> None:
    """Create database tables from SQLModel metadata on application startup."""
    from app import models  # noqa: F401

    SQLModel.metadata.create_all(engine)
    _apply_sqlite_compatibility_migrations()


def _apply_sqlite_compatibility_migrations() -> None:
    """Add Stage 8 columns to the existing local SQLite tool-log table."""
    if engine.dialect.name != "sqlite":
        return

    with engine.begin() as connection:
        columns = {
            row[1]
            for row in connection.exec_driver_sql("PRAGMA table_info(agent_tool_calls)").fetchall()
        }
        if "conversation_id" not in columns:
            connection.exec_driver_sql("ALTER TABLE agent_tool_calls ADD COLUMN conversation_id VARCHAR")
        if "assistant_message_id" not in columns:
            connection.exec_driver_sql("ALTER TABLE agent_tool_calls ADD COLUMN assistant_message_id INTEGER")


def get_session() -> Generator[Session, None, None]:
    """Provide one database session per request."""
    with Session(engine) as session:
        yield session
