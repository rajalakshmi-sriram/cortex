"""
Project Store for Cortex
File-backed persistence for research projects and their sub-resources
(tasks, papers, notes, hypotheses, methodology progress, manuscript, journals).

Each project is a directory under data/projects/<project_id>/ containing a
project.json plus one JSON file per sub-resource collection.
"""

import io
import json
import os
import threading
import uuid
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from app.logger import logger

SUB_COLLECTIONS = ['tasks', 'papers', 'notes', 'hypotheses', 'journals', 'datasets', 'analyses', 'charts']

# Bumped only if the export .zip's internal file layout changes in a way
# that would break reading an older export back in.
EXPORT_FORMAT_VERSION = 1


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

    def create_sample_project(self) -> Dict:
        """
        Create a fully-populated example project so a brand-new user has
        something to click around in immediately, instead of a blank slate.
        Every piece of content is clearly marked as a sample so it's never
        mistaken for real research.
        """
        project = self.create_project({
            'title': '[Sample] Does Caffeine Improve Reaction Time?',
            'research_area': 'Cognitive Psychology',
            'research_type': 'experimental',
            'specific_topic': 'The effect of a single 200mg caffeine dose on simple visual reaction time in healthy adults.',
            'specific_aims': 'To determine whether acute caffeine intake produces a measurable improvement in reaction time compared to placebo.',
            'research_questions': ['Does 200mg caffeine reduce mean reaction time relative to placebo?'],
        })
        project_id = project['id']

        self.collection(project_id, 'papers').add({
            'title': '[Sample paper] Caffeine and psychomotor performance: a review',
            'authors': 'Sample Author A, Sample Author B',
            'year': 2020,
            'source': 'Example Journal of Psychopharmacology',
            'annotations': 'This is placeholder sample data to help you explore the Paper Library - not a real paper. Delete it any time.',
        })

        self.collection(project_id, 'hypotheses').add({
            'text': 'H1: Participants who consume 200mg caffeine will have a faster mean reaction time than the placebo group.',
            'status': 'proposed',
        })

        self.collection(project_id, 'tasks').add({
            'title': '[Sample task] Recruit 30 participants',
            'status': 'todo',
        })
        self.collection(project_id, 'tasks').add({
            'title': '[Sample task] Run pilot session',
            'status': 'done',
        })

        self.collection(project_id, 'journals').add({
            'name': '[Sample] Journal of Cognitive Psychology (example)',
            'status': 'target',
            'notes': 'Placeholder - replace with a journal you actually plan to submit to.',
        })

        self.collection(project_id, 'datasets').add({
            'name': '[Sample] Reaction Time Data (ms)',
            'source': 'sample',
            'columns': ['participant', 'group', 'reaction_time_ms'],
            'rows': [
                [1, 'placebo', 312], [2, 'placebo', 298], [3, 'placebo', 305],
                [4, 'placebo', 320], [5, 'placebo', 291], [6, 'placebo', 315],
                [7, 'caffeine', 274], [8, 'caffeine', 281], [9, 'caffeine', 265],
                [10, 'caffeine', 290], [11, 'caffeine', 270], [12, 'caffeine', 278],
            ],
            'row_count': 12,
            'col_count': 3,
        })

        self.update_manuscript(project_id, {
            'abstract': (
                '[Sample text - replace with your own] This example explores whether a 200mg dose of '
                'caffeine improves simple visual reaction time relative to placebo in healthy adults. '
                'Edit or clear this section to start writing your own manuscript.'
            ),
        })

        # Mark the first couple of methodology steps done, so the progress bar
        # (and the idea of checking steps off) is visible immediately.
        steps = self.config.RESEARCH_TYPE_STEPS.get('experimental', [])
        for i in range(min(2, len(steps))):
            self.set_methodology_step(project_id, i, True)

        logger.info(f"Created sample project '{project['title']}' ({project_id})")
        return self.get_project(project_id)

    def export_project(self, project_id: str) -> bytes:
        """
        Package a project (metadata, methodology, manuscript, and every
        sub-collection - papers, datasets, tasks, etc.) into a .zip's raw
        bytes, for backup or handing off to a co-author.
        """
        project = self.get_project(project_id)
        if not project:
            raise ValueError(f"Unknown project: {project_id}")

        project_dir = self._project_dir(project_id)
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
            zf.writestr('manifest.json', json.dumps({
                'cortex_export_version': EXPORT_FORMAT_VERSION,
                'exported_at': now(),
                'source_project_id': project_id,
            }, indent=2))
            zf.writestr('project.json', json.dumps(project, indent=2))

            for filename in ['methodology.json', 'manuscript.json'] + [f'{name}.json' for name in SUB_COLLECTIONS]:
                path = project_dir / filename
                if path.exists():
                    zf.writestr(filename, path.read_text())

        return buffer.getvalue()

    def import_project(self, zip_bytes: bytes) -> Dict:
        """
        Recreate a project from a .zip produced by export_project(), as a
        brand-new project (fresh ID) so it never collides with anything
        already in this store - safe to import the same export multiple
        times, or into the same Cortex instance that exported it.
        """
        try:
            zf = zipfile.ZipFile(io.BytesIO(zip_bytes), 'r')
        except zipfile.BadZipFile:
            raise ValueError('Not a valid .zip file')

        with zf:
            names = set(zf.namelist())
            if 'manifest.json' not in names or 'project.json' not in names:
                raise ValueError('Not a valid Cortex project export')

            manifest = json.loads(zf.read('manifest.json'))
            if manifest.get('cortex_export_version') != EXPORT_FORMAT_VERSION:
                raise ValueError(f"Unsupported export version: {manifest.get('cortex_export_version')!r}")

            source_project = json.loads(zf.read('project.json'))
            project = self.create_project(source_project)
            project_dir = self._project_dir(project['id'])

            for filename in ['methodology.json', 'manuscript.json'] + [f'{name}.json' for name in SUB_COLLECTIONS]:
                if filename in names:
                    atomic_write_text(project_dir / filename, zf.read(filename).decode('utf-8'))

        logger.info(f"Imported project '{project['title']}' ({project['id']}) from export")
        return self.get_project(project['id'])

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
