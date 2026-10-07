#!/usr/bin/env python3
"""
SQLite Persistence Layer for PLB Story Forge
============================================
Persists sessions, story DNA, root stories, expanded generations,
and lineage relationships in a lightweight, robust local database.
"""

import sqlite3
import json
import time
from pathlib import Path
from typing import Dict, Any, List, Optional

DB_PATH = Path(__file__).resolve().parent / "story_forge.db"

def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes SQLite schema for sessions and recursive stories."""
    with get_connection() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS sessions (
            session_id TEXT PRIMARY KEY,
            source_video_name TEXT,
            source_video_path TEXT,
            source_video_hash TEXT,
            file_size_bytes INTEGER,
            duration_seconds REAL,
            created_at TEXT,
            provider_info TEXT,
            settings_json TEXT,
            story_dna_json TEXT
        );

        CREATE TABLE IF NOT EXISTS stories (
            session_id TEXT,
            story_id TEXT,
            parent_id TEXT,
            generation INTEGER,
            title TEXT,
            one_line_premise TEXT,
            mode TEXT,
            diversity_score REAL,
            data_json TEXT,
            evolution_json TEXT,
            created_at TEXT,
            PRIMARY KEY (session_id, story_id),
            FOREIGN KEY (session_id) REFERENCES sessions(session_id) ON DELETE CASCADE
        );

        CREATE INDEX IF NOT EXISTS idx_stories_parent ON stories(session_id, parent_id);
        CREATE INDEX IF NOT EXISTS idx_stories_gen ON stories(session_id, generation);
        """)

def save_session(
    session_id: str,
    meta: Dict[str, Any],
    story_dna: Dict[str, Any],
    settings: Dict[str, Any],
    provider_info: str = "local-deterministic"
):
    """Saves or updates a project session record."""
    init_db()
    with get_connection() as conn:
        conn.execute("""
        INSERT OR REPLACE INTO sessions (
            session_id, source_video_name, source_video_path, source_video_hash,
            file_size_bytes, duration_seconds, created_at, provider_info,
            settings_json, story_dna_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            session_id,
            meta.get("source_video_name", "Unknown Video"),
            meta.get("source_video_path", ""),
            meta.get("source_video_hash", ""),
            meta.get("file_size_bytes", 0),
            meta.get("technical_metadata", {}).get("duration_seconds", 0.0),
            time.strftime("%Y-%m-%d %H:%M:%S"),
            provider_info,
            json.dumps(settings),
            json.dumps(story_dna)
        ))

def save_stories_batch(session_id: str, stories: List[Dict[str, Any]]):
    """Saves a batch of story nodes (e.g. 50 root stories or 50 expansion children)."""
    init_db()
    now_str = time.strftime("%Y-%m-%d %H:%M:%S")
    with get_connection() as conn:
        for s in stories:
            conn.execute("""
            INSERT OR REPLACE INTO stories (
                session_id, story_id, parent_id, generation, title,
                one_line_premise, mode, diversity_score, data_json,
                evolution_json, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                session_id,
                s.get("story_id"),
                s.get("parent_id", "ROOT"),
                s.get("generation", 1),
                s.get("title", ""),
                s.get("one_line_premise", ""),
                s.get("mode", "AUTO"),
                s.get("diversity_score", 0.70),
                json.dumps(s),
                json.dumps(s.get("evolution_metadata", {})),
                now_str
            ))

def get_session(session_id: str) -> Optional[Dict[str, Any]]:
    """Retrieves session metadata and Story DNA."""
    init_db()
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM sessions WHERE session_id = ?", (session_id,)).fetchone()
        if not row:
            return None
        res = dict(row)
        res["settings"] = json.loads(res.pop("settings_json") or "{}")
        res["story_dna"] = json.loads(res.pop("story_dna_json") or "{}")
        return res

def list_recent_sessions(limit: int = 15) -> List[Dict[str, Any]]:
    """Lists recent story analysis sessions."""
    init_db()
    with get_connection() as conn:
        cursor = conn.execute(
            "SELECT session_id, source_video_name, source_video_path, source_video_hash, file_size_bytes, duration_seconds, created_at FROM sessions ORDER BY created_at DESC LIMIT ?",
            (limit,)
        )
        return [dict(r) for r in cursor.fetchall()]

def get_story(session_id: str, story_id: str) -> Optional[Dict[str, Any]]:
    """Retrieves a single story with all attributes."""
    init_db()
    with get_connection() as conn:
        row = conn.execute(
            "SELECT data_json, evolution_json FROM stories WHERE session_id = ? AND story_id = ?",
            (session_id, story_id)
        ).fetchone()
        if not row:
            return None
        data = json.loads(row["data_json"])
        if row["evolution_json"]:
            data["evolution_metadata"] = json.loads(row["evolution_json"])
        return data

def get_children(session_id: str, parent_id: str) -> List[Dict[str, Any]]:
    """Retrieves all direct child stories of a parent node."""
    init_db()
    with get_connection() as conn:
        cursor = conn.execute(
            "SELECT data_json, evolution_json FROM stories WHERE session_id = ? AND parent_id = ? ORDER BY story_id ASC",
            (session_id, parent_id)
        )
        children = []
        for row in cursor.fetchall():
            d = json.loads(row["data_json"])
            if row["evolution_json"]:
                d["evolution_metadata"] = json.loads(row["evolution_json"])
            children.append(d)
        return children

def get_all_stories_for_session(session_id: str) -> List[Dict[str, Any]]:
    """Retrieves all stories across all generations for a session."""
    init_db()
    with get_connection() as conn:
        cursor = conn.execute(
            "SELECT data_json, evolution_json FROM stories WHERE session_id = ? ORDER BY generation ASC, story_id ASC",
            (session_id,)
        )
        stories = []
        for row in cursor.fetchall():
            d = json.loads(row["data_json"])
            if row["evolution_json"]:
                d["evolution_metadata"] = json.loads(row["evolution_json"])
            stories.append(d)
        return stories

def get_lineage_graph(session_id: str) -> Dict[str, Any]:
    """
    Builds a hierarchical tree graph representation of all generated stories.
    ROOT -> Gen 1 (50 nodes) -> Gen 2 (expanded children) -> ...
    """
    all_stories = get_all_stories_for_session(session_id)
    session = get_session(session_id)
    dna = session["story_dna"] if session else {}

    nodes_by_id: Dict[str, Dict[str, Any]] = {}
    
    # Root Node
    root_node = {
        "id": "ROOT",
        "title": dna.get("core_premise", "Source Video Story DNA"),
        "generation": 0,
        "parent_id": None,
        "diversity_score": 1.0,
        "children_count": 0,
        "children": []
    }
    nodes_by_id["ROOT"] = root_node

    for s in all_stories:
        sid = s["story_id"]
        node = {
            "id": sid,
            "title": s.get("title", ""),
            "generation": s.get("generation", 1),
            "parent_id": s.get("parent_id", "ROOT"),
            "diversity_score": s.get("diversity_score", 0.70),
            "mode": s.get("mode", "AUTO"),
            "premise": s.get("one_line_premise", ""),
            "children_count": 0,
            "children": []
        }
        nodes_by_id[sid] = node

    # Stitch Parent-Child Trees
    for sid, node in nodes_by_id.items():
        if sid == "ROOT":
            continue
        pid = node["parent_id"]
        if pid in nodes_by_id:
            nodes_by_id[pid]["children"].append(node)
            nodes_by_id[pid]["children_count"] += 1

    return root_node
