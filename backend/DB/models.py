from tortoise.contrib.pydantic import pydantic_model_creator, pydantic_queryset_creator
from tortoise.fields import CASCADE
from tortoise.models import Model
from tortoise import fields


class Professor(Model):
    """Model for storing info about a professor"""
    id = fields.IntField(pk=True)
    name = fields.TextField()
    surname = fields.TextField()
    patronymic = fields.TextField()
    department = fields.TextField()

    def __str__(self):
        return ' '.join([self.surname, self.name, self.patronymic, self.department])

    def get_full_name(self):
        return self.surname + ' ' + self.name + ' ' + self.patronymic


class WorkKind(Model):
    name = fields.CharField(null=True, max_length=255)


class WorkKind2(Model):
    name = fields.CharField(null=True, max_length=255)


class WorkKind3(Model):
    name = fields.CharField(null=True, max_length=255)


class WorkEntry(Model):
    """Model for storing work entries in db"""
    id = fields.IntField(pk=True)
    submitter: fields.ForeignKeyRelation[Professor] = fields.ForeignKeyField(
        "models.Professor", related_name="Роботи", on_delete=CASCADE
    )
    workkind = fields.ForeignKeyField('models.WorkKind')
    workkind2 = fields.ForeignKeyField('models.WorkKind2')
    workkind3 = fields.ForeignKeyField('models.WorkKind3')
    description = fields.TextField()
    year = fields.CharField(max_length=100)

    def __str__(self):
        return str(self.submitter) + ' ' + self.description


class Rada(Model):
    """Model for storing info about Academic Councils"""
    code = fields.CharField(max_length=50)
    content = fields.TextField()

    def __str__(self):
        return self.content


class Report(Model):
    """Model for storing report entries regarding the check"""
    entry = fields.ForeignKeyField('models.WorkEntry', related_name='report')
    check_type = fields.CharField(max_length=255)
    result = fields.CharField(max_length=255)
    duplicate = fields.ForeignKeyField('models.WorkEntry', null=True, related_name='duplicate')


class ReestrEntry(Model):
    """Model for storing info from Українська наукова періодика"""
    name = fields.CharField(max_length=255)
    codes = fields.CharField(max_length=255)