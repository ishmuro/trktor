from pydantic import BaseModel

class DiscordConfigModel(BaseModel):
    api_key: str

class ConfigDataModel(BaseModel):
    discord: DiscordConfigModel
