import jinja2
from deepmerge import always_merger
from typing import List
from pathlib import Path
from pydantic import ValidationError
from visivo.utils import load_yaml_file
from ..models.project import Project

PROJECT_FILE_NAME = "project.visivo.yml"
PROFILE_FILE_NAME = "profile.yml"


class CoreParser:
    def __init__(self, project_file: Path, files: List[Path]):
        self.files = files
        self.project_file = project_file

    def parse(self) -> Project:
        return self.__build_project()

    def project_file_data(self):
        return load_yaml_file(self.project_file)

    def __build_project(self):
        data = self.__merged_project_data()
        project = Project(**data)
        return project

    def __merged_project_data(self):
        project_data = self.project_file_data()

        data_files = []
        for file in self.files:
            if file == self.project_file:
                continue
            data_files.append(load_yaml_file(file))

        return self.__merge_data_into_project(
            project_data=project_data, data_files=data_files
        )

    def __merge_data_into_project(self, project_data: dict, data_files: List[dict]):
        keys_to_merge = [
            "alerts",
            "targets",
            "models",
            "traces",
            "tables",
            "charts",
            "dashboards",
        ]
        for data_file in data_files:
            for key_to_merge in keys_to_merge:
                if key_to_merge in data_file:
                    base_merge = []
                    if key_to_merge in project_data:
                        base_merge = project_data[key_to_merge]
                    project_data[key_to_merge] = always_merger.merge(
                        base_merge, data_file[key_to_merge]
                    )
        return project_data
