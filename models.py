from pymodm import fields
from pymodm import MongoModel


class Benchmark(MongoModel):
    name = fields.CharField()


class User(MongoModel):
    code = fields.CharField(primary_key=True)
    title = fields.CharField()
    description = fields.CharField()
    maintainer = fields.CharField()
    sections = fields.ListField(fields.DictField())
    assessments = fields.ListField(fields.DictField())
    inClass = fields.IntegerField()
    inLab = fields.IntegerField()
    percentFailure = fields.IntegerField()
    averageGrade = fields.CharField()
    auDistribution = fields.DictField()
    caebAttributes = fields.DictField()
    learningOutcomes = fields.ListField(fields.CharField())
    prerequisites = fields.CharField()
    corequisites = fields.CharField()
    recommended = fields.CharField()
    benchmarks = fields.ListField(fields.ReferenceField(Benchmark))
