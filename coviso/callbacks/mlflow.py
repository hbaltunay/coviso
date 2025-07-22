import subprocess
from pathlib import Path
from typing import Any

import mlflow
from mlflow.entities import Experiment

from ..loggers import CLogger
from ..utils.file import check_unique_name
from .base import Callback

logger = CLogger(__name__)

LOCAL_FILE_URI_PREFIX = "file:"


def sanitize_dict(x: dict[str, Any]) -> dict[str, Any]:
    return {k.replace("(", "").replace(")", ""): float(v) for k, v in x.items()}


class Mlflow(Callback):
    """
    mlflow server --backend-store-uri file:///...
    """

    def __init__(
        self,
        epochs: int,
        run_name: str,
        experiment_name: str,
        experiment_path: str | Path = "./",
        resume: bool = False,
    ) -> None:

        self.epochs = epochs
        self.run_name = run_name
        self.experiment_name = experiment_name
        self.experiment_path = Path(experiment_path)
        self.resume = resume

        self.experiment_path = (Path(self.experiment_path) / "mlruns").resolve()
        if not self.experiment_path.is_dir():
            self.experiment_path.mkdir(parents=True)
            (self.experiment_path / ".trash").mkdir(parents=True)  # for experiments

        self.uri = LOCAL_FILE_URI_PREFIX + str(self.experiment_path)
        self.setup()

    def setup(self) -> None:

        mlflow.set_tracking_uri(self.uri)

        experiment = mlflow.get_experiment_by_name(name=self.experiment_name)
        if experiment is None:
            self.experiment_id = mlflow.create_experiment(
                name=self.experiment_name,
            )
        else:
            self.experiment_id = experiment.experiment_id

        mlflow.set_experiment(experiment_id=self.experiment_id)

        # mlflow.autolog()

    def check_runs(self) -> str | None:
        for exp_run in mlflow.search_runs(output_format="list"):
            if exp_run.info.run_name == self.run_name:
                self.last_epoch = exp_run.data.metrics.get("Epoch", 0)
                if self.last_epoch == self.epochs:
                    logger.info(f"Run(name: {self.run_name}) is completed!")
                return exp_run.info.run_id

    def get_run_name(self) -> str:
        run_names = []
        for exp_run in mlflow.search_runs(output_format="list"):
            run_names.append(exp_run.info.run_name)

        run_name = (
            self.run_name
            if run_names is []
            else check_unique_name(self.run_name, run_names)
        )

        return run_name

    def start(self) -> None:
        if self.resume:
            exp_run_id = self.check_runs()
            if exp_run_id is None:
                self.active_run = mlflow.start_run(run_name=self.run_name)
            else:
                self.active_run = mlflow.start_run(run_id=exp_run_id)
        else:
            self.active_run = mlflow.start_run(run_name=self.get_run_name())

        logger.info(
            f"Run Name - Id: {self.active_run.info.run_name} - {self.active_run.info.run_id}"
        )

    @property
    def experiment(self) -> Experiment:
        return mlflow.get_experiment(self.experiment_id)

    def end(self) -> None:
        mlflow.end_run()

    def run_server(self) -> None:
        experiment = mlflow.get_experiment(self.experiment_id)
        backend_store_uri = Path(experiment.artifact_location).parent
        command = [
            "mlflow",
            "server",
            "--backend-store-uri",
            backend_store_uri,
            # "--default-artifact-root", "efault_artifact_root",
            # "--host", "127.0.0.1",
            # "--port", "5000"
        ]

        subprocess.run(command)
