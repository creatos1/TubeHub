from app import db
from datetime import datetime

class Config(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key_name = db.Column(db.String(50), unique=True, nullable=False)
    key_value = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Config {self.key_name}>'

class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    youtube_id = db.Column(db.String(20), unique=True, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    thumbnail_url = db.Column(db.String(500))
    duration = db.Column(db.String(20))
    view_count = db.Column(db.Integer)
    like_count = db.Column(db.Integer)
    published_at = db.Column(db.DateTime)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Video {self.title}>'
    
    @property
    def youtube_url(self):
        return f"https://www.youtube.com/watch?v={self.youtube_id}"
    
    @property
    def formatted_message(self):
        """Generate a preformatted message for sharing"""
        return f"🎥 Check out this video: {self.title}\n{self.youtube_url}\n\n{self.description[:200]}{'...' if len(self.description) > 200 else ''}"
