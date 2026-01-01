"""
FastAPI application for GitHub Repository Access Plugin.
Provides endpoints to browse repository structure and read file contents.
"""
import os
from datetime import datetime
from typing import Optional, List, Dict, Any
import json
from pathlib import Path
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from github_client import GitHubClient
PLUGIN_DIR = Path(__file__).parent

# Initialize FastAPI app
app = FastAPI(
    title="GitHub Repository Access Plugin",
    description="Provides access to GitHub repository contents including file structure and file content reading.",
    version="1.0.0"
)

# Add CORS middleware to allow requests from LobeChat
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize GitHub client
github_client = GitHubClient(token=os.getenv("GITHUB_TOKEN"))

# Pydantic models for request/response validation
class RepositoryItem(BaseModel):
    """Represents a file or directory in a repository."""
    name: str
    path: str
    type: str  # "file" or "dir"
    size: Optional[int] = None

class RepositoryStructure(BaseModel):
    """Response model for repository structure endpoint."""
    path: str
    items: List[RepositoryItem]

class FileContent(BaseModel):
    """Response model for file content endpoint."""
    path: str
    content: str
    size: int
    encoding: str

class ErrorResponse(BaseModel):
    """Error response model."""
    error: str
    message: str

@app.get("/health")
async def health_check():
    """Health check endpoint for Docker health monitoring."""
    return {
        "status": "healthy",
        "service": "github-repo-access-plugin",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/repos/{owner}/{repo}/structure", response_model=RepositoryStructure)
async def get_repo_structure(
    owner: str,
    repo: str,
    path: Optional[str] = Query("", description="Path within repository (defaults to root)"),
    branch: Optional[str] = Query("", description="Branch name (defaults to default branch)")
) -> RepositoryStructure:
    """Get repository file and folder structure."""
    try:
        # Get repository structure from GitHub client
        structure_data = await github_client.get_repository_structure(
            owner=owner,
            repo=repo,
            path=path if path else "/",
            branch=branch if branch else None
        )
        
        return RepositoryStructure(**structure_data)
        
    except Exception as e:
        error_msg = str(e)
        if "404" in error_msg or "Not Found" in error_msg:
            raise HTTPException(
                status_code=404,
                detail={"error": "RepositoryNotFound", "message": f"Repository {owner}/{repo} not found"}
            )
        else:
            raise HTTPException(
                status_code=500,
                detail={"error": "GitHubAPIError", "message": f"Error accessing GitHub API: {error_msg}"}
            )

@app.get("/api/repos/{owner}/{repo}/files/{file_path}", response_model=FileContent)
async def read_file(
    owner: str,
    repo: str,
    file_path: str,
    branch: Optional[str] = Query("", description="Branch name (defaults to default branch)")
) -> FileContent:
    """Read a file from a GitHub repository."""
    try:
        # Get file content from GitHub client
        file_data = await github_client.get_file_content(
            owner=owner,
            repo=repo,
            file_path=file_path,
            branch=branch if branch else None
        )
        
        return FileContent(**file_data)
        
    except Exception as e:
        error_msg = str(e)
        if "404" in error_msg or "Not Found" in error_msg:
            raise HTTPException(
                status_code=404,
                detail={"error": "FileNotFound", "message": f"File {file_path} not found in {owner}/{repo}"}
            )
        else:
            raise HTTPException(
                status_code=500,
                detail={"error": "GitHubAPIError", "message": f"Error accessing GitHub API: {error_msg}"}
            )

@app.get("/manifest.json", include_in_schema=False)
async def get_manifest():
    """Return plugin manifest for LobeChat."""
    try:
        manifest_path = PLUGIN_DIR / "manifest.json"
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest_data = json.load(f)
        return JSONResponse(manifest_data)
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail={"error": "ManifestNotFound", "message": "manifest.json file not found"}
        )
    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=500,
            detail={"error": "InvalidManifest", "message": f"Invalid JSON in manifest: {str(e)}"}
        )