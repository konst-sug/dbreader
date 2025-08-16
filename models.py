from pydantic import BaseModel
from typing import List, Dict

class ProcessData(BaseModel):
    val1: str
    val2: str
    val3: str

class PaginationInfo(BaseModel):
    current_page: int
    total_pages: int
    data: List[Dict]

class User(BaseModel):
    dbName: str
    dbUser: str
    dbPassword: str
    dbPort: str
    dbHost: str
    docPath: str

class SearchQuery(BaseModel):
    SearchNameString: str | None = None
    DateRangeStartString: str | None = None
    DateRangeEndString: str | None = None
    SelectedType: list[str] | None = []
    SelectedReg: list[str] | None = []
    SelectedRegPeriod: list[str] | None = []