from functools import cached_property
import os
from typing import Optional

import click
from ocrd_models import OcrdFileType
from ocrd import Processor
from ocrd.decorators import ocrd_cli_options, ocrd_cli_wrap_processor
from ocrd_utils import make_file_id

from .cli import process as cli_process

@click.command()
@ocrd_cli_options
def ocrd_dinglehopper(*args, **kwargs):
    return ocrd_cli_wrap_processor(OcrdDinglehopperEvaluate, *args, **kwargs)

class OcrdDinglehopperEvaluate(Processor):

    @cached_property
    def executable(self):
        return 'ocrd-dinglehopper'

    def process_page_file(self, *input_files: Optional[OcrdFileType]) -> None:

        assert self.parameter
        metrics = self.parameter["metrics"]
        textequiv_level = self.parameter["textequiv_level"]

        # wrong number of inputs: let fail
        gt_file, ocr_file = input_files
        # missing on either side: skip (zip_input_files already warned)
        if not gt_file or not ocr_file:
            return
        # missing download (i.e. OCRD_DOWNLOAD_INPUT=false):
        if not gt_file.local_filename:
            if config.OCRD_MISSING_INPUT == 'ABORT':
                raise MissingInputFile(gt_file.fileGrp, gt_file.pageId, gt_file.mimetype)
            return
        if not ocr_file.local_filename:
            if config.OCRD_MISSING_INPUT == 'ABORT':
                raise MissingInputFile(ocr_file.fileGrp, ocr_file.pageId, ocr_file.mimetype)
            return

        page_id = gt_file.pageId

        file_id = make_file_id(ocr_file, self.output_file_grp)
        cli_process(
            gt_file.local_filename,
            ocr_file.local_filename,
            file_id,
            self.output_file_grp,
            metrics=metrics,
            textequiv_level=textequiv_level,
        )

        # Add reports to the workspace
        for report_suffix, mimetype in [
            [".html", "text/html"],
            [".json", "application/json"],
        ]:
            self.workspace.add_file(
                file_id=file_id + report_suffix,
                file_grp=self.output_file_grp,
                page_id=page_id,
                mimetype=mimetype,
                local_filename=report_prefix + report_suffix,
            )


if __name__ == "__main__":
    ocrd_dinglehopper()
