from pydantic import BaseModel


class AnalysisResult(BaseModel):
    summary: str
    customer_sentiment: str
    main_issue: str
    customer_needs: list[str]
    recommended_action: str