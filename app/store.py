import uuid
import pandas as pd
from typing import Any, Dict

_store: Dict[str, Dict[str, Any]] = {}

def create_upload_id(df: pd.DataFrame) -> str:
    upload_id = str(uuid.uuid4())
    _store[upload_id] = {
        "df": df,
        "columns": df.columns.tolist(),
        "system_prompt": None,
        "smart_df": None
    }
    return upload_id

def get_entry(upload_id: str) -> Dict[str, Any]:
    return _store.get(upload_id)
