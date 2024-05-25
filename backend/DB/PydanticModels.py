from tortoise.contrib.pydantic import pydantic_model_creator, pydantic_queryset_creator

from DB.models import Report
from tortoise import Tortoise

Tortoise.init_models(["DB.models"], "models")

PydanticReport = pydantic_model_creator(Report)

PydanticReportList = pydantic_queryset_creator(Report)

