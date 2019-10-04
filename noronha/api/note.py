# -*- coding: utf-8 -*-

from noronha.api.main import NoronhaAPI
from noronha.bay.expedition import ShortExpedition
from noronha.common import NoteConst
from noronha.common.annotations import projected, validate
from noronha.common.constants import DockerConst, OnBoard
from noronha.common.logging import LOG
from noronha.db.ds import Dataset
from noronha.db.movers import ModelVersion


class NotebookAPI(NoronhaAPI):
    
    valid = NoronhaAPI.valid
    
    @projected
    @validate(env_vars=dict, mounts=list, port=(int, None), tag=(str, None))
    def __call__(self, tag: str = DockerConst.LATEST, port: int = NoteConst.HOST_PORT,
                 movers: list = None, datasets: list = None, **kwargs):
        
        LOG.info("Notebook IDE will be mapped to port {}".format(port))
        return NotebookExp(
            port=port,
            proj=self.proj,
            tag=tag,
            movers=[ModelVersion.parse_ref(mv) for mv in movers or []],
            datasets=[Dataset.find_by_pk(ds) for ds in datasets or []]
        ).launch(**kwargs)


class NotebookExp(ShortExpedition):
    
    section = DockerConst.Section.IDE
    
    def __init__(self, port: int = NoteConst.HOST_PORT, **kwargs):
        
        self.port = port
        super().__init__(**kwargs)
    
    def make_cmd(self):
        
        return [
            OnBoard.ENTRYPOINT
        ] + (['--debug'] if LOG.debug_mode else [])
    
    def make_alias(self):
        
        return self.proj.name
    
    def make_ports(self):
        
        return [
            '{}:{}'.format(self.port, NoteConst.ORIGINAL_PORT)
        ]
