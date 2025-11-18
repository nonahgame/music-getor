# ... (same imports as before)

class MusicGenerationDB(Base):
    __tablename__ = "music_generations"

    # ... (existing fields)
    file_format = Column(String, nullable=True)  # 'mp3', 'wav', 'simple_mp4', 'high_mp4'
    instrument_pic = Column(String, nullable=True)  # Pic URL/path for MP4
    instrument_video = Column(String, nullable=True)  # Video URL/path for high_mp4

# ... (rest same; add to Pydantic if needed)
class MusicParams(BaseModel):
    # ... (existing)
    file_format: str
    instrument_pic: str | None
    instrument_video: str | None