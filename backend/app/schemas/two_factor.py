from pydantic import BaseModel


class TwoFactorSetupResponse(BaseModel):
    qr_code_url: str
    secret: str


class TwoFactorVerifyRequest(BaseModel):
    code: str
