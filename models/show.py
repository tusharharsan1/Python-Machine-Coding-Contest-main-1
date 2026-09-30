from sqlalchemy import Column, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship

from models.base_model import BaseModel


class Show(BaseModel):
    __tablename__ = "shows"

    start_time = Column(DateTime)
    end_time = Column(DateTime)

    movie_id = Column(Integer, ForeignKey("movies.id"))
    movie = relationship("Movie")

    screen_id = Column(Integer, ForeignKey("screens.id"))
    screen = relationship("Screen")

    # The features of this show, as a list of ShowFeature objects.
    # To create them:  show.features = [ShowFeature(feature=f) for f in some_feature_list]
    features = relationship("ShowFeature")
