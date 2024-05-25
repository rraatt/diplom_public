import asyncio
import logging
from typing import Optional

from fastapi import FastAPI, UploadFile, File, BackgroundTasks, Request
from starlette.responses import JSONResponse
from tortoise.contrib.fastapi import register_tortoise
from DB.excel_parse import get_df, process_data
from DB.models import Report, WorkEntry, Professor
from Services.code_checker import check_codes
from Services.helper import paginate, calculate_total_pages, filter_queryset
from Services.duplicate_checker import duplication_check_starter
from fastapi.middleware.cors import CORSMiddleware
from Services.globalparserhandler import GlobalParserHandler
from DB.PydanticModels import PydanticReportList
from tortoise.expressions import F

from Services.reestr_checker import start_fach_check
from Services.reestr_parser import parse_reestr
from Services.scopus_checker import start_scopus_check

import nltk
nltk.download('punkt')



logger = logging.getLogger("reports")

app = FastAPI()

origins = [
    # "http://localhost",
    # "http://localhost:5173",
    # "http://192.168.96.3:8080/"
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

parsing_handler = GlobalParserHandler()


@app.get("/api/button-state")
async def get_button_state():
    """Get button state, to check if Rada parse is in the progress"""
    return JSONResponse({"button_disabled": parsing_handler.button_disabled})


@app.post("/api/parse-rada")
async def refill_rada_db(background_tasks: BackgroundTasks):
    """Start Rada parser (empties previous entries), it takes a long time to parse because of Rada kpi protections
    against DDOS attacks"""
    await parsing_handler.globalparserhandler(background_tasks)
    return JSONResponse({"message": "Request made successfully"})


@app.post("/api/parse-reestr")
async def refill_reestr_db():
    """Start parsing Реєстр наукових видань України (empties previous entries)"""
    await parse_reestr()
    return JSONResponse({"message": "Request made successfully"})


@app.post('/api/start-scan')
async def start_scan(background_tasks: BackgroundTasks):
    """Starts a new scan, initiates all checks"""
    await Report.all().delete()
    # background_tasks.add_task(duplication_check_starter)
    # background_tasks.add_task(check_codes)
    background_tasks.add_task(start_scopus_check)
    # background_tasks.add_task(start_fach_check)
    return JSONResponse({"message": "Request made successfully"})


@app.get("/reports-data")
async def get_reports():
    """End point for getting params for reports filter"""
    unique_years = await WorkEntry.annotate(year=F('year')).distinct().values_list('year', flat=True)
    unique_check_types = await Report.annotate(year=F('check_type')).distinct().values_list('check_type', flat=True)
    unique_departments = await Professor.annotate(department=F('department')).values_list('department', flat=True)

    context = {
        'unique_years': unique_years,
        'unique_check_types': unique_check_types,
        'unique_departments': unique_departments
    }

    return context


@app.get("/reports")
async def get_reports(request: Request, all: Optional[bool] = False):
    """End point for getting reports, supports filtrating, returns entries in batches of 20 unless 'all' is True"""
    page_size = 20
    page = int(request.query_params.get('page', 1))
    filters = request.query_params.get('filters')

    reports = Report.all()
    filtered_reports = filter_queryset(reports, filters)

    if all:
        count = await filtered_reports.count()
        max_page = 1
        queryset = await PydanticReportList.from_queryset(filtered_reports)
    else:
        count = await filtered_reports.count()
        max_page = calculate_total_pages(count, page_size)
        paginated_queryset = paginate(filtered_reports, page, page_size)
        queryset = await PydanticReportList.from_queryset(paginated_queryset)

    context = {
        'queryset': queryset,
        'max_page': max_page,
    }

    return context


@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    """Endpoint for uploading Excel file with entries data"""
    try:
        contents = await file.read()
        df = await get_df(contents)
        await process_data(df)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=400)
    return JSONResponse({"message": "File uploaded successfully"})


@app.delete('/api/delete-report/{report_id}')
async def delete_report(report_id: int):
    """Endpoint for deleting a manually confirmed report"""
    item = await Report.get(id=report_id)
    await item.delete()
    return JSONResponse({"message": "Report deleted successfully"})


register_tortoise(
    app,
    db_url="sqlite://db.sqlite3",
    modules={"models": ["DB.models"]},
    generate_schemas=True,
    add_exception_handlers=True
)
