"""
Project Store for Cortex
File-backed persistence for research projects and their sub-resources
(tasks, papers, notes, hypotheses, methodology progress, manuscript, journals).

Each project is a directory under data/projects/<project_id>/ containing a
project.json plus one JSON file per sub-resource collection.
"""

import json
import os
import threading
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from app.logger import logger

SUB_COLLECTIONS = ['tasks', 'papers', 'notes', 'hypotheses', 'journals', 'datasets', 'analyses', 'charts']


def new_id() -> str:
    return uuid.uuid4().hex[:12]


def now() -> str:
    return datetime.now().isoformat()


def atomic_write_text(path: Path, text: str) -> None:
    """
    Write a file so a mid-write kill (force-quit, crash, power loss) can
    never leave a half-written/corrupt JSON file behind: write to a sibling
    temp file first, then atomically rename it over the real path.
    os.replace() is atomic on both POSIX and Windows - the original file is
    either fully replaced or untouched, never partially written.
    """
    tmp_path = path.with_suffix(path.suffix + f'.tmp-{os.getpid()}')
    tmp_path.write_text(text)
    os.replace(tmp_path, path)


# Flask's dev server runs threaded, and a new JSONCollection instance is
# created per request (see ProjectStore.collection()), so a per-instance lock
# wouldn't prevent concurrent read-modify-write races on the same file (e.g.
# saving many papers from a literature search at once). Use one process-wide
# lock per file path instead.
_file_locks: Dict[str, threading.Lock] = {}
_locks_guard = threading.Lock()


def _lock_for(path: Path) -> threading.Lock:
    key = str(path)
    with _locks_guard:
        if key not in _file_locks:
            _file_locks[key] = threading.Lock()
        return _file_locks[key]


class JSONCollection:
    """A simple list-of-dicts collection persisted as a JSON file, keyed by 'id'"""

    def __init__(self, path: Path):
        self.path = path
        self._lock = _lock_for(path)
        if not self.path.exists():
            atomic_write_text(self.path, '[]')

    def _load(self) -> List[Dict]:
        try:
            return json.loads(self.path.read_text() or '[]')
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def _save(self, items: List[Dict]):
        atomic_write_text(self.path, json.dumps(items, indent=2))

    def list(self) -> List[Dict]:
        with self._lock:
            return self._load()

    def get(self, item_id: str) -> Optional[Dict]:
        with self._lock:
            return next((item for item in self._load() if item.get('id') == item_id), None)

    def add(self, data: Dict) -> Dict:
        with self._lock:
            items = self._load()
            item = {'id': new_id(), 'created_at': now(), 'updated_at': now(), **data}
            items.append(item)
            self._save(items)
            return item

    def update(self, item_id: str, data: Dict) -> Optional[Dict]:
        with self._lock:
            items = self._load()
            for i, item in enumerate(items):
                if item.get('id') == item_id:
                    items[i] = {**item, **data, 'updated_at': now()}
                    self._save(items)
                    return items[i]
            return None

    def delete(self, item_id: str) -> bool:
        with self._lock:
            items = self._load()
            remaining = [item for item in items if item.get('id') != item_id]
            if len(remaining) == len(items):
                return False
            self._save(remaining)
            return True


class ProjectStore:
    """Manages research project workspaces and their sub-resources"""

    def __init__(self, config):
        self.config = config
        self.projects_dir = config.PROJECTS_DIR
        self.projects_dir.mkdir(exist_ok=True, parents=True)
        self._index_path = self.projects_dir / 'index.json'
        if not self._index_path.exists():
            atomic_write_text(self._index_path, '[]')
        logger.info(f"ProjectStore initialized at {self.projects_dir}")

    def _project_dir(self, project_id: str) -> Path:
        return self.projects_dir / project_id

    def _index(self) -> JSONCollection:
        return JSONCollection(self._index_path)

    def list_projects(self) -> List[Dict]:
        return sorted(self._index().list(), key=lambda p: p.get('updated_at', ''), reverse=True)

    def create_project(self, data: Dict) -> Dict:
        research_type = data.get('research_type')
        if research_type not in self.config.RESEARCH_TYPES:
            raise ValueError(f"Invalid research_type: {research_type}")

        project = self._index().add({
            'title': data.get('title', 'Untitled Project'),
            'research_area': data.get('research_area', ''),
            'research_type': research_type,
            'keywords': data.get('keywords', []),
            'institution': data.get('institution', ''),
            'collaborators': data.get('collaborators', []),
            'funding': data.get('funding', ''),
            'target_journals': data.get('target_journals', []),
            'citation_style': data.get('citation_style', 'APA'),
            'language': data.get('language', 'English'),
            'timeline': data.get('timeline', ''),
            'privacy': data.get('privacy', 'private'),
            'status': data.get('status', 'active'),
            # Populated via the Project Search workflow: narrowing a broad topic
            # down to a specific research focus, aims, and questions.
            'specific_topic': data.get('specific_topic', ''),
            'specific_aims': data.get('specific_aims', ''),
            'research_questions': data.get('research_questions', []),
        })

        project_dir = self._project_dir(project['id'])
        project_dir.mkdir(exist_ok=True)
        for name in SUB_COLLECTIONS:
            JSONCollection(project_dir / f'{name}.json')

        steps = self.config.RESEARCH_TYPE_STEPS.get(research_type, [])
        methodology_path = project_dir / 'methodology.json'
        atomic_write_text(methodology_path, json.dumps({
            'completed_steps': []
        }, indent=2))

        manuscript_path = project_dir / 'manuscript.json'
        atomic_write_text(manuscript_path, json.dumps(
            {section: '' for section in self.config.MANUSCRIPT_SECTIONS}, indent=2
        ))

        logger.info(f"Created project '{project['title']}' ({project['id']}) [{research_type}]")
        return project

    def get_project(self, project_id: str) -> Optional[Dict]:
        return self._index().get(project_id)

    def update_project(self, project_id: str, data: Dict) -> Optional[Dict]:
        return self._index().update(project_id, data)

    def delete_project(self, project_id: str) -> bool:
        import shutil
        deleted = self._index().delete(project_id)
        project_dir = self._project_dir(project_id)
        if project_dir.exists():
            shutil.rmtree(project_dir)
        return deleted

    def collection(self, project_id: str, name: str) -> JSONCollection:
        if name not in SUB_COLLECTIONS:
            raise ValueError(f"Unknown collection: {name}")
        return JSONCollection(self._project_dir(project_id) / f'{name}.json')

    def get_methodology(self, project_id: str) -> Dict:
        project = self.get_project(project_id)
        if not project:
            raise ValueError(f"Unknown project: {project_id}")

        from app.tool_recommendations import get_recommended_tools, get_methodology_guidelines

        steps = self.config.RESEARCH_TYPE_STEPS.get(project['research_type'], [])
        path = self._project_dir(project_id) / 'methodology.json'
        state = json.loads(path.read_text()) if path.exists() else {'completed_steps': []}
        completed = set(state.get('completed_steps', []))
        step_tools = state.get('step_tools', {})

        return {
            'research_type': project['research_type'],
            'research_type_name': self.config.RESEARCH_TYPES[project['research_type']]['name'],
            'methodology_guidelines': get_methodology_guidelines(project['research_type']),
            'steps': [
                {
                    'index': i,
                    'text': step,
                    'completed': i in completed,
                    'recommended_tools': get_recommended_tools(step),
                    'custom_tools': step_tools.get(str(i), []),
                }
                for i, step in enumerate(steps)
            ],
            'total_steps': len(steps),
            'completed_count': len(completed),
        }

    def set_methodology_step(self, project_id: str, step_index: int, completed: bool) -> Dict:
        path = self._project_dir(project_id) / 'methodology.json'
        with _lock_for(path):
            state = json.loads(path.read_text()) if path.exists() else {'completed_steps': []}
            completed_steps = set(state.get('completed_steps', []))

            if completed:
                completed_steps.add(step_index)
            else:
                completed_steps.discard(step_index)

            state['completed_steps'] = sorted(completed_steps)
            atomic_write_text(path, json.dumps(state, indent=2))
        return self.get_methodology(project_id)

    def add_step_tool(self, project_id: str, step_index: int, name: str, url: str) -> Dict:
        path = self._project_dir(project_id) / 'methodology.json'
        with _lock_for(path):
            state = json.loads(path.read_text()) if path.exists() else {'completed_steps': []}
            step_tools = state.setdefault('step_tools', {})
            key = str(step_index)
            tools = step_tools.setdefault(key, [])
            tools.append({'id': new_id(), 'name': name, 'url': url})
            atomic_write_text(path, json.dumps(state, indent=2))
        return self.get_methodology(project_id)

    def remove_step_tool(self, project_id: str, step_index: int, tool_id: str) -> Dict:
        path = self._project_dir(project_id) / 'methodology.json'
        with _lock_for(path):
            state = json.loads(path.read_text()) if path.exists() else {'completed_steps': []}
            step_tools = state.setdefault('step_tools', {})
            key = str(step_index)
            step_tools[key] = [t for t in step_tools.get(key, []) if t.get('id') != tool_id]
            atomic_write_text(path, json.dumps(state, indent=2))
        return self.get_methodology(project_id)

    def get_manuscript(self, project_id: str) -> Dict:
        path = self._project_dir(project_id) / 'manuscript.json'
        if not path.exists():
            return {section: '' for section in self.config.MANUSCRIPT_SECTIONS}
        return json.loads(path.read_text())

    def update_manuscript(self, project_id: str, sections: Dict) -> Dict:
        path = self._project_dir(project_id) / 'manuscript.json'
        current = self.get_manuscript(project_id)
        current.update({k: v for k, v in sections.items() if k in self.config.MANUSCRIPT_SECTIONS})
        atomic_write_text(path, json.dumps(current, indent=2))
        return current
