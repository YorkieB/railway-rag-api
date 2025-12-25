"""
Media Indexer

Indexes media files (images, audio, video) with metadata extraction.
"""

from typing import List, Optional, Dict
from datetime import datetime
from pathlib import Path

from .models import IndexedDocument, IndexMetadata, DocumentType


class MediaIndexer:
    """Indexes media files."""
    
    def __init__(self):
        """Initialize media indexer."""
        pass
    
    async def index_image(self, file_path: str) -> IndexedDocument:
        """
        Index an image file.
        
        Args:
            file_path: Path to image file
        
        Returns:
            IndexedDocument with image metadata
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Extract metadata
        metadata_dict = await self._extract_image_metadata(file_path)
        
        # Create metadata
        metadata = IndexMetadata(
            document_id=f"img_{path.stem}_{path.stat().st_mtime}",
            document_type=DocumentType.IMAGE,
            source=str(path.absolute()),
            title=path.stem,
            size=path.stat().st_size,
            indexed_at=datetime.utcnow(),
            custom_metadata=metadata_dict
        )
        
        # For images, content is metadata description
        content = f"Image: {path.name}\nMetadata: {metadata_dict}"
        
        return IndexedDocument(
            id=metadata.document_id,
            content=content,
            metadata=metadata,
            chunks=[content]
        )
    
    async def index_audio(self, file_path: str) -> IndexedDocument:
        """
        Index an audio file.
        
        Args:
            file_path: Path to audio file
        
        Returns:
            IndexedDocument with audio metadata
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Extract metadata
        metadata_dict = await self._extract_audio_metadata(file_path)
        
        # Create metadata
        metadata = IndexMetadata(
            document_id=f"audio_{path.stem}_{path.stat().st_mtime}",
            document_type=DocumentType.AUDIO,
            source=str(path.absolute()),
            title=path.stem,
            size=path.stat().st_size,
            indexed_at=datetime.utcnow(),
            custom_metadata=metadata_dict
        )
        
        content = f"Audio: {path.name}\nMetadata: {metadata_dict}"
        
        return IndexedDocument(
            id=metadata.document_id,
            content=content,
            metadata=metadata,
            chunks=[content]
        )
    
    async def index_video(self, file_path: str) -> IndexedDocument:
        """
        Index a video file.
        
        Args:
            file_path: Path to video file
        
        Returns:
            IndexedDocument with video metadata
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Extract metadata
        metadata_dict = await self._extract_video_metadata(file_path)
        
        # Create metadata
        metadata = IndexMetadata(
            document_id=f"video_{path.stem}_{path.stat().st_mtime}",
            document_type=DocumentType.VIDEO,
            source=str(path.absolute()),
            title=path.stem,
            size=path.stat().st_size,
            indexed_at=datetime.utcnow(),
            custom_metadata=metadata_dict
        )
        
        content = f"Video: {path.name}\nMetadata: {metadata_dict}"
        
        return IndexedDocument(
            id=metadata.document_id,
            content=content,
            metadata=metadata,
            chunks=[content]
        )
    
    async def _extract_image_metadata(self, file_path: str) -> Dict:
        """Extract image metadata."""
        metadata = {}
        
        try:
            from PIL import Image
            from PIL.ExifTags import TAGS
            
            with Image.open(file_path) as img:
                metadata["format"] = img.format
                metadata["mode"] = img.mode
                metadata["size"] = img.size
                
                # Extract EXIF data
                exifdata = img.getexif()
                if exifdata:
                    exif_dict = {}
                    for tag_id, value in exifdata.items():
                        tag = TAGS.get(tag_id, tag_id)
                        exif_dict[tag] = value
                    metadata["exif"] = exif_dict
        except ImportError:
            metadata["note"] = "PIL/Pillow not installed for detailed metadata"
        except Exception as e:
            metadata["error"] = str(e)
        
        return metadata
    
    async def _extract_audio_metadata(self, file_path: str) -> Dict:
        """Extract audio metadata."""
        metadata = {}
        
        try:
            import mutagen
            from mutagen.id3 import ID3NoHeaderError
            
            audio_file = mutagen.File(file_path)
            if audio_file:
                metadata["length"] = audio_file.info.length if hasattr(audio_file.info, "length") else None
                metadata["bitrate"] = audio_file.info.bitrate if hasattr(audio_file.info, "bitrate") else None
                
                # Extract tags
                if audio_file.tags:
                    for key, value in audio_file.tags.items():
                        if isinstance(value, list) and len(value) > 0:
                            metadata[key] = value[0]
                        else:
                            metadata[key] = value
        except ImportError:
            metadata["note"] = "mutagen not installed for detailed metadata"
        except Exception as e:
            metadata["error"] = str(e)
        
        return metadata
    
    async def _extract_video_metadata(self, file_path: str) -> Dict:
        """Extract video metadata."""
        metadata = {}
        
        try:
            import ffmpeg
            
            probe = ffmpeg.probe(file_path)
            video_stream = next((stream for stream in probe["streams"] if stream["codec_type"] == "video"), None)
            audio_stream = next((stream for stream in probe["streams"] if stream["codec_type"] == "audio"), None)
            
            if video_stream:
                metadata["video"] = {
                    "codec": video_stream.get("codec_name"),
                    "width": video_stream.get("width"),
                    "height": video_stream.get("height"),
                    "fps": eval(video_stream.get("r_frame_rate", "0/1"))
                }
            
            if audio_stream:
                metadata["audio"] = {
                    "codec": audio_stream.get("codec_name"),
                    "sample_rate": audio_stream.get("sample_rate"),
                    "channels": audio_stream.get("channels")
                }
            
            metadata["duration"] = float(probe["format"].get("duration", 0))
        except ImportError:
            metadata["note"] = "ffmpeg-python not installed for detailed metadata"
        except Exception as e:
            metadata["error"] = str(e)
        
        return metadata

