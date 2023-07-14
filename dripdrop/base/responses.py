from pydantic import BaseModel, ConfigDict


def snake_to_camel(string: str):
    field_parts = string.split("_")
    new_field = ""
    for i, part in enumerate(field_parts):
        if i == 0:
            new_field += part
        else:
            new_field += part.capitalize()
    return new_field


class ResponseBaseModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=snake_to_camel, populate_by_name=True, from_attributes=True
    )
