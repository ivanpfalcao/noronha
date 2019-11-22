# -*- coding: utf-8 -*-

import os
import papermill as pm

from noronha.bay.barrel import NotebookBarrel
from noronha.common.annotations import Patient, PatientError, patient
from noronha.common.constants import OnBoard, Task, Extension
from noronha.common.errors import NhaStorageError
from noronha.common.logging import LOG
from noronha.db.proj import Project
from noronha.tools.main import NoronhaEngine
from noronha.tools.utils import load_proc_monitor


class NotebookRunner(Patient):

    def __init__(self, debug=False):
        
        super().__init__(timeout=3)
        self.debug = debug
        self.proj = Project.load()
        self.proc_mon = load_proc_monitor()
        
        if self.debug:
            LOG.debug_mode = True
    
    @property
    def output_file_name(self):
        
        return self.proc_mon.proc_name
    
    def _print_exc(self, e: Exception):
        
        LOG.error("Notebook execution failed:")
        LOG.error(e)
        self.proc_mon.set_state(Task.State.FAILED)
    
    def _handle_exc(self, e: Exception):
        
        if str(e) == "Kernel didn't respond in -1 seconds":
            raise PatientError(original_exception=e, raise_callback=self._print_exc)
        else:
            self._print_exc(e)
    
    @patient
    def _run(self, **kwargs):
        
        try:
            LOG.debug("Notebook parameters:")
            LOG.debug(kwargs.get('parameters', {}))
            self.proc_mon.set_state(Task.State.RUNNING)
            pm.execute_notebook(**kwargs)
        except Exception as e:
            self._handle_exc(e)
        else:
            LOG.info("Notebook execution succeeded!")
            self.proc_mon.set_state(Task.State.FINISHED)
    
    def _save_output(self, note_path, output_path):
        
        try:
            # TODO: convert to pdf (find a light-weight lib for that)
            NotebookBarrel(
                proj=self.proj,
                notebook=note_path,
                file_name=output_path
            ).store_from_path(os.getcwd())
        except Exception as e:
            err = NhaStorageError("Failed to save output notebook '{}'".format(output_path))
            e.__cause__ = e
            LOG.error(err)
    
    def __call__(self, note_path: str, params: dict):
        
        NoronhaEngine.progress_callback = lambda x: self.proc_mon.set_progress(x)
        output_path = '.'.join([self.output_file_name, Extension.IPYNB])
        
        self._run(**dict(
            parameters=params,
            engine_name=NoronhaEngine.alias,
            input_path=os.path.join(OnBoard.APP_HOME, note_path),
            output_path=output_path
        ))
        
        code = 0 if self.proc_mon.task.state == Task.State.FINISHED else 1
        
        if code == 1 or self.debug:
            self._save_output(note_path, output_path)
        
        return code
