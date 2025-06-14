from marshmallow import fields, Schema

class UserSchema(Schema):
    userjwt_id = fields.Integer()
    userjwt_username = fields.String()
    

class ProjectSchema(Schema):
    project_id=fields.Integer()
    project_name = fields.String()
    project_category = fields.String()
    project_description=fields.String()
    project_created = fields.String()
    project_updated = fields.String()
    user_id = fields.Integer()