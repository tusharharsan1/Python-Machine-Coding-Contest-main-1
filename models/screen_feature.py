from sqlalchemy import Column, Enum, ForeignKey, Integer

from models.base_model import BaseModel
from models.feature import Feature


class ScreenFeature(BaseModel):
    """One row = "this screen supports this feature".

    A database column cannot hold a list, so a list of features is stored as one row per feature.
    """
    __tablename__ = "screen_features"

    screen_id = Column(Integer, ForeignKey("screens.id"))
    feature = Column(Enum(Feature))
