from sqlalchemy import Column, Enum, ForeignKey, Integer

from models.base_model import BaseModel
from models.feature import Feature


class ShowFeature(BaseModel):
    """One row = "this show uses this feature" (same idea as ScreenFeature)."""
    __tablename__ = "show_features"

    show_id = Column(Integer, ForeignKey("shows.id"))
    feature = Column(Enum(Feature))
